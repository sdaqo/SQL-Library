from dataclasses import dataclass
from typing import Optional


@dataclass
class MediaItem:
    id: Optional[int]
    title: str
    age_limit: int
    media_type: str
    author: str
    isbn: Optional[int]


@dataclass
class User:
    id: Optional[int]
    name: str
    surename: str
    email: str
    pwdhash: str
    user_type: str
    birthday: str


@dataclass
class Borrowing:
    id: Optional[int]
    media_id: int
    user_id: int
    borrow_date: Optional[str]
    return_date: Optional[str]


@dataclass
class Author:
    id: Optional[int]
    name: str
