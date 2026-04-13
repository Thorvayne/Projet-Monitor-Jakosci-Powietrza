from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from geopy.distance import geodesic
import httpx
import asyncio
from typing import Optional

from database import engine, Base, get_db
from db_models import UserDB, CityDB, FavoriteDB
import auth
import gios_client
from models import Station, AirQualityIndex

app = FastAPI(title="Air Quality API - Poland")


# async def update_history_worker():
#     while True:
#         async with SessionLocal() as db:
#             print("Worker: Pobieram dane historyczne...")
#             for city_name in ["Łódź", "Warszawa", "Kraków"]: # Tutaj Twoja lista miast
#                 # Tutaj wywołujesz swoją logikę pobierania danych z GIOŚ (tę z endpointu)
#                 # I zapisujesz wynik do AirQualityHistoryDB
#                 pass
#         await asyncio.sleep(3600) # Czekaj godzinę



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FavoriteCreate(BaseModel):
    username: str
    city_name: str

class UserCreate(BaseModel):
    username: str
    password: str

class CityCreate(BaseModel):
    name: str
    gios_station_id: int

async def get_city_coords(city_name: str):
    # Nominatim wymaga unikalnego User-Agenta, inaczej blokuje (403/502)
    headers = {"User-Agent": "AirQualityMonitorApp/1.0 (twoj-mail@przyklad.com)"}
    url = f"https://nominatim.openstreetmap.org/search?city={city_name}&country=Poland&format=json"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"Błąd Nominatim: {e}")
    return None, None

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

