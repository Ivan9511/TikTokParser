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
