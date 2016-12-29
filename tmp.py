from flask import Flask, jsonify
import requests
app = Flask(__name__)
import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
engine = create_engine('mysql+pymysql://github:test@localhost/github')
DBSession = sessionmaker(bind=engine)
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

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/effect')
def effect():
    server_chan_url = 'http://sc.ftqq.com/SCU4819T4a9424bcfd09b1c39cee36cae6309d9758648caace3a6.send'
    tmp_session = DBSession()
    res = tmp_session.query(relationship).count()
    data = {
        'text':'%s 总计' % datetime.datetime.now(),
        'desp':res
    }
    tmp_session.close()
    r = requests.post(url=server_chan_url, data=data)
    return jsonify(data)

@app.route('/effect/view')
def view():
    tmp_session = DBSession()



if __name__ == "__main__":
    app.run()