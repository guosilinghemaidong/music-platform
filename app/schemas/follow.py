from pydantic import BaseModel


class FollowStatus(BaseModel):
    is_followed: bool

    class Config:
        from_attributes = True


class FollowToggle(BaseModel):
    following_id: int

