from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()
engine = create_engine('sqlite:///christmas_flight_database.db')
Session = sessionmaker(bind=engine)


class Flight(Base):
    __tablename__ = 'flights'

    id = Column(Integer, primary_key=True)
    data_flight = Column(String, nullable=False)
    data_added = Column(Date, default=datetime.datetime.utcnow, nullable=False)
    destination = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    def __repr__(self):
        return f"\n\ndata: {self.data_flight}\n destination: {self.destination}\n price: {self.price}"


Base.metadata.create_all(engine)
