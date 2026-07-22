from pydantic import BaseModel


class CollectionStatus(BaseModel):
    is_collected: bool

    class Config:
        from_attributes = True


class CollectionToggle(BaseModel):
    music_id: int

