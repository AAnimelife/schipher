import base64
import datetime
import operator
import random
import re
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import File
from smtplib import SMTP
from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from DB_tables import *
from models_api import *


def send_code(email):
    msg = MIMEMultipart()
    check = random.randint(100000, 999999)  # подтверждение почты и создание пароля

    message = f'''<table style="width:100%;margin-top:46px;border-top:2px solid 
    #2086E0;background:#fff;box-shadow:0px 0px 2px #ddd;text-align:center;"> <tbody> <tr> <td 
    style="font-size:20px;font-weight:400;padding-top:120px;color:#303030;">Confirmation code</td> </tr> <tr> <td 
    style="font-size:36px;font-weight:800;color: #178BFE;">{check}</td> </tr> <tr> <td 
                    style="font-size:16px;font-weight:200;padding-top:30px;color: #303030;"> Чтобы подтвердить аккаунт введите этот код на сайтt: </td> </tr> <tr> <td style="font-size:16px;font-weight:400;color: 
                    #303030;padding-bottom:108px;border-bottom:1px solid #eee;"> <a href="/compose?To={email}">
{email}</a> 
                    </td>
                </tr>
                </tbody>
            </table>'''

    msg.attach(MIMEText(message, 'html'))
    msg["Subject"] = "[Scipher] Код подтверждения"
    server = SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login("socialpostchat@gmail.com", "8t%EzRUP")
    server.sendmail("socialpostchat@gmail.com", email, msg.as_string())
    server.quit()
    return check


def get_img(travel: str):
    if travel and travel[-4::] == '.jpg':
        with open(travel, "rb") as imageFile:
            str = base64.b64encode(imageFile.read())
            return str
    return None


def make_array(arr: list, func):
    """Функция, которая возвращает массив результатов работы функции с каждым объектом массива
    :param arr: массив объектов
    :param func: функция
    :return:
    """

    new = []
    for i in arr:
        if i:
            new.append(func(i))
    return new


def make_comment_array(arr: list, user_id: int, db: Session, func):
    """Функция, которая возвращает массив результатов работы функции с каждым объектом массива
    :param arr: массив объектов
    :param db: сессия БД
    :param func: функция
    :return:
    """

    new = []
    for comment in arr:
        if comment:
            user = db.query(Users).filter(Users.id == comment.user_id).first()
            new.append(func(comment, user, user_id))
    return new


def convert_to_all_tag(tag: Tags):
    """
        Функция, которая возвращает объект класса Tags согласно модели TagAll
        :param tag: - объект класса Tags
        :return:
        """
    if str(type(tag)) == """<class 'NoneType'>""":
        return None
    arr = make_array(tag.tags, convert_to_basic_article)
    arr = list(map(dict, arr))
    arr.sort(key=operator.itemgetter('likes'), reverse=True)
    new = TagBase(id=tag.id,
                  title_rus=tag.title_rus,
                  title_eng=tag.title_eng,
                  text_color=tag.text_color,
                  background_color=tag.background_color,
                  description_rus=tag.description_rus,
                  description_eng=tag.description_eng,
                  articles=arr[0:10]
                  )
    return new


def convert_to_basic_tag(tag: Tags):
    """
    Функция, которая возвращает объект класса Tags согласно модели TagBasic
    :param tag: - объект класса Tags
    :return:
    """
    if str(type(tag)) == """<class 'NoneType'>""":
        return None
    new = TagBasic(id=tag.id,
                   title_rus=tag.title_rus,
                   title_eng=tag.title_eng,
                   text_color=tag.text_color,
                   background_color=tag.background_color)
    return new


def convert_to_basic_article(article: Articles):
    """
        Функция, которая возвращает объект класса Article согласно модели TagBasic
        :param article: - объект класса Tags
        :return:
        """
    if str(type(article)) == """<class 'NoneType'>""":
        return None
    new = Article(id=article.id,
                  authorship=make_array(article.authorship, convert_to_basic_user),
                  title=article.title,
                  description=article.description,
                  background_color=article.background_color,
                  background_img=get_img(article.background_img),
                  text_color=article.text_color,
                  period_start=article.period_start,
                  period_end=article.period_end,
                  published=article.is_published,
                  moderated=article.is_moderated,
                  likes=len(article.likes),
                  rating=article.rating,
                  views=len(article.views_article),
                  date_added=article.date_added,
                  text=article.text,
                  tags=make_array(article.tags, convert_to_basic_tag))
    return new


