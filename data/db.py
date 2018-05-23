import numpy as np
from sqlalchemy import String, Column, Integer, create_engine, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from settings import *

Base = declarative_base()


class Coin(Base):
    __tablename__ = 'coin'

    coin_name = Column(String(50))
    algorithm = Column(String(100))
    fullname = Column(String(100))
    id = Column(Integer)
    image_url = Column(String(200))
    name = Column(String(50))
    symbol = Column(String(15), primary_key=True)
    url = Column(String(200))

    candlesticks = relationship('Candlestick', back_populates='coin')


class Candlestick(Base):
    __tablename__ = 'candlestick'

    coin_symbol = Column(String(15), ForeignKey('coin.symbol'), primary_key=True)
    timestamp = Column(Integer, primary_key=True)
    time = Column(DateTime)
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Float)
    bench = Column(String(15))

    coin = relationship('Coin', back_populates='candlesticks')

    def __repr__(self):
        return "<{} - o: {:.3f} h: {:.3f} l: {:.3f} c:{:.3f} v:{:.3f}>".format(
            self.coin_symbol, self.open, self.high, self.low, self.close, self.volume
        )

    def as_vector(self):
        return np.array([self.open, self.high, self.low, self.close, self.volume])


def init_db():
    url = '{dialect}+{driver}://{username}:{password}@{host}/{db}?charset=utf8'.format(
        dialect='mysql',
        driver='mysqldb',
        username=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        db=DB_NAME)
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session