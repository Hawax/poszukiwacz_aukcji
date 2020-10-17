from aukcje import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy_json import MutableJson
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    id_telegram = Column(String(10), unique=True)
    username = Column(String(100))
    urls = Column(MutableJson, default={})
    checks = Column(Integer, default=600)
    urls_data = Column(MutableJson, default={})
    timeout = Column(Integer, default=300)
    dealer = Column(Boolean, default=True)
    start = Column(Boolean, default=True)

    def __repr__(self):
        return f"User, id: {self.id}, id_telegram: {self.id_telegram}, urls_data: {self.urls_data}"

#
# Base.metadata.drop_all(db)
# Base.metadata.create_all(db)
