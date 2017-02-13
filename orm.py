from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建连接
# '数据库类型+数据库驱动名称://用户名:口令@机器地址:端口号/数据库名'
engine = create_engine('mysql+pymysql://github:test@localhost/github')
# 创建表
metadata = MetaData(engine)
user = Table('relationship', metadata,
             Column('id', Integer, primary_key=True),
             Column('user_name', String(256)),
             Column('referer', String(256)),
             Column('level', Integer),
             Column('type', String(256))
             )
metadata.create_all()
# 创建对象的基类
Base = declarative_base()
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

# 定义User对象:

class relationship(Base):
    # 表名:
    __tablename__ = 'relationship'
    # 表结构:
    id = Column(Integer, primary_key=True)
    user_name = Column(String(256))
    level = Column(Integer)
    referer = Column(String(256))
    type = Column(String(256))
