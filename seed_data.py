"""
种子数据脚本 — 初始化测试数据
=============================================
用法：python seed_data.py

插入内容：
  - 1 个管理员账号 + 4 个普通用户
  - 4 个音乐分类
  - 3 个歌手 + 3 张专辑 + 4 首歌曲（引用 static/ 里已有的真实文件）
  - 若干收藏、点赞、评论、动态、关注数据

特点：幂等可重复执行，已存在的数据会自动跳过。
"""

import asyncio
import os
import sys

# 确保能 import app 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, engine
from app.utils.auth import hash_password
from app.models.user import User
from app.models.category import Category
from app.models.singer import Singer
from app.models.album import Album
from app.models.music import Music
from app.models.collection import Collection
from app.models.music_like import MusicLike
from app.models.follow import Follow
from app.models.comment import Comment
from app.models.post import Post


# ==================== 数据定义 ====================

USERS = [
    {"username": "admin", "password": "admin123", "nickname": "管理员", "role": "admin", "status": 1,
     "avatar": None, "signature": "平台管理员"},
    {"username": "zhangsan", "password": "123456", "nickname": "张三", "role": "user", "status": 1,
     "avatar": None, "signature": "爱听周杰伦"},
    {"username": "lisi", "password": "123456", "nickname": "李四", "role": "user", "status": 1,
     "avatar": None, "signature": "林俊杰铁粉"},
    {"username": "wangwu", "password": "123456", "nickname": "王五", "role": "user", "status": 1,
     "avatar": None, "signature": None},
    {"username": "zhaoliu", "password": "123456", "nickname": "赵六", "role": "user", "status": 0,  # 禁用状态，方便测试
     "avatar": None, "signature": None},
]

CATEGORIES = ["流行", "摇滚", "民谣", "R&B"]

SINGERS = [
    {"name": "周杰伦", "gender": 1, "avatar": None, "introduction": "华语流行音乐天王，代表作《晴天》《双截棍》等"},
    {"name": "林俊杰", "gender": 1, "avatar": None, "introduction": "新加坡华语流行歌手，代表作《江南》等"},
    {"name": "邓紫棋", "gender": 2, "avatar": None, "introduction": "中国香港流行歌手，代表作《光年之外》等"},
]

# 专辑：(名称, 歌手索引, 发行日期)
ALBUMS = [
    {"name": "范特西", "singer_idx": 0, "release_date": "2001-09-14"},
    {"name": "第二天堂", "singer_idx": 1, "release_date": "2004-06-04"},
    {"name": "新的心跳", "singer_idx": 2, "release_date": "2015-11-06"},
]

# 歌曲：(标题, 歌手索引, 专辑索引, 分类索引, 文件名, 封面名, 时长秒)
MUSICS = [
    {
        "title": "双截棍",
        "singer_idx": 0, "album_idx": 0, "category_idx": 0,
        "file_url": "/static/music/周杰伦  -  双截棍.mp3",
        "cover": "/static/images/双截棍.jpg",
        "duration": 219, "play_count": 1520, "status": 1,
    },
    {
        "title": "晴天",
        "singer_idx": 0, "album_idx": 0, "category_idx": 0,
        "file_url": "/static/music/周杰伦 -- 晴天.mp3",
        "cover": "/static/images/晴天.jpg",
        "duration": 269, "play_count": 3280, "status": 1,
    },
    {
        "title": "江南",
        "singer_idx": 1, "album_idx": 1, "category_idx": 0,
        "file_url": "/static/music/林俊杰 - 江南.mp3",
        "cover": "/static/images/江南.jpg",
        "duration": 250, "play_count": 2100, "status": 1,
    },
    {
        "title": "光年之外",
        "singer_idx": 2, "album_idx": 2, "category_idx": 0,
        "file_url": "/static/music/光年之外.mp3",
        "cover": "/static/images/光年之外.jpg",
        "duration": 235, "play_count": 4500, "status": 1,
    },
]

# 互动数据
COLLECTIONS = [
    {"user_idx": 1, "music_idx": 0},  # 张三收藏双截棍
    {"user_idx": 1, "music_idx": 1},  # 张三收藏晴天
    {"user_idx": 2, "music_idx": 2},  # 李四收藏江南
    {"user_idx": 2, "music_idx": 3},  # 李四收藏光年之外
]

LIKES = [
    {"user_idx": 1, "music_idx": 3},
    {"user_idx": 2, "music_idx": 3},
    {"user_idx": 3, "music_idx": 1},
]

FOLLOWS = [
    {"follower_idx": 1, "following_idx": 2},  # 张三关注李四
    {"follower_idx": 2, "following_idx": 1},  # 李四关注张三（互关）
    {"follower_idx": 3, "following_idx": 1},  # 王五关注张三
]

COMMENTS = [
    {"user_idx": 1, "music_idx": 1, "content": "青春的回忆，永远的晴天！"},
    {"user_idx": 2, "music_idx": 2, "content": "林俊杰的江南太好听了"},
    {"user_idx": 3, "music_idx": 3, "content": "光年之外循环了无数遍"},
]

POSTS = [
    {"user_idx": 1, "content": "今天听了周杰伦的晴天，回忆杀！", "images": None, "music_idx": 1, "status": 1},
    {"user_idx": 2, "content": "分享一首邓紫棋的光年之外，强烈推荐！", "images": None, "music_idx": 3, "status": 1},
    {"user_idx": 3, "content": "这条动态待审核测试", "images": None, "music_idx": None, "status": 0},  # 待审核
]


# ==================== 工具函数 ====================