def convert_to_compilation(compilation: Compilations):
    if str(type(compilation)) == """<class 'NoneType'>""":
        return None
    new = Compilation(id=compilation.id,
                      title=compilation.title,
                      description=compilation.description,
                      public=compilation.is_public,
                      articles=make_array(compilation.compilations, convert_to_basic_article))
    return new


def convert_to_basic_user(user: Users):
    if str(type(user)) == """<class 'NoneType'>""":
        return None
    new = UserBasic(id=user.id,
                    username=user.username,
                    text_color=user.text_color,
                    avatar=get_img(user.avatar),
                    background_img=get_img(user.background_img),
                    rating=user.rating_users)
    return new


def convert_to_standard_user(user: Users):
    if str(type(user)) == """<class 'NoneType'>""":
        return None
    new = UserStandard(id=user.id,
                       rating=user.rating_users,
                       is_active=user.is_active,
                       login=user.login,
                       is_admin=user.is_admin,
                       first_name=user.first_name,
                       second_name=user.second_name,
                       avatar=get_img(user.avatar),
                       background_img=get_img(user.background_img),
                       password=user.password,
                       username=user.username,
                       email=user.email,
                       description=user.description,
                       date_added=str(user.date_added),
                       date_of_birth=str(user.date_of_birth),
                       last_activity=str(user.last_activity)
                       )
    return new


def convert_to_all_user(db: Session, user: Users):
    if str(type(user)) == """<class 'NoneType'>""":
        return None
    new = UserAll(id=user.id,
                  rating=user.rating_users,
                  is_active=user.is_active,
                  login=user.login,
                  is_admin=user.is_admin,
                  first_name=user.first_name,
                  second_name=user.second_name,
                  avatar=get_img(user.avatar),
                  background_img=get_img(user.background_img),
                  password=user.password,
                  username=user.username,
                  email=user.email,
                  description=user.description,
                  date_added=user.date_added,
                  date_of_birth=user.date_of_birth,
                  last_activity=user.last_activity,
                  authorship=make_array(user.authorship, convert_to_basic_article),
                  read=make_array(user.read, convert_to_basic_article),
                  viewed=make_array(user.viewed_article, convert_to_basic_article),
                  comments=make_comment_array(user.user_comments, user.id, db, convert_to_comment),
                  comments_liked=make_comment_array(user.comment_likes, user.id, db, convert_to_comment),
                  compilations=make_array(user.user_compilations, convert_to_compilation)
                  )
    return new


def convert_to_author(db: Session, user: Users):
    if str(type(user)) == """<class 'NoneType'>""":
        return None
    new = UserAuthor(id=user.id,
                     rating=user.rating_users,
                     is_active=user.is_active,
                     is_admin=user.is_admin,
                     first_name=user.first_name,
                     second_name=user.second_name,
                     avatar=get_img(user.avatar),
                     background_img=get_img(user.background_img),
                     password=user.password,
                     username=user.username,
                     email=user.email,
                     description=user.description,
                     date_added=user.date_added,
                     date_of_birth=user.date_of_birth,
                     last_activity=user.last_activity,
                     authorship=make_array(user.authorship, convert_to_basic_article),
                     comments=make_comment_array(user.user_comments, user.id, db, convert_to_comment)
                     )
    return new


def create_basic_article(db: Session, article: ArticleBasic):
    time = datetime.now()
    db_user_article = Articles(title=article.title,
                               date_added=time,
                               is_published=False)
    for author in article.authorship:
        if get_user(db, author):
            db_user_article.authorship.append(get_user(db, author))
    db.add(db_user_article)
    db.commit()
    db.refresh(db_user_article)
    return db_user_article


