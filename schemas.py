from datetime import datetime
from fastapi import responses
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

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

class DashboardItem(BaseModel):
    id: Optional[int]
    online: Optional[bool]
    response_code: Optional[str]
    timestamp: Optional[datetime]
    name: Optional[str]
    url: Optional[str]
    port: Optional[str]
    protocol: Optional[str]
    
    def set_values(self, website: WebsitePost, status: Status = None) -> None:
        '''
        Set the values or the variables based on the supplied website and status so we can push to web clients
        '''
        self.id = website.id
        self.online = status.online if status is not None else 'initializing'
        self.response_code = status.response_code if status is not None else 'initializing'
        self.timestamp = status.timestamp if status is not None else 'N/A'
        self.name = website.name
        self.url = website.url
        self.port = website.port
        self.protocol = website.protocol
    class Config:
        orm_mode = False

# Class containing enums for payload actions
class PayloadAction(Enum):
    REFRESH = 'refresh'
    UPDATE = 'update'
    DELETE = 'delete'
    CREATE = 'create'