import uvicorn
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, Header, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker, Session

import crud
from DB_tables import *
from models_api import *

engine = create_engine('sqlite:///scipher.db', echo=False, connect_args={'check_same_thread': False})
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def get_user(db, email: str):
    user = crud.get_user_by_email(db, email)
    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(db, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    # if not verify_password(password, user.password):
    if not password == user.password:
        return False
    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), from_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, from_data.username, from_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/user/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user


@app.patch('/article/{article_id}/all')
def update_article(article_id: int, article: UpdateArticleAll, user=Depends(get_current_user),
                   db: Session = Depends(get_db)):
    if crud.get_article_by_id(db, article_id) in user.authorship:
        return crud.update_article_all(db, article=article, article_id=article_id)


@app.post('/img/user/avatar')
def patch_img_user_avatar(file: bytes = File(...), user=Depends(get_current_user),
                          db: Session = Depends(get_db)):
    """
    Функция, которая добавляет аватарку пользователю

    """
    return crud.update_user_avatar(db=db, user_id=user.id, file=file)


@app.post('/img/user/back')
def patch_img_user_back(file: bytes = File(...), user=Depends(get_current_user),
                        db: Session = Depends(get_db)):
    return crud.update_user_background_img(db=db, user_id=user.id, file=file)


@app.post('/img/article/{article_id}/back')
def patch_img_article(article_id: int, file: bytes = File(...), user=Depends(get_current_user),
                      db: Session = Depends(get_db)):
    return crud.update_article_background_img(db=db, article_id=article_id, file=file)


