from datetime import datetime
from fastapi import responses
from pydantic import BaseModel
from typing import List


class Website(BaseModel):
    id: int
    name: str
    url: str
    port: str
    protocol: str

    class Config:
        orm_mode = True

class Status(BaseModel):
    id: int
    timestamp: datetime
    online: bool
    response_code: str

    class Config:
        orm_mode = True

class WebAdmin(BaseModel):
    id: int
    name: str
    email_address: str
    sites: List[Website]

    class Config:
        orm_mode = True