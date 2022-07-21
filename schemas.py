from uuid import UUID

from pydantic import BaseModel


class ThingBase(BaseModel):
    number: int
    name: str
    owner_id: UUID


class ThingCreate(ThingBase):
    pass


class Thing(ThingBase):
    id: int

    class Config:
        orm_mode = True


class Sleep(BaseModel):
    id: UUID
    things: list[Thing]

    class Config:
        orm_mode = True
