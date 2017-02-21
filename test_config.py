from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
default_user = 'jamcplusplus'


_database = 'github'
_database_user = 'root'
_database_pass = 'test'
Base = declarative_base()

class relationship(Base):
    # 表名:
    __tablename__ = 'relationship'
    # 表结构:
    id = Column(Integer, primary_key=True)
    user_name = Column(String(256))
    level = Column(Integer)
    referer = Column(String(256))
    type = Column(String(256))

class database(object):


    engine = create_engine(
            'mysql+pymysql://root:test@localhost/github', pool_size=500)
    session = sessionmaker(bind=engine)


    def __check(self, username, referer):
        tmp_session = self.session()
        try:
            tmp_session.query(relationship).filter_by(
                user_name=username, referer=referer).one()
            return True
        except Exception as e:
            return False
        finally:
            tmp_session.close()

    def find_level(self, level):
        tmp_session = self.session()
        users = []
        res = tmp_session.query(relationship).filter_by(
            level=level).all()
        try:
            for i in res:
                users.append(i.user_name)
        except Exception as e:
            pass
        finally:
            tmp_session.close()
            return users

    def create_table(self):
        metadata = MetaData(self.engine)
        self.user = Table('relationship', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('user_name', String(256)),
                          Column('referer', String(256)),
                          Column('level', Integer),
                          Column('type', String(256))
                          )
        metadata.create_all()

    def insert(self, **kwargs):
        tmp_session = self.session()
        user_name = kwargs['user_name']
        referer = kwargs['referer']
        action = kwargs['action']
        level = kwargs['level']
        if self.__check(username=user_name, referer=referer):
            return
        new_user = relationship(
            user_name=user_name,
            level=level,
            type=action,
            referer=referer)
        tmp_session.add(new_user)
        tmp_session.commit()
        tmp_session.close()

    def init_user(self):
        tmp_session = self.session()
        init = relationship(
            user_name=default_user,
            level=0,
            type='',
            referer='self')
        tmp_session.add(init)
        tmp_session.commit()
        tmp_session.close()