def create_like_of_article(db: Session, user_id: int, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.likes.append(get_user(db, user_id))
    db.commit()
    return 1


def get_user_by_id(db: Session, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).filter(Users.is_deleted == 0).first()
    return convert_to_all_user(user, db)


def get_user_standard_by_id(db: Session, user_id):
    user = db.query(Users).filter(Users.id == user_id).filter(Users.is_deleted == 0).first()
    return convert_to_standard_user(user)


def get_user_basic_by_id(db: Session, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).filter(Users.is_deleted == 0).first()
    return convert_to_basic_user(user)


def get_user_author_by_id(db: Session, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).filter(Users.is_deleted == 0).first()
    return convert_to_author(db, user)


def get_article_title(db: Session, article_id: int):
    return db.query(Articles).filter(Articles.id == article_id).filter(Articles.is_deleted == 0).first().title


def convert_to_comment(comment: Comments, user: Users, user_id: int):
    user_ids = [user.id for user in comment.likes]
    is_liked = user_id in user_ids

    author = UserComment(id=user.id,
                         username=user.username,
                         avatar=get_img(user.avatar))

    new = Comment(id=comment.id,
                  answer_id=comment.answer_id,
                  text=comment.text,
                  date_added=comment.date_added,
                  edited=comment.is_edited,
                  user_id=comment.user_id,
                  likes=len(comment.likes),
                  article_id=comment.article_id,
                  author=author,
                  is_liked=is_liked)

    return new


def get_users(db: Session, skip: int = 0, limit: int = 100):
    arr = db.query(Users).filter(Users.is_deleted == 0).offset(skip).limit(limit).all()
    return make_array(arr, convert_to_basic_user)


def get_best_users(db: Session, skip: int = 0, limit: int = 100):
    arr = db.query(Users).filter(Users.is_deleted == 0).order_by(-Users.rating_users).offset(skip).limit(limit).all()
    return make_array(arr, convert_to_basic_user)


def create_user(db: Session, user: UserCreate):
    time = datetime.now()
    db_user = Users(email=user.email,
                    login=user.login,
                    password=user.password,
                    username=user.username,
                    date_added=time,
                    date_of_birth=user.date_of_birth,
                    last_activity=time,
                    is_active=False)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    with open("static/avatar.png", "rb") as f:
        avatar = f.read()
    update_user_avatar(db=db, user_id=db_user.id, file=avatar)
    db.commit()
    return db_user


def update_user_info(db: Session, user_id: int, new_info: UserUpdate):
    current_data = db.query(Users).filter(Users.id == user_id).first()
    current_data.date_of_birth = new_info.date_of_birth
    current_data.description = new_info.description
    current_data.first_name = new_info.first_name
    current_data.second_name = new_info.second_name
    current_data.username = new_info.username
    current_data.text_color = new_info.text_color
    current_data.background_color = new_info.background_color
    db.commit()
    return current_data


def update_user_email(db: Session, email: str, user_id: int):
    current_data = db.query(Users).filter(Users.id == user_id).first()
    current_data.email = email
    db.commit()
    return current_data


def update_user_password(db: Session, password: str, user_id: int):
    current_data = db.query(Users).filter(Users.id == user_id).first()
    current_data.password = password
    db.commit()
    return current_data


def update_user_first_name(db: Session, first_name: str, user_id: int):
    current_data = db.query(Users).filter(Users.id == user_id).first()
    current_data.first_name = first_name
    db.commit()
    return current_data


def update_user_second_name(db: Session, second_name: str, user_id: int):
    current_data = db.query(Users).filter(Users.id == user_id).first()
    current_data.second_name = second_name
    db.commit()
    return current_data


def update_user_description(db: Session, description: str, user_id: int):
    current_data = db.query(Users).filter(Users.id == user_id).first()
    current_data.description = description
    db.commit()
    return current_data


def update_user_last_activity(db: Session, last_activity: Date, user_id: int):
    current_data = db.query(Users).filter(Users.id == user_id).first()
    current_data.last_activity = last_activity
    db.commit()
    return current_data


def update_user_is_active(db: Session, is_active: bool, user_id: int):
    current_data = db.query(Users).filter(Users.id == user_id).first()
    current_data.is_active = is_active
    db.commit()
    return current_data


def delete_user(db: Session, user_id: int):
    current_data = db.query(Users).filter(Users.id == user_id).first()
    current_data.is_deleted = True
    db.commit()
    return current_data


def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comments).filter(Comments.id == comment_id).first()


def get_comments_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 0):
    arr = db.query(Comments).filter(Comments.user_id == user_id).filter(Comments.is_deleted == 0).all()
    return make_comment_array(arr, user_id, db, convert_to_comment)[skip:limit]


