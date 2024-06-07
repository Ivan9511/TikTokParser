from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from clickhouse_driver import Client
from models import temp_posts_max_date  # Замените на ваш импорт моделей

# Создание соединения с ClickHouse
CLICKHOUSE_DATABASE_URL = "clickhouse://default:123456@localhost/imas"
clickhouse_engine = create_engine(CLICKHOUSE_DATABASE_URL)
ClickHouseSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=clickhouse_engine)

# Создание соединения с MySQL
MYSQL_DATABASE_URL = "mysql+pymysql://newuser:password@localhost/imas"
mysql_engine = create_engine(MYSQL_DATABASE_URL)
MySQLSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)

Base = declarative_base()

@contextmanager
def get_clickhouse_db():
    db = ClickHouseSessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_mysql_db():
    db = MySQLSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_clickhouse_res_ids():
    query = text('SELECT id FROM resource_social')  # Замените на ваш запрос
    with get_clickhouse_db() as db:
        res = db.execute(query).fetchall()
    clickhouse_res_ids = {row[0] for row in res}
    return clickhouse_res_ids

def get_mysql_res_ids():
    with get_mysql_db() as db:
        mysql_res_ids = {row.res_id for row in db.query(temp_posts_max_date.res_id).all()}
    return mysql_res_ids

def find_missing_res_ids(clickhouse_res_ids, mysql_res_ids):
    missing_res_ids = clickhouse_res_ids - mysql_res_ids
    return missing_res_ids

clickhouse_res_ids = get_clickhouse_res_ids()
mysql_res_ids = get_mysql_res_ids()
missing_res_ids = find_missing_res_ids(clickhouse_res_ids, mysql_res_ids)

print("Missing res_ids:", missing_res_ids)