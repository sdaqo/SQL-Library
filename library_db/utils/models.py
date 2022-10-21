from dataclasses import dataclass
from typing import Optional

@dataclass
class MediaItem:
    id: int
    title: str
    age_limit: int
    media_type: str 
    author: str

@dataclass
class User:
    id: int
    name: str
    surename: str
    email: str
    pwdhash: str
    user_type: str
    birthday: str

@dataclass
class Borrowing:
    id: int
    media_id: int
    user_id: int
    borrow_date: Optional[str]
    return_date: Optional[str]