def create_comment(db: Session, comment: CommentCreate):
    time = datetime.now()
    db_user_comment = Comments(article_id=comment.article_id,
                               answer_id=comment.answer_id,
                               text=comment.text,
                               date_added=time,
                               user_id=comment.user_id,
                               )
    db.add(db_user_comment)
    db.commit()
    db.refresh(db_user_comment)
    return make_comment_array([db_user_comment], 0, db, convert_to_comment)


def update_comment_text(db: Session, comment_id: int, text: str, is_edited: bool):
    current_data = db.query(Comments).filter(Comments.id == comment_id).first()
    current_data.text = text
    current_data.is_edited = is_edited
    db.commit()
    return current_data


def update_comment_answer_id(db: Session, answer_id: int, comment_id: int):
    current_data = db.query(Comments).filter(Comments.id == comment_id).first()
    current_data.answer_id = answer_id
    db.commit()
    return current_data


def update_comment_is_edited(db: Session, is_edited: bool, comment_id: int):
    current_data = db.query(Comments).filter(Comments.id == comment_id).first()
    current_data.is_edited = is_edited
    db.commit()
    return current_data


def delete_comment(db: Session, comment_id: int):
    current_data = db.query(Comments).filter(Comments.id == comment_id).first()
    current_data.is_deleted = True
    db.commit()
    return current_data


def get_articles(db: Session, skip: int, limit: int):
    arr = db.query(Articles).filter(Articles.is_deleted == 0).offset(skip).limit(limit).all()
    return make_array(arr, convert_to_basic_article)


def get_last_articles(db: Session, skip: int, limit: int):
    arr = db.query(Articles).filter(Articles.is_deleted == 0).order_by(-Articles.id).offset(skip).limit(limit).all()
    return make_array(arr, convert_to_basic_article)


def get_article_by_id(db: Session, article_id: int, user_id: int):
    article = db.query(Articles).filter(Articles.id == article_id).filter(Articles.is_deleted == 0).first()
    user = db.query(Users).filter(Users.id == user_id).filter(Users.is_deleted == 0).first()
    is_read = article in user.read if user else False
    new = Article(id=article.id,
                  authorship=make_array(article.authorship, convert_to_basic_user),
                  title=article.title,
                  description=article.description,
                  background_color=article.background_color,
                  background_img=get_img(article.background_img),
                  text_color=article.text_color,
                  period_start=article.period_start,
                  period_end=article.period_end,
                  published=article.is_published,
                  moderated=article.is_moderated,
                  likes=len(article.likes),
                  rating=article.rating,
                  views=len(article.views_article),
                  date_added=article.date_added,
                  text=article.text,
                  tags=make_array(article.tags, convert_to_basic_tag),
                  is_read=is_read)
    return new


def get_tag(db: Session, tag_id: int):
    return db.query(Tags).filter(Tags.id == tag_id).filter(Tags.is_deleted == 0).first()


def get_user(db: Session, user_id: int):
    return db.query(Users).filter(Users.id == user_id).filter(Users.is_deleted == 0).first()


def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).filter(Users.is_deleted == 0).first()


def create_article(db: Session, article: ArticleCreate):
    time = datetime.now()
    db_user_article = Articles(title=article.title,
                               text=article.text,
                               date_added=time,
                               period_start=article.period_start)
    for author in article.authorship:
        if get_user(db, author):
            db_user_article.authorship.append(get_user(db, author))

    for tag in article.tags:
        if get_tag(db, tag):
            db_user_article.tags.append(get_tag(db, tag))

    db.add(db_user_article)
    db.commit()
    db.refresh(db_user_article)
    return db_user_article


def update_article_text(db: Session, article_id: int, text: str):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.text = text
    db.commit()
    return current_data


