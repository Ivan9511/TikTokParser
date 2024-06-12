from sqlalchemy import Column, Integer, String, Date, DateTime, BigInteger, SmallInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class resource_social(Base):
    __tablename__ = 'resource_social'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    country_id = Column(SmallInteger)
    region_id = Column(SmallInteger)
    city_id = Column(SmallInteger)
    resource_name = Column(String)
    link = Column(String)
    screen_name = Column(String)
    type = Column(Integer)
    stability = Column(Integer)
    image_profile = Column(String)
    s_id = Column(String)
    start_date_imas = Column(Date)
    members = Column(Integer)
    info_check = Column(Integer)
    datetime_enable = Column(DateTime)
    worker = Column(Integer)

class temp_posts(Base):
    __tablename__ = 'temp_posts'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_id = Column(String(30), nullable=False)
    from_id = Column(String(30), nullable=False)
    item_id = Column(String(30), nullable=False)
    res_id = Column(Integer, nullable=False)
    title = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    text = Column(String(collation='utf8mb4_unicode_ci'), nullable=False)
    date = Column(Integer, nullable=False)
    s_date = Column(DateTime, nullable=False)
    not_date = Column(Date, nullable=False)
    link = Column(String(4000), nullable=False)
    from_type = Column(Integer, nullable=False, default=0)
    type = Column(Integer, nullable=False, default=0)
    sphinx_status = Column(String(10), nullable=False, default='')

class posts_likes(Base):
    __tablename__ = 'posts_likes'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_id = Column(String(30), nullable=False)
    from_id = Column(String(30), nullable=False)
    item_id = Column(String(30), nullable=False)
    reposts = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)
    likes = Column(Integer, nullable=False)

class temp_attachments(Base):
    __tablename__ = 'temp_attachments'

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    post_id = Column(BigInteger, default=0) # по умолчанию - 0
    attachment = Column(String(4000), nullable=False) # ссылка на фото или видео
    type = Column(Integer, nullable=False) #если фото - 0, если видео - 2
    owner_id = Column(Integer, nullable=False) #  ID источника в TikTok (s_id в таблице resource_social)
    from_id = Column(String(30), nullable=False)
    item_id = Column(String(30), nullable=False) # ID поста в TikTok (aweme_id)

class temp_posts_max_date(Base):
    __tablename__ = 'temp_posts_max_date'

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    type = Column(Integer) #TikTok, тип соц. сети в системе iMAS
    res_id = Column(BigInteger) #ID в таблице resource_social
    max_date = Column(Integer) # самая поздняя дата поста из всех постов
    min_date = Column(Integer)
    min_item_id = Column(Integer)