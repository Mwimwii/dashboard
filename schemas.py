from datetime import datetime
from fastapi import responses
from pydantic import BaseModel
from typing import List, Optional

# Default class for websites used for API's serialisation and Request validation
class Website(BaseModel):
    id: Optional[int]

    class Config:
        orm_mode = True

# validate patch requests
class WebsitePatch(Website):
    name: Optional[str]
    url: Optional[str]
    port: Optional[str]
    protocol: Optional[str]

# validate Post requests
class WebsitePost(Website):
    name: str
    url: str
    port: str
    protocol: str


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

class DashboardItem(WebsitePost):
    online: bool
    response_code: str
    # TODO: timestamp?
    class Config:
        orm_mode = False