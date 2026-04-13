import httpx

BASE_URL = "https://api.gios.gov.pl/pjp-api/v1/rest"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

async def fetch_all_stations():
    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        all_stations = []
        page = 0
        total_pages = 1  # Zaczynamy od 1, żeby pętla ruszyła
        
        # Pętla, która "przeklika" wszystkie strony wyników z GIOŚ
        while page < total_pages:
            # Pobieramy bezpiecznie po 100 wyników na stronę
            response = await client.get(f"{BASE_URL}/station/findAll?size=100&page={page}")
            response.raise_for_status()
            data = response.json()
            
            # Wyciągamy stacje z obecnej strony i doklejamy do naszego wielkiego zbioru
            stations_on_page = data.get("Lista stacji pomiarowych", [])
            all_stations.extend(stations_on_page)
            
            # GIOŚ mówi nam, ile jest wszystkich stron - aktualizujemy licznik!
            total_pages = data.get("totalPages", 1)
            page += 1
            
        # Zwracamy złączone wyniki z całej Polski (teraz Łódź na pewno tu jest!)
        return {"Lista stacji pomiarowych": all_stations}

async def fetch_station_index(station_id: int):
    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        response = await client.get(f"{BASE_URL}/aqindex/getIndex/{station_id}")
        response.raise_for_status()
        return response.json()

async def fetch_sensors_data(station_id: int):
    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        try:
            resp = await client.get(f"{BASE_URL}/station/sensors/{station_id}")
            sensors_raw = resp.json()
            
            # 1. Wyciągamy listę używając dokładnego klucza z Twoich logów
            sensors = sensors_raw.get("Lista stanowisk pomiarowych dla podanej stacji", [])
                
           # ...
            # Zmieniamy listę poszukiwanych sensorów na szerszą
# Poszukiwane zanieczyszczenia
            target_sensors = ["PM2.5", "PM10", "NO2", "O3", "SO2", "CO", "C6H6"]
            
            # ZACZYNAMY OD PUSTEGO SŁOWNIKA!
            results = {} 
            
            # 2. Pętla po stanowiskach
            for s in sensors:
                code = s.get("Wskaźnik - kod", "").upper()
                
                if code in target_sensors:
                    if code not in results:
                        results[code] = None
                        
                    sensor_id = s.get("Identyfikator stanowiska")
                    data_resp = await client.get(f"{BASE_URL}/data/getData/{sensor_id}")
                    data_json = data_resp.json()
                    
                    values = data_json.get("Lista danych pomiarowych") or data_json.get("values") or []
                        
                    history = []
                    current_val = None
                    
                    # Przechodzimy przez wszystkie pomiary (GIOŚ podaje je od najnowszego)
                    for v in values:
                        val = v.get("Wartość") if "Wartość" in v else v.get("value")
                        date_str = v.get("Data") if "Data" in v else v.get("date") # np. "2023-10-24 14:00:00"
                        
                        if val is not None and date_str:
                            # Wyciągamy samą godzinę: np. "14:00"
                            hour = date_str.split(" ")[1][:5]
                            
                            # Zapisujemy do historii
                            history.append({"time": hour, "value": round(val, 1)})
                            
                            # Pierwsza znaleziona wartość to nasza "aktualna"
                            if current_val is None:
                                current_val = round(val, 1)
                                
                    # Jeśli mamy dane, pakujemy je w fajny obiekt dla frontendu
                    if current_val is not None and results[code] is None:
                        results[code] = {
                            "current": current_val,
                            "history": history[:12] # Bierzemy maksymalnie 12 ostatnich godzin
                        }
                    
            return results

        except Exception as e:
            print(f"KRYTYCZNY Błąd sensorów: {e}")
            return {"PM2.5": None, "PM10": None}
# import httpx
# import json
# from redis_client import cache

# BASE_URL = "https://api.gios.gov.pl/pjp-api/Rest"

# async def fetch_all_stations():
#     cache_key = "gios_all_stations"
    
#     # 1. Sprawdź, czy mamy dane w Redis
#     cached_data = await cache.get(cache_key)
#     if cached_data:
#         return json.loads(cached_data)
    
#     # 2. Jeśli nie, pobierz z GIOŚ
#     async with httpx.AsyncClient() as client:
#         response = await client.get(f"{BASE_URL}/station/findAll")
#         response.raise_for_status()
#         data = response.json()
        
#         # 3. Zapisz w Redis na 12 godzin (43200 sekund)
#         await cache.set(cache_key, json.dumps(data), ex=43200)
#         return data

# async def fetch_station_index(station_id: int):
#     cache_key = f"gios_index_{station_id}"
    
#     cached_data = await cache.get(cache_key)
#     if cached_data:
#         return json.loads(cached_data)

#     async with httpx.AsyncClient() as client:
#         response = await client.get(f"{BASE_URL}/aqindex/getIndex/{station_id}")
#         response.raise_for_status()
#         data = response.json()
        
#         # Aktualizacje w GIOŚ są co około godzinę, 15 minut (900s) to bezpieczny bufor
#         await cache.set(cache_key, json.dumps(data), ex=900)
#         return data