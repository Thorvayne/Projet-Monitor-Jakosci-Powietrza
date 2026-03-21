from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List

from database import engine, Base, get_db
from db_models import UserDB, CityDB
import auth
import gios_client
from models import Station, AirQualityIndex

app = FastAPI(title="Air Quality API - Poland")


class UserCreate(BaseModel):
    username: str
    password: str

class CityCreate(BaseModel):
    name: str
    gios_station_id: int


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ==========================================
# --- ENDPOINTY GIOŚ (JAKOŚĆ POWIETRZA) ---
# ==========================================

@app.get("/stations")
async def get_stations():
    try:
        stations = await gios_client.fetch_all_stations()
        return stations
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Błąd komunikacji z GIOŚ lub Redis: {str(e)}")

@app.get("/stations/{station_id}/index")
async def get_station_index(station_id: int):
    
    try:
        index_data = await gios_client.fetch_station_index(station_id)
        return index_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Błąd komunikacji z GIOŚ lub Redis: {str(e)}")

# ==========================================
# --- ENDPOINTY UŻYTKOWNIKÓW I MIAST ---
# ==========================================

@app.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserDB).where(UserDB.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Użytkownik o takiej nazwie już istnieje.")
    
    hashed_pw = auth.get_password_hash(user.password)
    new_user = UserDB(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()
    return {"message": "Użytkownik zarejestrowany pomyślnie!"}

@app.post("/login")
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserDB).where(UserDB.username == user.username))
    db_user = result.scalars().first()
    
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Nieprawidłowy login lub hasło.")
    
    return {"message": f"Zalogowano pomyślnie jako {db_user.username}"}

@app.post("/cities")
async def add_city(city: CityCreate, db: AsyncSession = Depends(get_db)):
    new_city = CityDB(name=city.name, gios_station_id=city.gios_station_id)
    db.add(new_city)
    await db.commit()
    return {"message": f"Miasto {city.name} dodane do bazy."}

@app.get("/cities")
async def get_cities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CityDB))
    return result.scalars().all()