@app.get('/img/avatar/user/{user_id}')
def get_img_avatar(user_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    with open(f'static/user{user_id}_avatar.jpg', "rb") as imageFile:
        str = base64.b64encode(imageFile.read())
        return str


@app.get('/img/back/user/{user_id}')
def get_img_avatar(user_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    with open(f'static/user{user_id}_back.jpg', "rb") as imageFile:
        str = base64.b64encode(imageFile.read())
        return str


@app.get('/img/back/article/{article_id}')
def get_img_avatar(article_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    with open(f'static/article{article_id}_back.jpg', "rb") as imageFile:
        str = base64.b64encode(imageFile.read())
        return str


@app.post('/article/basic')
def post_basic_article(article: ArticleBasic, db: Session = Depends(get_db)):
    return crud.create_basic_article(db=db, article=article)


@app.post("/finder", response_model=List[Article])
def smart_finder(finder: Finder, db: Session = Depends(get_db)):
    return crud.smart_finder(db=db, finder=finder)


@app.get("/users", response_model=List[UserBasic])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить все данные всех пользователей в промежудке

    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[UserBasic]:
    """
    return crud.get_users(db=db, skip=skip, limit=limit)


@app.get("/users/best", response_model=List[UserBasic])
def get_best_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить все данные всех пользователей в промежудке, отсортированых по репутации

    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[UserBasic]:
    """
    return crud.get_best_users(db=db, skip=skip, limit=limit)


@app.get("/user/{user_id}/all", response_model=UserAll)
def get_user_by_id(user_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Функция, которая позволляет получить все данные о пользователе по его id

    :param user_id: int - id пользователя
    :param db: Session - база данных
    :return UserAll:
    """
    return crud.get_user_by_id(db=db, user_id=user.id)


@app.get("/user/{email}/email")
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """
    Функция, которая проверяет есть ли пользователь с этой почтой

    :param email: str - id пользователя
    :param db: Session - база данных
    :return UserAll:
    """
    return crud.is_user_with_email(db=db, email=email)


@app.get("/user/{user_id}/standard", response_model=UserStandard)
def get_user_standard_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Функция, которая позволляет получить информацию о пользователе по его id

    :param user_id: int - id пользователя
    :param db: Session - база данных
    :return UserStandard:
    """
    return crud.get_user_standard_by_id(db=db, user_id=user_id)


@app.get("/user/{user_id}/basic", response_model=UserBasic)
def get_user_basic_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Функция, которая позволляет получить минимальную информацию о пользователе по его id

    :param user_id: int - id пользователя
    :param db: Session - база данных
    :return UserBasic:
    """
    return crud.get_user_basic_by_id(db=db, user_id=user_id)


@app.get("/user/{user_id}/author", response_model=UserAuthor)
def get_user_author_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Функция, которая позволляет получить информацию пользователя как автора по его id

    :param user:
    :param user_id: int - id пользователя
    :param db: Session - база данных
    :return UserAuthor:
    """
    return crud.get_user_author_by_id(db=db, user_id=user_id)


@app.get("/user/{user_id}/authorship", response_model=List[Article])
def get_authorship_by_user_id(user_id: int, skip: int = 0, limit: int = 10,
                              db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные о всех статьях пользователя в промежудке

    :param user_id: int - id пользователя
    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Article]:
    """
    return crud.get_authorship_by_user_id(db=db, user_id=user_id, skip=skip, limit=limit)


@app.get("/user/{user_id}/read", response_model=List[Article])
def get_read_articles_by_user_id(user_id: int,user=Depends(get_current_user), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные о прочитанных статьях пользователя в промежудке

    :param user_id: int - id пользователя
    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Article]:
    """
    return crud.get_read_articles_by_user_id(db=db, user_id=user.id, skip=skip, limit=limit)


@app.get("/user/{user_id}/view", response_model=List[Article])
def get_view_articles_by_user_id(user_id: int,user=Depends(get_current_user), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные о открытых статьях пользователя в промежудке

    :param user_id: int - id пользователя
    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Article]:
    """
    return crud.get_view_articles_by_user_id(db=db, user_id=user.id, skip=skip, limit=limit)


@app.get("/user/{user_id}/comments", response_model=List[Comment])
def get_comments_by_user_id(user_id: int,user=Depends(get_current_user), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные о всех комментариях пользователя в промежудке

    :param user_id: int - id пользователя
    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Comment]:
    """
    return crud.get_comments_by_user_id(db=db, user_id=user.id, skip=skip, limit=limit)


@app.get("/user/{user_id}/compilation", response_model=List[Compilation])
def get_compilations_by_user_id(user_id: int,user=Depends(get_current_user), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные о всех сборниках пользователя в промежудке

    :param user_id: int - id пользователя
    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Compilation]:
    """
    return crud.get_compilations_by_user_id(db=db, user_id=user.id, skip=skip, limit=limit)


@app.get("/article/{article_id}/comments/{user_id}", response_model=List[Comment])
def get_comments_by_article_id(article_id: int, user_id: int, skip: int = 0, limit: int = 10,
                               db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные о всех комментариях статьи в промежудке

    :param article_id: int - id статьи
    :param user_id: int - id пользователя
    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Comment]:
    """
    return crud.get_comments_by_article_id(db=db, article_id=article_id, user_id=user_id, skip=skip, limit=limit)


@app.get('/tag/{tag_id}/articles')
def get_popular_articles_by_tag(tag_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Позволяет получить самые популярные статьи с этим тегом
    :param limit:
    :param skip:
    :param tag_id:
    :param db:
    :return:
    """
    return crud.get_popular_articles_by_tag(db=db, tag_id=tag_id, skip=skip, limit=limit)


@app.get("/user/{user_id}/comments_likes", response_model=List[Comment])
def get_favorite_comments_by_user_id(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные о всех любимых комментариях пользователя в промежудке

    :param user_id: int - id пользователя
    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Comment]:
    """
    return crud.get_favorite_comments_by_user_id(db=db, user_id=user_id, skip=skip, limit=limit)


@app.get("/articles", response_model=List[Article])
def get_articles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные всех статьях в промежудке

    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Article]:
    """
    return crud.get_articles(db=db, skip=skip, limit=limit)


@app.get('/login/{email}/{password}', response_model=UserBasic)
def login(email: str, password: str, db: Session = Depends(get_db)):
    """
    Функция, которая проверяет логин и пароль
    :param email:
    :param password:
    :param db:
    :return:
    """
    return crud.login(db=db, email=email, password=password)


@app.patch('/logout')
def logout(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Функция, которая проверяет логин и пароль
    :param user:
    :param db:
    :return:
    """
    return crud.logout(db=db, user_id=user.id)


@app.get("/articles/last", response_model=List[Article])
def get_last_articles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные всех статьях в промежудке отсортированых по новизне

    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Article]:
    """
    return crud.get_last_articles(db=db, skip=skip, limit=limit)


@app.get("/articles/popular", response_model=List[Article])
def get_popular_articles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные всех статьях в промежудке отсортированых по популярности за неделю

    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[Article]:
    """
    return crud.get_popular_articles(db=db, skip=skip, limit=limit)


@app.get("/article/{article_id}/user/{user_id}")
def get_article(article_id: int, user_id, db: Session = Depends(get_db)):
    """
     Функция, которая позволляет получить все данные о статье по её id

    :param article_id: int - id статьи
    :param db: Session - база данных
    :return Article:
    """
    return crud.get_article_by_id(db=db, article_id=article_id, user_id=user_id)


@app.get("/articles/{title}/search", response_model=List[Article])
def get_articles_by_title(title: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
     Функция, которая позволляет получить все данные о статье по её названию

    :param limit:
    :param skip:
    :param article_title:
    :param db: Session - база данных
    :return Article:
    """
    return crud.get_articles_by_title(db=db, title=title, skip=skip, limit=limit)


@app.get('/tags/{title}/search', response_model=List[TagModel])
def get_tags_by_title(title: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить все данные тега по его id

    :param title: заголовок тега
    :param db: Session - база данных
    :return List[TagModel]:
    """
    return crud.get_tags_by_title(db=db, title=title, skip=skip, limit=limit)


@app.get("/users/{username}/search", response_model=List[UserBasic])
def get_user_by_username(username: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволляет получить все данные о пользователе по его имени

    :param limit:
    :param skip:
    :param username: имя пользователя
    :param db: Session - база данных
    :return List[UserBasic]:
    """
    return crud.get_users_by_username(db=db, username=username, skip=skip, limit=limit)


@app.get('/tags/popular', response_model=List[TagBasic])
def get_popular_tags(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Функция, которая позволяет получить данные всех тегах в промежудке, отсортированых по популярности

    :param skip: int - начало промежудка
    :param limit: int - конец промежудка
    :param db: Session - база данных
    :return List[TagBasic]:
    """
    return crud.get_popular_tags(db=db, skip=skip, limit=limit)


@app.post("/user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Функция, которая позвляет добавить нового пользователя

    :param user: UserCreate - данные пользователя
    :param db: Session - база данных
    :return:
    """
    return crud.create_user(db=db, user=user)


@app.patch("/authorship/{user_id}/{article_id}")
def create_authorship(user_id: int, article_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Функция, которая позволяет добавить автора к статье

    :param user_id: int - id пользователя
    :param article_id: int - id статьи
    :param db: Session - база данных
    :return:
    """
    return crud.create_authorship(db=db, user_id=user.id, article_id=article_id)


@app.patch("/read/{user_id}/{article_id}")
def create_read_of_article(user_id: int, article_id: int, user=Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """
    Функция, которая позволяет добавить статью в прочитанное

    :param user_id: int - id пользователя
    :param article_id: int - id статьи
    :param db: Session - база данных
    :return:
    """
    return crud.create_read_of_article(db=db, user_id=user.id, article_id=article_id)


@app.patch("/view/{user_id}/{article_id}")
def create_view_of_article(user_id: int, article_id: int, user=Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """
    Функция, которая позволяет добавить статью в читаемое

    :param user_id: int - id пользователя
    :param article_id: int - id статьи
    :param db: Session - база данных
    :return:
    """
    return crud.create_view_of_article(db=db, user_id=user.id, article_id=article_id)


@app.patch('/article/{article_id}/is_publish/')
def is_published(article_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.update_article_is_published(db=db, article_id=article_id)


@app.patch("/like/{user_id}/comment/{comment_id}")
def update_like_of_comment(user_id: int, comment_id: int, user=Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """
    Функция, которая позволяет добавить в комментарий в избранные

    :param user_id: int - id пользователя
    :param comment_id: int - id комментария
    :param db: Session - база данных
    :return:
    """
    return crud.create_like_of_comment(db=db, user_id=user.id, comment_id=comment_id)


@app.patch("/rating/{user_id}/article/{article_id}")
def update_rating_of_article(user_id: int, article_id: int, rating: int, user=Depends(get_current_user),db: Session = Depends(get_db)):
    """
    Функция, которая позволяет оценить статью

    :param article_id: int - id статьи
    :param user_id: int - id пользователя
    :param rating: int - rating статьи
    :param db: Session - база данных
    :return:
    """
    return crud.create_rating_article(db=db, user_id=user.id, article_id=article_id, rating=rating)


@app.post("/comment")
def create_comment(comment: CommentCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Функция, которая позволяет создать новый комментарий

    :param comment: CommentCreate - данные комментария
    :param db: Session - база данных
    :return:
    """
    return crud.create_comment(db=db, comment=comment)


@app.post("/article")
def create_article(article: ArticleCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Функция, которая позволяет создать новую статью

    :param article: ArticleCreate - данные статьи
    :param db: Session - база данных
    :return:
    """
    return crud.create_article(db=db, article=article)


@app.post("/tag")
def create_tag(tag: TagCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Функция, которая позволяет создать новый тег

    :param tag: TegCreate - данные тега
    :param db: Session - база данных
    :return:
    """

    return crud.create_tag(db=db, tag=tag)


@app.post("/compilation")
def create_compilation(compilation: CompilationsCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Функция, которая позволяет создать новый сборник

    :param compilation:
    :param db:
    :return:
    """
    return crud.create_compilation(db, compilation)


@app.patch('/users/{user_id}/info')
def update_user_info(user_id: int, info: UserUpdate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Функция, которая позволяет изменить данные пользователя

    :param user_id: int - id пользователя
    :param info: UserUpdate - новые данные пользователя
    :param db: Session - база данных
    :return:
    """

    return crud.update_user_info(db=db, user_id=user.id, new_info=info)


# @app.patch('/moderate/article/{article_id}')
# def moderate_article(article_id: int, db: Session = Depends(get_db)):
#     return crud.moderate_article(db=db, article_id=article_id)


@app.patch('/delete/article/{article_id}')
def delete_article(article_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    crud.delete_article(db=db, article_id=article_id)


@app.get('/compilations/{user_id}/article/{article_id}', response_model=List[CompilationsGet])
def is_in_compilation(user_id: int, article_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.article_compilations(db=db, user_id=user.id, article_id=article_id)


@app.patch('/compilation/{compilation_id}/article/{article_id}')
def put_article_in_compilation(compilation_id: int, article_id: int, user=Depends(get_current_user),
                               db: Session = Depends(get_db)):
    """
    Функция, которая позволяет добавить статью в сборник

    :param article_id:
    :param compilation_id:
    :param db: Session - база данных
    :return:
    """

    return crud.put_article_in_compilation(db=db, compilation_id=compilation_id, article_id=article_id)


@app.patch('/comment/{comment_id}/text')
def update_comment_text(comment_id: int, info: CommentUpdate, user=Depends(get_current_user),
                        db: Session = Depends(get_db)):
    """
    Функция, которая позволяет поменять текст комментария

    :param comment_id: int - id комментария
    :param info: CommentUpdate - новый текст пользователя
    :param db: Session - база данных
    :return:
    """
    return crud.update_comment_text(db=db, comment_id=comment_id, text=info.text, is_edited=info.edited)


@app.patch('/user/{user_id}/delete')
def delete_user(user_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Функция, которая позволяет удалить пользователя

    :param user_id: int - id пользователя
    :param db: Session - база данных
    :return:
    """

    return crud.delete_user(db=db, user_id=user.id)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=7000)
