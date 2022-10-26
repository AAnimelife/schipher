from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

association_table_comments_likes = Table('comments_likes', Base.metadata,
                                         Column('user_id', Integer, ForeignKey('users.id')),
                                         Column('comment_id', Integer, ForeignKey('comments.id')))

association_table_articles_likes = Table('articles_likes', Base.metadata,
                                         Column('user_id', Integer, ForeignKey('users.id')),
                                         Column('article_id', Integer, ForeignKey('articles.id')))

association_table_authorship = Table('authorship', Base.metadata,
                                     Column('user_id', Integer, ForeignKey('users.id')),
                                     Column('article_id', Integer, ForeignKey('articles.id')),
                                     Column('role', String))

association_table_readers = Table('readers', Base.metadata,
                                  Column('user_id', Integer, ForeignKey('users.id')),
                                  Column('article_id', Integer, ForeignKey('articles.id')))

association_table_views_article = Table('views_article', Base.metadata,
                                        Column('user_id', Integer, ForeignKey('users.id')),
                                        Column('article_id', Integer, ForeignKey('articles.id')))

association_table_rating = Table('rating', Base.metadata,
                                 Column('user_id', Integer, ForeignKey('users.id')),
                                 Column('article_id', Integer, ForeignKey('articles.id')),
                                 Column('rating', String))

association_table_compilations = Table('compilationss', Base.metadata,
                                       Column('compilation_id', Integer, ForeignKey('compilations.id')),
                                       Column('article_id', Integer, ForeignKey('articles.id')))

association_table_tags = Table('tagss', Base.metadata,
                               Column('tag_id', Integer, ForeignKey('tags.id')),
                               Column('article_id', Integer, ForeignKey('articles.id')))

association_table_views_news = Table('views_news', Base.metadata,
                                     Column('user_id', Integer, ForeignKey('users.id')),
                                     Column('news_id', Integer, ForeignKey('news.id')))

association_table_receiver_id_articles = Table('receiver_id_articles', Base.metadata,
                                               Column('user_id', Integer, ForeignKey('users.id')),
                                               Column('article_notification_id', Integer,
                                                      ForeignKey('article_notifications.id')))  # !!!!!!!!!!!!!!!!!!!

association_table_receiver_id_news = Table('receiver_id_news', Base.metadata,
                                           Column('user_id', Integer, ForeignKey('users.id')),
                                           Column('news_notification_id', Integer, ForeignKey('news_notifications.id')))

association_table_receiver_id_comments = Table('receiver_id_comments', Base.metadata,
                                               Column('user_id', Integer, ForeignKey('users.id')),
                                               Column('comments_notification_id', Integer,
                                                      ForeignKey('comments_notifications.id')))


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    login = Column(String)
    first_name = Column(String)
    second_name = Column(String)
    rating_users = Column(Integer, default=0)
    avatar = Column(String)
    background_img = Column(String)
    background_color = Column(String)
    text_color = Column(String)
    password = Column(String)
    username = Column(String)
    email = Column(String, unique=True)
    description = Column(String)
    date_added = Column(DateTime)
    date_of_birth = Column(Date)
    last_activity = Column(DateTime)
    is_active = Column(Boolean)
    is_deleted = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    user_comments = relationship('Comments')
    user_compilations = relationship('Compilations')
    user_news = relationship('News')


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    answer_id = Column(Integer, default=0)
    text = Column(String)
    date_added = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    article_id = Column(Integer, ForeignKey('articles.id'))
    likes = relationship("Users", backref="comment_likes",
                         secondary=association_table_comments_likes)


class Articles(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    text = Column(String)
    period_start = Column(Date)
    background_color = Column(String)
    background_img = Column(String)
    text_color = Column(String)
    period_end = Column(Date)
    date_added = Column(DateTime)
    rating = Column(Float, default=0)
    is_published = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_moderated = Column(Boolean, default=True)

    article_comments = relationship('Comments')
    likes = relationship("Users", backref="articles_likes",
                         secondary=association_table_articles_likes)
    authorship = relationship("Users", backref="authorship",
                              secondary=association_table_authorship)
    readers = relationship("Users", backref="read",
                           secondary=association_table_readers)
    views_article = relationship("Users", backref="viewed_article",
                                 secondary=association_table_views_article)
    rating_articles = relationship("Users", backref="rating",
                                   secondary=association_table_rating)
    tags = relationship("Tags", backref="tags",
                        secondary=association_table_tags)


class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    title_rus = Column(String)
    title_eng = Column(String)
    description_rus = Column(String)
    description_eng = Column(String)
    text_color = Column(String)
    background_color = Column(String)
    is_deleted = Column(Boolean, default=False)
    is_moderated = Column(Boolean, default=True)


class Compilations(Base):
    __tablename__ = "compilations"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    is_public = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    author_id = Column(Integer, ForeignKey('users.id'))
    compilations = relationship("Articles", backref="compilations",
                                secondary=association_table_compilations)


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date_added = Column(DateTime)
    period_start = Column(Date)
    period_end = Column(Date)
    text = Column(String)
    is_deleted = Column(Boolean, default=False)

    author_id = Column(Integer, ForeignKey('users.id'))
    views_news = relationship("Users", backref="views_news",
                              secondary=association_table_views_news)


class ArticleNotifications(Base):
    __tablename__ = "article_notifications"
    id = Column(Integer, primary_key=True)
    is_deleted = Column(Boolean, default=False)
    is_readed = Column(Boolean)

    article_id = Column(Integer, ForeignKey('articles.id'))


class NewsNotifications(Base):
    __tablename__ = "news_notifications"
    id = Column(Integer, primary_key=True)
    is_deleted = Column(Boolean, default=False)
    is_readed = Column(Boolean)

    news_id = Column(Integer, ForeignKey('news.id'))


class CommentsNotifications(Base):
    __tablename__ = "comments_notifications"
    id = Column(Integer, primary_key=True)
    is_deleted = Column(Boolean, default=False)
    is_readed = Column(Boolean)

    comment_id = Column(Integer, ForeignKey('comments.id'))
