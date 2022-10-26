from datetime import datetime, date
from typing import List, Optional

from fastapi import File
from pydantic import BaseModel

class Token(BaseModel):
 access_token: str
 token_type: str


class TokenData(BaseModel):
 email: Optional[str]


class UpdateArticleAll(BaseModel):
    title: str
    description: str
    text: str
    background_color: str
    text_color: str
    tags: List[int]


class UpdateUserAll(BaseModel):
    id: int
    login: str
    first_name: Optional[str]
    second_name: Optional[str]
    rating_users: int
    avatar: Optional[str]
    background_img: Optional[str]
    password: str
    username: str
    email: str
    date_of_birth: Optional[date]
    description: str
    last_activity: datetime
    is_admin: bool
    is_active: bool
    background_color: str
    text_color: str


class ArticleBasic(BaseModel):
    title: str
    authorship: List[int]


class Finder(BaseModel):
    title: Optional[str]
    min_rating: Optional[float]
    max_rating: Optional[float]
    authorship_add: Optional[List[int]]
    authorship_del: Optional[List[int]]
    tags_add: Optional[List[int]]
    tags_del: Optional[List[int]]


class UserBasic(BaseModel):
    """Модель, нужна при получении минимальной информации о пользователе,
         нужна при множественном поиске, создана для экономии памяти и интернета
         поля: id, username, avatar, background_img, rating"""

    id: int
    username: str
    avatar: Optional[str]
    background_img: Optional[str]
    text_color: Optional[str]
    rating: int


class TagBasic(BaseModel):
    """Модель, нужна при получении минимальной информации о теге,
         нужна при множественном поиске, создана для экономии памяти и интернета
         поля: id, title_rus, title_eng, text_color, background_color"""

    id: int
    title_rus: str
    title_eng: Optional[str]
    text_color: Optional[str]
    background_color: Optional[str]


class Article(BaseModel):
    """Модель, нужна при получении полной информации о статье,
         не рекомендуется использовать при множественном поиске
         поля: id, authorship, title, text, description, background_color, text_color, period_start, period_end,
         published, moderated, rating, views, date_added, tags"""
    id: int
    authorship: List[UserBasic]
    title: str
    text: Optional[str]
    description: Optional[str]
    background_color: Optional[str]
    background_img: Optional[str]
    text_color: Optional[str]
    period_start: Optional[date]
    period_end: Optional[date]
    published: bool
    moderated: bool
    rating: float
    likes: int
    views: int
    date_added: datetime
    tags: List[TagBasic]
    is_read: Optional[bool]


class Compilation(BaseModel):
    """Модель """
    id: int
    title: str
    description: Optional[str]
    public: bool
    articles: List[Article]


class UserComment(BaseModel):
    avatar: Optional[str]
    username: str


class Comment(BaseModel):
    id: int
    answer_id: int
    text: str
    date_added: datetime
    edited: bool
    author: UserComment
    likes: int
    article_id: int
    is_liked: bool


class UserStandard(BaseModel):
    id: int
    rating: int
    is_active: bool
    login: str
    is_admin: bool
    first_name: Optional[str]
    second_name: Optional[str]
    avatar: Optional[str]
    background_img: Optional[str]
    password: str
    username: str
    email: str
    description: Optional[str]
    date_added: datetime
    date_of_birth: Optional[date]
    last_activity: datetime


class UserAll(BaseModel):
    id: int
    rating: int
    is_active: bool
    login: str
    is_admin: bool
    first_name: Optional[str]
    second_name: Optional[str]
    avatar: Optional[str]
    background_img: Optional[str]
    password: str
    username: str
    email: str
    description: str
    date_added: datetime
    date_of_birth: Optional[date]
    last_activity: datetime
    authorship: List[Article]
    read: List[Article]
    viewed: List[Article]
    comments: List[Comment]
    comments_liked: List[Comment]
    compilations: List[Compilation]


class UserAuthor(BaseModel):
    id: int
    rating: int
    is_active: bool
    is_admin: bool
    first_name: Optional[str]
    second_name: Optional[str]
    avatar: Optional[str]
    background_img: Optional[str]
    username: str
    email: str
    description: Optional[str]
    date_added: datetime
    date_of_birth: Optional[date]
    last_activity: datetime
    authorship: List[Article]


class TagBase(BaseModel):
    id: int
    title_rus: str
    title_eng: Optional[str]
    text_color: Optional[str]
    background_color: Optional[str]
    description_rus: str
    description_eng: Optional[str]
    articles: List[Article]


class TagUpdate(BaseModel):
    pass


class TagGet(BaseModel):
    id: int
    title_rus: str
    description_rus: str
    description_eng: str
    text_color: str
    background_color: str
    title_eng: str
    background_color: str


class TagCreate(BaseModel):
    title_rus: str
    description_rus: str
    text_color: str
    background_color: str


class TagModel(TagBase):
    id: int


class UserGet(BaseModel):
    id: int
    login: str
    avatar: Optional[str]


class CommentBase(BaseModel):
    answer_id: int
    text: str
    date_added: datetime
    deleted: bool = False
    edited: bool = False
    user_id: int
    likes: List[UserGet]
    article_id: int


class CommentCreate(BaseModel):
    article_id: int
    answer_id: int
    text: str
    user_id: int


class CommentGet(BaseModel):
    id: int
    answer_id: int
    text: str
    date_added: datetime
    deleted: bool = False
    edited: bool = False
    authors: List[UserGet]
    likes: int
    is_liked: bool
    article_id: int


class CommentUpdate(BaseModel):
    text: str
    edited: Optional[bool] = True


class CommentModel(CommentBase):
    id: int


class CompilationsGet(BaseModel):
    id: int
    title: str
    saved: bool


class ArticleBase(BaseModel):
    title: str
    description: str
    text_color: str
    background_color: str
    background_img: Optional[str]
    description: Optional[str]
    text: str
    period_start: date
    period_end: date
    date_added: datetime
    published: bool
    moderated: bool
    deleted: bool = False
    authorship: List[UserGet]
    readers: List[UserGet]
    views: List[UserGet]
    rating: float
    user_rating: Optional[int]
    is_read_by_user: Optional[int]

    comments: List[CommentGet]
    tags: List[TagGet]


class ArticleCreate(BaseModel):
    authorship: List[int]
    title: str
    text: str
    date_added: datetime
    tags: List[int]
    period_start: date


class ArticleGet(BaseModel):
    authorship: List[UserGet]
    title: str
    text: str
    rating: float
    date_added: datetime
    tags: List[TagGet]
    is_read_by_user: Optional[bool]
    rating_by_user: Optional[int]


class ArticleUpdate(BaseModel):
    pass


class ArticleModel(ArticleBase):
    id: int


class CompilationsBase(BaseModel):
    title: str
    description: str
    public: bool
    deleted: bool = False
    user_id: int
    articles: List[ArticleGet]


class CompilationsCreate(BaseModel):
    title: str
    public: bool = True
    user_id: int
    description: Optional[str]


class CompilationsUpdate(BaseModel):
    pass


class CompilationsModel(CompilationsBase):
    id: int


class UserCreate(BaseModel):
    login: str
    username: str
    password: str
    date_of_birth: Optional[date]
    email: str


class UserUpdate(BaseModel):
    username: str
    text_color: str
    background_color: str
    background_img: Optional[str]
    avatar: Optional[str]
    description: str
    date_of_birth: Optional[date]
    first_name: Optional[str]
    second_name: Optional[str]
