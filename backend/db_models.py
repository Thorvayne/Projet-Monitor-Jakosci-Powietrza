from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# 👤 USER
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    favorites = relationship(
        "FavoriteDB",
        back_populates="owner",
        cascade="all, delete-orphan"
    )


# ⭐ FAVORITES
class FavoriteDB(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("UserDB", back_populates="favorites")


# 🏙️ CITY
class CityDB(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    gios_station_id = Column(Integer)