async def get_or_create(db: AsyncSession, model, filters: dict, defaults: dict = None):
    """查询是否存在，不存在则创建。返回 (对象, 是否新建)。"""
    stmt = select(model)
    for key, value in filters.items():
        stmt = stmt.where(getattr(model, key) == value)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if obj:
        return obj, False
    data = {**filters}
    if defaults:
        data.update(defaults)
    obj = model(**data)
    db.add(obj)
    await db.flush()
    return obj, True


# ==================== 主逻辑 ====================

async def seed():
    async with AsyncSessionLocal() as db:
        try:
            # 1. 用户
            print("→ 插入用户...")
            user_ids = {}
            for u in USERS:
                obj, created = await get_or_create(
                    db, User,
                    filters={"username": u["username"]},
                    defaults={
                        "password": hash_password(u["password"]),
                        "nickname": u["nickname"],
                        "role": u["role"],
                        "status": u["status"],
                        "avatar": u["avatar"],
                        "signature": u["signature"],
                    },
                )
                user_ids[u["username"]] = obj.id
                action = "新建" if created else "已存在，跳过"
                print(f"   用户 {u['username']}（{u['nickname']}）— {action}")

            # 2. 分类
            print("→ 插入分类...")
            cat_ids = []
            for name in CATEGORIES:
                obj, created = await get_or_create(db, Category, filters={"name": name})
                cat_ids.append(obj.id)
                print(f"   分类「{name}」— {'新建' if created else '已存在，跳过'}")

            # 3. 歌手
            print("→ 插入歌手...")
            singer_ids = []
            for s in SINGERS:
                obj, created = await get_or_create(
                    db, Singer,
                    filters={"name": s["name"]},
                    defaults={"gender": s["gender"], "avatar": s["avatar"],
                              "introduction": s["introduction"]},
                )
                singer_ids.append(obj.id)
                print(f"   歌手「{s['name']}」— {'新建' if created else '已存在，跳过'}")

            # 4. 专辑
            print("→ 插入专辑...")
            album_ids = []
            for a in ALBUMS:
                obj, created = await get_or_create(
                    db, Album,
                    filters={"name": a["name"], "singer_id": singer_ids[a["singer_idx"]]},
                    defaults={"cover": None, "release_date": a["release_date"]},
                )
                album_ids.append(obj.id)
                print(f"   专辑「{a['name']}」— {'新建' if created else '已存在，跳过'}")

            # 5. 歌曲
            print("→ 插入歌曲...")
            music_ids = []
            for m in MUSICS:
                obj, created = await get_or_create(
                    db, Music,
                    filters={"title": m["title"], "singer_id": singer_ids[m["singer_idx"]]},
                    defaults={
                        "album_id": album_ids[m["album_idx"]],
                        "category_id": cat_ids[m["category_idx"]],
                        "file_url": m["file_url"],
                        "cover": m["cover"],
                        "duration": m["duration"],
                        "play_count": m["play_count"],
                        "status": m["status"],
                    },
                )
                music_ids.append(obj.id)
                print(f"   歌曲「{m['title']}」— {'新建' if created else '已存在，跳过'}")

            # 6. 收藏
            print("→ 插入收藏...")
            for c in COLLECTIONS:
                _, created = await get_or_create(
                    db, Collection,
                    filters={"user_id": user_ids[list(user_ids.keys())[c["user_idx"]]],
                             "music_id": music_ids[c["music_idx"]]},
                )
                if created:
                    print(f"   收藏 #{c['user_idx']} → 歌曲#{c['music_idx']}")

            # 7. 点赞
            print("→ 插入点赞...")
            for l in LIKES:
                _, created = await get_or_create(
                    db, MusicLike,
                    filters={"user_id": user_ids[list(user_ids.keys())[l["user_idx"]]],
                             "music_id": music_ids[l["music_idx"]]},
                )
                if created:
                    print(f"   点赞 #{l['user_idx']} → 歌曲#{l['music_idx']}")

            # 8. 关注
            print("→ 插入关注...")
            usernames = list(user_ids.keys())
            for f in FOLLOWS:
                _, created = await get_or_create(
                    db, Follow,
                    filters={"follower_id": user_ids[usernames[f["follower_idx"]]],
                             "following_id": user_ids[usernames[f["following_idx"]]]},
                )
                if created:
                    print(f"   {usernames[f['follower_idx']]} 关注了 {usernames[f['following_idx']]}")

            # 9. 评论
            print("→ 插入评论...")
            for c in COMMENTS:
                _, created = await get_or_create(
                    db, Comment,
                    filters={"user_id": user_ids[usernames[c["user_idx"]]],
                             "music_id": music_ids[c["music_idx"]],
                             "content": c["content"]},
                )
                if created:
                    print(f"   {usernames[c['user_idx']]} 评论了「{MUSICS[c['music_idx']]['title']}」")

            # 10. 动态
            print("→ 插入动态...")
            for p in POSTS:
                music_id = music_ids[p["music_idx"]] if p["music_idx"] is not None else None
                _, created = await get_or_create(
                    db, Post,
                    filters={"user_id": user_ids[usernames[p["user_idx"]]],
                             "content": p["content"]},
                    defaults={"images": p["images"], "music_id": music_id, "status": p["status"]},
                )
                if created:
                    print(f"   {usernames[p['user_idx']]} 发布动态（status={p['status']}）")

            await db.commit()
            print("\n✅ 种子数据插入完成！")
            print(f"   测试账号：")
            print(f"   管理员 — admin / admin123")
            print(f"   普通用户 — zhangsan / 123456")
            print(f"   普通用户 — lisi / 123456")
            print(f"   普通用户 — wangwu / 123456")
            print(f"   已禁用用户 — zhaoliu / 123456")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ 出错：{e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())
    # 正确关闭连接池，避免 "Event loop is closed" 警告
    asyncio.run(engine.dispose())