@app.get("/air-quality")
async def get_air_quality(city: str, station_id: Optional[int] = None):
    try:
        # 1. Pobierz wszystkie stacje z GIOŚ
        stations_response = await gios_client.fetch_all_stations()
        stations = stations_response.get("Lista stacji pomiarowych", [])

        # 2. Szukamy wszystkich stacji w danym mieście
        city_stations = [s for s in stations if s.get("Nazwa miasta", "").lower() == city.lower()]
        
        target_station = None
        nearest_info = ""
        available_stations = []

        if city_stations:
            # Przygotowujemy listę wszystkich stacji dla tego miasta do wyświetlenia na froncie
            available_stations = [{"id": s["Identyfikator stacji"], "name": s["Nazwa stacji"]} for s in city_stations]
            
            # Jeśli użytkownik wybrał konkretną stację (z dropdowna), szukamy jej
            if station_id:
                target_station = next((s for s in city_stations if s["Identyfikator stacji"] == int(station_id)), city_stations[0])
            else:
                # Domyślnie bierzemy pierwszą stację z brzegu
                target_station = city_stations[0]
        else:
            # 3. Jeśli nie ma w ogóle stacji w tym mieście, szukamy najbliższej w Polsce
            city_lat, city_lon = await get_city_coords(city)
            
            if city_lat and city_lon:
                def calculate_distance(s):
                    try:
                        s_lat = float(s['WGS84 φ N'].replace(',', '.'))
                        s_lon = float(s['WGS84 λ E'].replace(',', '.'))
                        return geodesic((city_lat, city_lon), (s_lat, s_lon)).km
                    except:
                        return 999999

                target_station = min(stations, key=calculate_distance)
                dist = round(calculate_distance(target_station), 1)
                nearest_info = f"Brak stacji w {city.capitalize()}. Najbliższa: {target_station['Nazwa stacji']} ({dist} km)"
                available_stations = [{"id": target_station["Identyfikator stacji"], "name": target_station["Nazwa stacji"]}]
            else:
                raise HTTPException(status_code=404, detail=f"Nie znaleziono miasta ani stacji dla: {city}")

        # 4. Pobieramy dane o jakości ORAZ liczby z sensorów
        current_station_id = target_station["Identyfikator stacji"]
        
        index_task = gios_client.fetch_station_index(current_station_id)
        sensors_task = gios_client.fetch_sensors_data(current_station_id) 
        
        try:
            index_data_full, sensor_values = await asyncio.gather(index_task, sensors_task)
        except Exception as e:
            print(f"Ostrzeżenie gather: {e}")
            index_data_full = await gios_client.fetch_station_index(current_station_id)
            sensor_values = {}

        aq_data = index_data_full.get("AqIndex", {})
        level_name = aq_data.get("Nazwa kategorii indeksu", "Brak danych")

        # Mapowanie AQI dla kolorów
        aqi_value = 80
        if level_name == "Bardzo dobry": aqi_value = 20
        elif level_name == "Dobry": aqi_value = 40
        elif level_name in ["Umiarkowany", "Dostateczny"]: aqi_value = 70
        elif level_name in ["Zły", "Bardzo zły"]: aqi_value = 150

        return {
            "city": city.capitalize(),
            "station_name": target_station.get("Nazwa stacji"),
            "station_id": current_station_id,               # <--- Zwracamy ID aktualnej stacji
            "available_stations": available_stations,       # <--- Zwracamy listę wszystkich stacji
            "aqi": aqi_value,
            "status_text": level_name,
            "timestamp": aq_data.get("Data wykonania obliczeń indeksu", "Brak danych"),
            "nearest_info": nearest_info,
            "sensors": sensor_values
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Błąd główny: {e}")
        raise HTTPException(status_code=502, detail="Problem z połączeniem z usługami zewnętrznymi.")
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
    
    return {
        "message": f"Zalogowano jako {db_user.username}",
        "username": db_user.username
    }


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

@app.post("/favorites")
async def add_favorite(fav: FavoriteCreate, db: AsyncSession = Depends(get_db)):
    # 1. Szukamy użytkownika
    result = await db.execute(select(UserDB).where(UserDB.username == fav.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika.")
    
    # 2. Sprawdzamy, czy miasto już jest w ulubionych
    check = await db.execute(
        select(FavoriteDB).where(FavoriteDB.user_id == user.id, FavoriteDB.city_name == fav.city_name)
    )
    if check.scalars().first():
        return {"message": "Miasto jest już w ulubionych"}

    # 3. Zapisujemy do bazy
    new_fav = FavoriteDB(city_name=fav.city_name, user_id=user.id)
    db.add(new_fav)
    await db.commit()
    return {"message": f"Dodano {fav.city_name} do ulubionych!"}

@app.delete("/favorites")
async def delete_favorite(fav: FavoriteCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserDB).where(UserDB.username == fav.username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(FavoriteDB).where(
            FavoriteDB.user_id == user.id,
            FavoriteDB.city_name == fav.city_name
        )
    )
    favorite = result.scalars().first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    await db.delete(favorite)
    await db.commit()

    return {"message": f"Usunięto {fav.city_name}"}

@app.get("/favorites/{username}")
async def get_favorites(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserDB).where(UserDB.username == username))
    user = result.scalars().first()
    if not user:
        return []
        
    favs = await db.execute(select(FavoriteDB).where(FavoriteDB.user_id == user.id))
    return [f.city_name for f in favs.scalars().all()]




@app.get("/ranking")
async def get_ranking():
    try:
        stations_response = await gios_client.fetch_all_stations()
        stations = stations_response.get("Lista stacji pomiarowych", [])
        
        major_cities = ['Warszawa', 'Kraków', 'Wrocław', 'Poznań', 'Gdańsk', 'Szczecin', 'Lublin', 'Katowice', 'Łódź', 'Białystok']

        sem = asyncio.Semaphore(3)

        async def safe_fetch(station_id, city_name):
            async with sem:
                for attempt in range(3):
                    try:
                        # NOWOŚĆ: Pobieramy OBA zestawy danych, żeby złamać remisy!
                        idx_task = gios_client.fetch_station_index(station_id)
                        sen_task = gios_client.fetch_sensors_data(station_id)
                        
                        idx_data, sen_data = await asyncio.gather(idx_task, sen_task)
                        return idx_data, sen_data, city_name
                    except Exception as e:
                        if attempt == 2:
                            print(f"Odrzucono ranking {city_name}: {e}")
                            return None, None, city_name
                        await asyncio.sleep(0.5)

        tasks = []
        for city in major_cities:
            station = next((s for s in stations if s.get("Nazwa miasta", "").lower() == city.lower()), None)
            if station:
                tasks.append(safe_fetch(station["Identyfikator stacji"], city))

        if not tasks:
            return {"best": {"name": "--", "aqi": 0, "status": ""}, "worst": {"name": "--", "aqi": 0, "status": ""}}

        results_data = await asyncio.gather(*tasks)
        results = []

        for idx_data, sen_data, city_name in results_data:
            if not idx_data:
                continue
            
            aq_data = idx_data.get("AqIndex", {})
            level_name = aq_data.get("Nazwa kategorii indeksu") or "Brak"

            valid_levels = ["Bardzo dobry", "Dobry", "Umiarkowany", "Dostateczny", "Zły", "Bardzo zły"]

            if level_name in valid_levels:
                # 1. Baza punktowa (Główne sortowanie)
                base_score = 80
                if level_name == "Bardzo dobry": base_score = 20
                elif level_name == "Dobry": base_score = 40
                elif level_name in ["Umiarkowany", "Dostateczny"]: base_score = 70
                elif level_name in ["Zły", "Bardzo zły"]: base_score = 150

                # 2. Łamacz remisów (Tie-breaker) na podstawie pyłów
                tie_breaker = 0.0
                if sen_data:
                    pm10_obj = sen_data.get("PM10")
                    pm25_obj = sen_data.get("PM2.5")
                    
                    pm10_val = pm10_obj.get("current") if isinstance(pm10_obj, dict) else None
                    pm25_val = pm25_obj.get("current") if isinstance(pm25_obj, dict) else None
                    
                    # Bierzemy PM10, jak nie ma to PM2.5, a jak nie ma to 0
                    actual_val = pm10_val if pm10_val is not None else (pm25_val if pm25_val is not None else 0)
                    
                    # Zamieniamy np. 35 ug/m3 na 0.035 punktu.
                    tie_breaker = actual_val / 1000.0

                final_score = base_score + tie_breaker
                results.append({"name": city_name, "aqi": final_score, "status": level_name})

        if not results:
             return {"best": {"name": "--", "aqi": 0, "status": "Brak danych"}, "worst": {"name": "--", "aqi": 0, "status": "Brak danych"}}

        # Teraz sortowanie ułoży to perfekcyjnie, bo punkty to np. 40.012 vs 40.035
        results.sort(key=lambda x: x["aqi"])
        
        return {
            "best": results[0], 
            "worst": results[-1] 
        }
    except Exception as e:
        print(f"Krytyczny błąd rankingu: {e}")
        return {"best": {"name": "--", "aqi": 0, "status": "Błąd"}, "worst": {"name": "--", "aqi": 0, "status": "Błąd"}}

@app.get("/map-stations")
async def get_map_stations():
    try:
        stations_response = await gios_client.fetch_all_stations()
        stations = stations_response.get("Lista stacji pomiarowych", [])
        
        map_data = []
        for s in stations:
            try:
                # GIOŚ podaje koordynaty z przecinkiem, np. "52,23". Zmieniamy na "52.23" (float)
                lat = float(s['WGS84 φ N'].replace(',', '.'))
                lon = float(s['WGS84 λ E'].replace(',', '.'))
                
                map_data.append({
                    "id": s["Identyfikator stacji"],
                    "name": s["Nazwa stacji"],
                    "city": s.get("Nazwa miasta", "Nieznane"),
                    "lat": lat,
                    "lon": lon
                })
            except Exception:
                continue # Pomijamy stacje z uszkodzonymi współrzędnymi
                
        return map_data
    except Exception as e:
        print(f"Błąd mapy: {e}")
        return []