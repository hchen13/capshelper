
from sqlalchemy import Column, String, Integer, Float, create_engine, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
import numpy as np
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def _json_repr(value):
    repr = str(value)
    try:
        repr = float(repr)
    except ValueError:
        return repr
    return repr


class Candlestick(Base):
    __tablename__ = 'candlestick'

    id = Column(Integer, primary_key=True)
    base = Column(String(10))
    counter = Column(String(10))
    timestamp = Column(Integer)
    time = Column(DateTime)
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Float)
    ma1 = Column(Float)
    ma2 = Column(Float)
    ma3 = Column(Float)
    macd_proper = Column(Float)
    macd_signal = Column(Float)
    macd_diff = Column(Float)

    __table_args__ = (UniqueConstraint('base', 'counter', 'timestamp', name='base_counter_time_uniq'),)

    def __repr__(self):
        return "<{}/{} - o: {:.3f} h: {:.3f} l: {:.3f} c:{:.3f} v:{:.3f}>".format(
            self.base, self.counter,
            self.open, self.high, self.low, self.close, self.volume
        )

    def as_vector(self, column_vector=False):
        v = np.array([self.open, self.high, self.low, self.close, self.volume])
        v = v.reshape(-1, 1)
        if column_vector:
            v = v.T
        return v

    def to_representation(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns }


def init_db(host, name, user, pwd):
    url = '{dialect}+{driver}://{username}:{password}@{host}/{db}?charset=utf8'.format(
        dialect='mysql',
        driver='mysqldb',
        username=user,
        password=pwd,
        host=host,
        db=name
    )
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session
