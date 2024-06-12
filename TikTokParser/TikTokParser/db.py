from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Создание соединения с ClickHouse
CLICKHOUSE_DATABASE_URL = "clickhouse://default:123456@localhost/imas"
clickhouse_engine = create_engine(CLICKHOUSE_DATABASE_URL)
ClickHouseSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=clickhouse_engine)

# Создание соединения с MySQL
MYSQL_DATABASE_URL = "mysql+pymysql://newuser:password@localhost/test"
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
