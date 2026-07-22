from pydantic import BaseModel


class LikeStatus(BaseModel):
    is_liked: bool

    class Config:
        from_attributes = True


class LikeToggle(BaseModel):
    music_id: int

