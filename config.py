import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, TIMESTAMP, MetaData, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


default_user = 'jamcplusplus'

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

class repo(Base):
    # 表名:
    __tablename__ = 'repo'
    # 表结构:
    id = Column(Integer, primary_key=True)
    project_name = Column(String(256))
    project_url = Column(String(256))
    project_user = Column(String(256))

class star(Base):
    # 表名:
    __tablename__ = 'star'
    # 表结构:
    id = Column(Integer, primary_key=True)
    project_name = Column(String(256))
    project_url = Column(String(256))
    project_owner = Column(String(256))
    referer_user = Column(String(256))

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
        self.relationship = Table('relationship', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('user_name', String(256)),
                          Column('referer', String(256)),
                          Column('level', Integer),
                          Column('type', String(256))
                          )
        metadata.create_all()

    def relationship(self, **kwargs):
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

    def repo(self, **kwargs):
        tmp_session = self.session()
        project_name = kwargs['project_name']
        project_url = kwargs['project_url']
        project_user = kwargs['project_user']
        new_project = repo(
            project_name=project_name,
            project_url=project_url,
            project_user=project_user)
        tmp_session.add(new_project)
        tmp_session.commit()
        tmp_session.close()

    def star(self, **kwargs):
        tmp_session = self.session()
        project_name = kwargs['project_name']
        project_url = kwargs['project_url']
        project_owner = kwargs['project_owner']
        referer_user = kwargs['referer_user']
        new_project = star(
            project_name=project_name,
            project_url=project_url,
            project_owner=project_owner,
            referer_user=referer_user)
        tmp_session.add(new_project)
        tmp_session.commit()
        tmp_session.close()


    def init_user(self):
        """"初始化用户"""
        tmp_session = self.session()
        init = relationship(
            user_name=default_user,
            level=0,
            type='',
            referer='self')
        tmp_session.add(init)
        tmp_session.commit()
        tmp_session.close()


class github_statistics_all(Base):
    __tablename__ = 'statistics_all'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP, default=datetime.datetime.now())
    total = Column(Integer)


class github_statistics_level(Base):
    __tablename__ = 'statistics_level'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP, default=datetime.datetime.now())
    total = Column(Integer)
    level = Column(Integer)


class statistics(database):

    def __init__(self):
        statistics_engine = create_engine('sqlite:///statistics.db')
        self.DBSession = sessionmaker(bind=statistics_engine)

    def statistics_all(self):
        tmp_session = self.session()
        total = tmp_session.query(
            func.count()).select_from(relationship).scalar()
        tmp_session.close()
        statistics_session = self.DBSession()
        all = github_statistics_all(
            total=total
        )
        statistics_session.add(all)
        statistics_session.commit()
        statistics_session.close()
        return total

    def statistics_level(self, level):
        tmp_session = self.session()
        total = tmp_session.query(
            func.count(
                'level={}'.format(level))).select_from(relationship).scalar()
        tmp_session.close()
        statistics_session = self.DBSession()
        level = github_statistics_level(
            total=total,
            level=level
        )
        statistics_session.add(level)
        statistics_session.commit()
        statistics_session.close()
        return total
