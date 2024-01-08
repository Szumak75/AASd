global engine, session, metadata
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
import mysql.connector
import time

SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://test:test2013@172.16.1.160:24801/test?charset=utf8'
SQLALCHEMY_POOL_SIZE=45
SQLALCHEMY_POOL_MAX_OVERFLOW=45

connect_args={
    'raise_on_warnings': True,
    'failover': [{
        'user': 'test',
        'password': 'test2013',
        'host': '172.16.1.160',
        'port': 24802,
        'database': 'test',
    }, {
        'user': 'test',
        'password': 'test2013',
        'host': '172.16.1.160',
        'port': 24803,
        'database': 'test',
    }]
}
engine = create_engine(SQLALCHEMY_DATABASE_URI,connect_args=connect_args,
                       pool_size=SQLALCHEMY_POOL_SIZE,
                       max_overflow=SQLALCHEMY_POOL_MAX_OVERFLOW)
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
metadata = MetaData(bind=engine)


base= 2000

while True:
    base+=1
    info = "info%s"%base
    print info
    results = session.execute("insert into t1 values(%s,'%s')"%(base,info))
    print results
    session.commit()
    time.sleep(10)