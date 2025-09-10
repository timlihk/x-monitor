from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any

class MonitoredTermBase(BaseModel):
    keyword: str
    restrict_following: bool = False
    active: bool = True

class MonitoredTermCreate(MonitoredTermBase):
    pass

class MonitoredTermUpdate(BaseModel):
    keyword: Optional[str] = None
    restrict_following: Optional[bool] = None
    active: Optional[bool] = None

class MonitoredTerm(MonitoredTermBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ResultBase(BaseModel):
    tweets_raw: Any
    summary: str

class ResultCreate(ResultBase):
    keyword_id: int

class Result(ResultBase):
    id: int
    keyword_id: int
    created_at: datetime
    monitored_term: Optional[MonitoredTerm] = None

    class Config:
        from_attributes = True

class TweetSummaryRequest(BaseModel):
    keyword: str
    restrict_following: bool = False

class TweetSummaryResponse(BaseModel):
    summary: str
    tweet_count: int
    keyword: str