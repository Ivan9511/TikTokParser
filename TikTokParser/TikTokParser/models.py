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