def update_article_title(db: Session, title: str, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.title = title
    db.commit()
    return current_data


def update_article_description(db: Session, description: str, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.description = description
    db.commit()
    return current_data


def update_article_is_published(db: Session, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.is_published = True
    db.commit()
    return current_data


def update_article_is_moderated(db: Session, is_moderated: bool, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.is_moderated = is_moderated
    db.commit()
    return current_data


def update_article_period_start(db: Session, period_start: Date, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.period_start = period_start
    db.commit()
    return current_data


def update_article_period_end(db: Session, period_end: Date, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.period_end = period_end
    db.commit()
    return current_data


def update_article_date_added(db: Session, date_added: Date, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.date_added = date_added
    db.commit()
    return current_data


def create_like_of_article(db: Session, user_id: int, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.likes.append(get_user(db, user_id))
    db.commit()
    return 1


def delete_article(db: Session, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).first()
    current_data.is_deleted = True
    db.commit()
    return current_data


def get_popular_tags(db: Session, skip: int = 0, limit: int = 100):
    arr = db.query(Tags).filter(Tags.is_deleted == 0).offset(skip).limit(limit).all()
    return make_array(arr, convert_to_basic_tag)


def create_tag(db: Session, tag: TagCreate):
    db_article_tag = Tags(title_rus=tag.title_rus,
                          description_rus=tag.description_rus,
                          text_color=tag.text_color,
                          background_color=tag.background_color)
    db.add(db_article_tag)
    db.commit()
    db.refresh(db_article_tag)
    return db_article_tag


def article_compilations(db: Session, user_id: int, article_id: int):
    article = db.query(Articles).filter(Articles.id == article_id).first()
    user = db.query(Users).filter(Users.id == user_id).first()
    resp = []
    for compilation in user.user_compilations:
        comp = CompilationsGet(id=compilation.id,
                               title=compilation.title,
                               saved=article in compilation.compilations)
        resp.append(comp)
    return resp


def update_tag_is_moderated(db: Session, is_moderated: bool, tag_id: int):
    current_data = db.query(Tags).filter(Tags.id == tag_id).first()
    current_data.is_moderated = is_moderated
    db.commit()
    return current_data


def delete_tag(db: Session, tag_id: int):
    current_data = db.query(Tags).filter(Tags.id == tag_id).first()
    current_data.is_deleted = True
    db.commit()
    return current_data


def get_compilation_by_id(db: Session, compilation_id: int):
    return db.query(Compilations).filter(Compilations.id == compilation_id).first()


def create_compilation(db: Session, compilation: CompilationsCreate):
    db_compilation = Compilations(title=compilation.title,
                                  description=compilation.description,
                                  is_public=compilation.public,
                                  author_id=compilation.user_id)
    db.add(db_compilation)
    db.commit()
    db.refresh(db_compilation)
    return db_compilation


def put_article_in_compilation(db: Session, compilation_id: int, article_id: int):
    new = db.query(Articles).filter(Articles.id == article_id).filter(Articles.is_deleted == False).first()
    db_comp = db.query(Compilations).filter(Compilations.id == compilation_id).filter(
        Compilations.is_deleted == 0).first()
    db_comp.compilations.append(new)
    db.commit()
    return convert_to_basic_article(new)


def update_compilation_title(db: Session, title: str, compilation_id: int):
    current_data = db.query(Compilations).filter(Compilations.id == compilation_id).first()
    current_data.title = title
    db.commit()
    return current_data


def update_compilation_description(db: Session, description: str, compilation_id: int):
    current_data = db.query(Compilations).filter(Compilations.id == compilation_id).first()
    current_data.description = description
    db.commit()
    return current_data


def login(db: Session, email: str, password: str):
    user = db.query(Users).filter(Users.email == email).filter(Users.password == password).first()
    if user:
        user.is_active = True
        db.commit()
        return convert_to_basic_user(user)
    else:
        return 0


def logout(db: Session, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        return 0
    else:
        return 0


def update_compilation_is_public(db: Session, is_public: bool, compilation_id: int):
    current_data = db.query(Compilations).filter(Compilations.id == compilation_id).first()
    current_data.is_public = is_public
    db.commit()
    return current_data


def delete_compilation(db: Session, compilation_id: int):
    current_data = db.query(Compilations).filter(Compilations.id == compilation_id).first()
    current_data.is_deleted = True
    db.commit()
    return current_data


def create_like_of_comment(db: Session, comment_id: int, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    comment = db.query(Comments).filter(Comments.id == comment_id).first()
    if comment in user.comment_likes:
        user.comment_likes.remove(comment)
    else:
        user.comment_likes.append(comment)
    db.commit()
    return 1


def create_authorship(db: Session, user_id: int, article_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    article = db.query(Articles).filter(Articles.id == article_id).first()
    user.authorship.append(article)
    db.commit()
    return 1


def create_view_of_article(db: Session, user_id: int, article_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    article = db.query(Articles).filter(Articles.id == article_id).first()
    user.viewed_article.append(article)
    db.commit()
    return 1


def create_read_of_article(db: Session, user_id: int, article_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    article = db.query(Articles).filter(Articles.id == article_id).first()
    if article in user.read:
        user.read.remove(article)
    else:
        user.read.append(article)
    db.commit()
    return 1


def get_news(db: Session):
    return db.query(News).all()


def get_news_by_user_id(db: Session, user_id: int):
    return db.query(News).filter(News.author_id == user_id).all()


def create_news(db: Session):
    db_news = association_table_comments_likes()
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news


def get_popular_articles_by_tag(db: Session, tag_id: int, skip: int, limit: int):
    tag = get_tag(db, tag_id)
    if tag == None:
        return None
    arr = make_array(tag.tags, convert_to_basic_article)
    return arr[skip:skip + limit]


def get_compilations_by_user_id(db: Session, user_id: int, skip: int, limit: int):
    arr = db.query(Compilations).filter(Compilations.is_deleted == 0).filter(Compilations.author_id == user_id)
    arr = arr.offset(skip).limit(limit).all()
    return make_array(arr, convert_to_compilation)


def delete_news(db: Session, news_id: int):
    current_data = db.query(News).filter(News.id == news_id).first()
    current_data.is_deleted = True
    db.commit()
    return current_data


def get_authorship_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user == None:
        return None
    return make_array(user.authorship, convert_to_basic_article)[skip:limit]


# def moderate_article(db: Session, article_id: int):
#     db.query(Articles).filter(Articles.id == article_id).first().is_moderated = 1
#     db.commit()
#     return 1

def get_read_articles_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user == None:
        return None
    return make_array(user.read, convert_to_basic_article)[skip:skip + limit]


def get_view_articles_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user == None:
        return None
    return make_array(user.viewed_article, convert_to_basic_article)[skip:limit]


def get_favorite_comments_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user == None:
        return None
    return make_comment_array(user.comment_likes, user_id, db, convert_to_comment)[skip:limit]


def get_comments_by_article_id(db: Session, article_id: int, user_id: int, skip: int, limit: int):
    arr = db.query(Comments).filter(Comments.article_id == article_id).filter(Comments.is_deleted == 0).offset(skip)
    arr = arr.limit(limit).all()
    return make_comment_array(arr, user_id, db, convert_to_comment)


def get_popular_articles(db: Session, skip: int, limit: int):
    time = datetime.now() - timedelta(days=7)
    arr = db.query(Articles).filter(Articles.is_deleted == 0).filter(Articles.is_moderated == 1)
    arr = arr.filter(Articles.is_published == 1).filter(Articles.date_added >= time).offset(skip).limit(limit).all()
    arr = make_array(arr, convert_to_basic_article)
    arr = list(map(dict, arr))
    arr.sort(key=operator.itemgetter('rating'), reverse=True)
    return arr


def smart_finder(db: Session, finder: Finder):
    arr = db.query(Articles).filter(Articles.is_deleted == 0).filter(Articles.is_moderated == 1)
    arr = arr.filter(Articles.is_published == 1)
    ans1 = []
    ans2 = []
    ans3 = []
    ans4 = []

    if finder.title is not None:
        arr = arr.filter(Articles.title.like(f"%{finder.title}%"))

    if finder.max_rating != 0:
        arr = arr.filter(Articles.rating <= finder.max_rating)

    if finder.min_rating != 0:
        arr = arr.filter(Articles.rating >= finder.min_rating)

    if finder.authorship_add is not None:
        for user_id in finder.authorship_add:
            arr = arr.filter(association_table_authorship.c.user_id == user_id)

    if finder.authorship_del is not None:
        for user_id in finder.authorship_del:
            arr = arr.filter(association_table_authorship.c.user_id != user_id)

    if finder.tags_add is not None:
        for tag_id in finder.tags_add:
            arr = arr.filter(association_table_tags.c.tag_id == tag_id)

    if finder.tags_del is not None:
        for tag_id in finder.tags_del:
            arr = arr.filter(association_table_tags.c.tag_id != tag_id)

    ans = arr.all()
    ans = make_array(ans, convert_to_basic_article)
    return ans


def get_articles_by_title(db: Session, title: str, skip: int, limit: int):
    return make_array(
        db.query(Articles).filter(Articles.title.like(f"%{title}%")).filter(Articles.is_deleted == 0).filter(
            Articles.is_moderated == 1).filter(Articles.is_published == 1).offset(skip).limit(limit).all(),
        convert_to_basic_article)


def get_tags_by_title(db: Session, title: str, skip: int, limit: int):
    return make_array(
        db.query(Tags).filter(Tags.title_rus.like(f"%{title}%")).filter(Tags.is_deleted == 0).offset(skip).limit(
            limit).all(), convert_to_all_tag)


def get_users_by_username(db: Session, username: str, skip: int, limit: int):
    return make_array(
        db.query(Users).filter(Users.username.like(f"%{username}%")).filter(Users.is_deleted == 0).offset(skip).limit(
            limit).all(), convert_to_basic_user)


def is_user_with_email(db: Session, email: str):
    checker = db.query(Users).filter(Users.email == email).filter(Users.is_deleted == 0).first()
    return False if checker else send_code(email)


def update_user_all(db: Session, user: UpdateUserAll):
    current_data = db.query(Users).filter(Users.id == user.id).filter(Users.is_deleted == 0).first()
    current_data.login = user.login
    current_data.first_name = user.first_name
    current_data.second_name = user.second_name
    current_data.rating_users = user.rating_users
    current_data.avatar = user.avatar
    current_data.password = user.password
    current_data.background_img = user.background_img
    current_data.username = user.username
    current_data.email = user.email
    current_data.date_of_birth = user.date_of_birth
    current_data.description = user.description
    current_data.last_activity = user.last_activity
    current_data.is_admin = user.is_admin
    current_data.is_active = user.is_active
    current_data.background_color = user.background_color
    current_data.text_color = user.text_color
    db.commit()
    return current_data


def update_article_all(db: Session, article: UpdateArticleAll, article_id: int):
    current_data = db.query(Articles).filter(Articles.id == article_id).filter(Articles.is_deleted == 0).first()
    current_data.title = article.title
    current_data.description = article.description
    current_data.text = article.text
    current_data.background_color = article.background_color
    current_data.text_color = article.text_color
    current_data.tags = []
    for t in article.tags:
        tag = get_tag(db, t)
        if tag:
            current_data.tags.append(tag)
    db.commit()
    return convert_to_basic_article(current_data)


def update_article_background_img(db: Session, article_id: int, file: bytes = File(...)):
    current_data = db.query(Articles).filter(Articles.id == article_id).filter(Articles.is_deleted == 0).first()
    with open(f'static/article{article_id}_back.jpg', 'wb') as image:
        image.write(file)
        image.close()
    current_data.background_img = f'static/article{article_id}_back.jpg'
    db.commit()
    return convert_to_basic_article(current_data)


def update_user_background_img(db: Session, user_id: int, file: bytes = File(...)):
    current_data = db.query(Users).filter(Users.id == user_id).filter(Users.is_deleted == 0).first()
    with open(f'static/user{user_id}_back.jpg', 'wb') as image:
        image.write(file)
        image.close()
    current_data.background_img = f'static/user{user_id}_back.jpg'
    db.commit()
    return convert_to_basic_user(current_data)


def update_user_avatar(db: Session, user_id: int, file: bytes = File(...)):
    current_data = db.query(Users).filter(Users.id == user_id).filter(Users.is_deleted == 0).first()
    with open(f'static/user{user_id}_avatar.jpg', 'wb') as image:
        image.write(file)
        image.close()
    current_data.avatar = f'static/user{user_id}_avatar.jpg'
    db.commit()
    return convert_to_basic_user(current_data)


def create_rating_article(db: Session, user_id: int, article_id: int, rating: int):
    if 10 < rating < 1:
        return 0
    else:
        db.query(association_table_rating).filter(association_table_rating.c.user_id == user_id).delete()
        stmt = (
            insert(association_table_rating).
                values(user_id=user_id, article_id=article_id, rating=rating)
        )
        db.execute(stmt)
        article = db.query(Articles).filter(Articles.id == article_id).filter(Articles.is_deleted == 0).first()
        rating = db.query(func.avg(association_table_rating.c.rating)).filter(
            association_table_rating.c.article_id == article_id).scalar()
        article.rating = rating
        db.commit()
        return rating
