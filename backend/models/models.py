from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class AssetInfo(Base):
    __tablename__ = 'asset_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=True)
    data_source = Column(String, nullable=True)
    class_ = Column(String, nullable=True)  # 'class' is a reserved keyword in Python
    sub_class = Column(String, nullable=True)
    type = Column(String, nullable=True)

class Entry(Base):
    __tablename__ = 'entry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_date = Column(String, nullable=True)
    symbol = Column(String, nullable=True)
    cost = Column(String, nullable=True)
    # Add other fields as per the schema

class FloorCeiling(Base):
    __tablename__ = 'floor_ceiling'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test = Column(String, nullable=False)
    fc_val = Column(String, nullable=False)
    fc_date = Column(Integer, ForeignKey('stock_data.id'), nullable=False)
    rg_ch_date = Column(Integer, ForeignKey('stock_data.id'), nullable=False)
    rg_ch_val = Column(String, nullable=False)
    type = Column(String, nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)

    stock = relationship('Stock', back_populates='floor_ceilings')
    fc_date_data = relationship('StockData', foreign_keys=[fc_date])
    rg_ch_date_data = relationship('StockData', foreign_keys=[rg_ch_date])

class Peak(Base):
    __tablename__ = 'peak'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start = Column(Integer, ForeignKey('stock_data.id'), nullable=False)
    end = Column(Integer, ForeignKey('stock_data.id'), nullable=False)
    type = Column(Integer, nullable=False)
    lvl = Column(Integer, nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)

    stock = relationship('Stock', back_populates='peaks')
    start_data = relationship('StockData', foreign_keys=[start])
    end_data = relationship('StockData', foreign_keys=[end])

class Regime(Base):
    __tablename__ = 'regime'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start = Column(Integer, ForeignKey('stock_data.id'), nullable=False)
    end = Column(Integer, ForeignKey('stock_data.id'), nullable=False)
    rg = Column(String, nullable=False)
    type = Column(String, nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)

    stock = relationship('Stock', back_populates='regimes')
    start_data = relationship('StockData', foreign_keys=[start])
    end_data = relationship('StockData', foreign_keys=[end])

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

class StockData(Base):
    __tablename__ = 'stock_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    close = Column(String, nullable=False)
    open = Column(String, nullable=False)
    high = Column(String, nullable=False)
    low = Column(String, nullable=False)
    volume = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)  # Changed from String to DateTime

    stock = relationship('Stock', back_populates='stock_data')

class StockInfo(Base):
    __tablename__ = 'stock_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=True)
    security = Column(String, nullable=True)
    gics_sector = Column(String, nullable=True)
    gics_sub_industry = Column(String, nullable=True)
    headquarters_location = Column(String, nullable=True)
    date_added = Column(String, nullable=True)
    cik = Column(Integer, nullable=True)
    founded = Column(String, nullable=True)

class Stock(Base):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    is_relative = Column(String, nullable=False)
    interval = Column(String, nullable=False)
    data_source = Column(String, nullable=False)
    market_index = Column(String, nullable=False)
    sec_type = Column(String, nullable=False)

    peaks = relationship('Peak', back_populates='stock')
    regimes = relationship('Regime', back_populates='stock')
    floor_ceilings = relationship('FloorCeiling', back_populates='stock')
    stock_data = relationship('StockData', back_populates='stock')

# class TimestampData(Base):
#     __tablename__ = 'timestamp_data'

#     bar_number = Column(Integer, primary_key=True, autoincrement=True)
#     interval = Column(String, nullable=False)
#     timestamp = Column(String, nullable=False)
#     data_source = Column(String, nullable=False)

# Example engine and session setup (adjust connection string as needed):
# engine = create_engine('postgresql://user:password@localhost/dbname')
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# session = Session()