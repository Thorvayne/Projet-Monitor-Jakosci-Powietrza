import httpx


BASE_URL = "https://api.gios.gov.pl/pjp-api/v1/rest"

async def fetch_all_stations():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/station/findAll")
        response.raise_for_status()
        return response.json()

async def fetch_station_index(station_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/aqindex/getIndex/{station_id}")
        response.raise_for_status()
        return response.json()

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