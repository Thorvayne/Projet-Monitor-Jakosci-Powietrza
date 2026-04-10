from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relacja - jeden użytkownik może mieć wiele ulubionych
    favorites = relationship("FavoriteDB", back_populates="owner", cascade="all, delete-orphan")

class FavoriteDB(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("UserDB", back_populates="favorites")
    
class CityDB(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    gios_station_id = Column(Integer)
    
# class AirQualityHistoryDB(Base):
#     __tablename__ = "air_quality_history"
#     id = Column(Integer, primary_key=True, index=True)
#     city_name = Column(String, index=True)
#     aqi = Column(Integer)
#     pm25 = Column(String)
#     pm10 = Column(String)
#     timestamp = Column(DateTime, default=datetime.utcnow)