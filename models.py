from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class Website(BaseModel):
    site_id: UUID
    protocol: Optional[str] = 'https'
    sub_domain: Optional[str] = 'www'
    host_name: str
    domain: str = 'gov.zm'
    port: Optional[int] = 443
    
    def url(self):
        return f'{self.protocol}://{self.sub_domain}.{self.host_name}.{self.domain}:{self.port}'
