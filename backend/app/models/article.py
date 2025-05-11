from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl

class Article(BaseModel):
    title: str
    text: str
    url: HttpUrl
    date_published: Optional[datetime] = None
    source: str = "Reuters"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 