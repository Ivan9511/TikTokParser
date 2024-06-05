from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from datetime import datetime


# Создание соединения с MySQL
MYSQL_DATABASE_URL = "mysql+pymysql://newuser:password@localhost/imas"
mysql_engine = create_engine(MYSQL_DATABASE_URL)
MySQLSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)

Base = declarative_base()

class TempPosts(Base):
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
    from_type = Column(Integer, nullable=False, default=3)
    type = Column(Integer, nullable=False, default=0)
    sphinx_status = Column(String(10), nullable=False, default='')

# После этого выполните команду для создания таблицы в базе данных
Base.metadata.create_all(mysql_engine)

@contextmanager
def get_mysql_db():
    db = MySQLSessionLocal()
    try:
        yield db
        db.commit()  # Подтверждаем изменения после успешного добавления
    except:
        db.rollback()  # Откатываем изменения в случае ошибки
        raise
    finally:
        db.close()

with get_mysql_db() as db:
    new_post = TempPosts(
        owner_id='12345',
        from_id='54321',
        item_id='98765',
        res_id=1,
        title='',
        text='Текст вашего поста',
        date=int(datetime.now().timestamp()),
        s_date=datetime.now(),
        not_date=datetime.now().date(),
        link='https://www.tiktok.com/@astana_hub/video/7376228846242123013',
        from_type=3,
        type=0
    )
    db.add(new_post)
    db.commit()