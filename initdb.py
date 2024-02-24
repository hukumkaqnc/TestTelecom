from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, ForeignKey, Sequence, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date




sql_url = "postgresql+psycopg2://postgres:admin@localhost:5432/tmpkDB"#подключение к бд
engine = create_engine(sql_url)
Base = declarative_base()

#создание таблиц
class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key = True)
    city = Column(String, nullable = False)
    srteet = Column(String, nullable = False)
    build = Column(String,nullable= False)
    apart = Column(String, default = 'None')
class Tariff(Base):
    __tablename__ = "tariff"
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    price = Column(Integer, nullable = False)
    date_start = Column(Date, default = date.today() )
    date_end = Column(Date, nullable = True)
class Contracts(Base):
    __tablename__ = "contracts"
    id = Column(String, primary_key = True)
    fio = Column(String, nullable = False)
    is_phys = Column(Boolean, default = True)
    status = Column(String, nullable = False)
    addr = Column(Integer, ForeignKey('address.id'))
    tariff = Column(Integer, ForeignKey('tariff.id'))
class Incoming(Base):
    __tablename__ = "incoming"
    id = Column(Integer, primary_key = True)
    value = Column(Integer, nullable = False)
    date = Column(Date, default = date.today())
    cont_id = Column(String, ForeignKey('contracts.id'))
    


Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autoflush=False, bind=engine)



