import React, { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'

// Naprawa znikających ikonek pinezek w Leaflet w środowisku React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const popularCities = [
  'Łódź', 'Warszawa', 'Kraków', 'Wrocław', 'Poznań', 
  'Gdańsk', 'Katowice', 'Szczecin', 'Lublin', 'Białystok'
]

const getAqiPercentage = aqi => {
  if (aqi <= 20) return 15
  if (aqi <= 40) return 35
  if (aqi <= 75) return 60
  return 90
}

function getStatus(aqi, statusText) {
  if (statusText === 'Bardzo dobry' || statusText === 'Dobry') return { text: statusText, color: 'bg-green-500' }
  if (statusText === 'Umiarkowany' || statusText === 'Dostateczny') return { text: statusText, color: 'bg-yellow-400' }
  if (statusText === 'Zły' || statusText === 'Bardzo zły') return { text: statusText, color: 'bg-red-500' }
  if (aqi <= 50) return { text: 'Dobra', color: 'bg-green-500' }
  if (aqi <= 100) return { text: 'Średnia', color: 'bg-yellow-400' }
  return { text: 'Zła', color: 'bg-red-500' }
}

const getBarColor = (sensorName, value) => {
  let limit1 = 20, limit2 = 50, limit3 = 100;
  if (sensorName.includes('PM2.5')) { limit1 = 15; limit2 = 35; limit3 = 55; }
  else if (sensorName.includes('PM10')) { limit1 = 20; limit2 = 50; limit3 = 80; }
  else if (sensorName.includes('NO2')) { limit1 = 40; limit2 = 100; limit3 = 200; }
  else if (sensorName.includes('O3')) { limit1 = 50; limit2 = 100; limit3 = 130; }
  else if (sensorName.includes('SO2')) { limit1 = 50; limit2 = 100; limit3 = 200; }

  if (value <= limit1) return 'bg-green-400';
  if (value <= limit2) return 'bg-yellow-400';
  if (value <= limit3) return 'bg-orange-500';
  return 'bg-red-600';
};

function App() {
  const [city, setCity] = useState('Łódź')
  const [inputCity, setInputCity] = useState('')
  const [selectedStationId, setSelectedStationId] = useState(null)
  const [data, setData] = useState(null)
  const [dark, setDark] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  
  const [user, setUser] = useState(localStorage.getItem("username") || null)
  const [favorites, setFavorites] = useState([])
  const [authForm, setAuthForm] = useState({ username: '', password: '' })
  
  // Nowe stany dla Rankingu i Mapy
  const [ranking, setRanking] = useState({ best: null, worst: null })
  const [mapStations, setMapStations] = useState([])

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080'

  // 1. Pobieranie danych dla konkretnego miasta
  useEffect(() => {
    setData(null) 
    let url = `${apiUrl}/air-quality?city=${city}`;
    if (selectedStationId) url += `&station_id=${selectedStationId}`;

    fetch(url)
      .then(res => res.ok ? res.json() : null)
      .then(data => { if(data) setData(data) })
      .catch(err => console.error("Błąd API:", err))
  }, [city, selectedStationId])

  // 2. Pobieranie ulubionych
  useEffect(() => {
    if (user) {
      fetch(`${apiUrl}/favorites/${user}`)
        .then(res => res.json())
        .then(data => setFavorites(data || []))
    }
  }, [user])

  // 3. Pobieranie Rankingu
  useEffect(() => {
    fetch(`${apiUrl}/ranking`)
      .then(res => res.json())
      .then(data => setRanking(data))
      .catch(err => console.error("Błąd rankingu:", err));
  }, [apiUrl]);

  // 4. Pobieranie stacji na mapę
  useEffect(() => {
    fetch(`${apiUrl}/map-stations`)
      .then(res => res.json())
      .then(data => setMapStations(data))
      .catch(err => console.error("Błąd mapy:", err));
  }, [apiUrl]);

  const handleCityChange = (newCity) => {
    setSelectedStationId(null); 
    setCity(newCity);
  }

  const handleAuth = async (endpoint) => {
    if (!authForm.username || !authForm.password) return alert("Podaj login i hasło!")
    try {
      const res = await fetch(`${apiUrl}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(authForm)
      });
      const resData = await res.json();
      if (res.ok) {
        setUser(authForm.username);
        localStorage.setItem("username", authForm.username);
        setAuthForm({ username: '', password: '' });
        alert(resData.message);
      } else {
        alert(resData.detail || "Błąd");
      }
    } catch (err) { alert("Błąd serwera"); }
  }

  const handleLogout = () => {
    setUser(null);
    setFavorites([]);
    localStorage.removeItem("username");
    setMenuOpen(false);
  }

  const addToFavorites = async () => {
    if (!user) return alert("Musisz być zalogowany, aby dodać ulubione!");
    if (favorites.includes(data.city)) return alert("Miasto jest już w ulubionych!");

    const res = await fetch(`${apiUrl}/favorites`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: user, city_name: data.city })
    });

    if (res.ok) {
      setFavorites([...favorites, data.city]);
      alert(`Dodano ${data.city} do ulubionych!`);
    }
  }

  const status = data ? getStatus(data.aqi, data.status_text) : null

  return (
    <div className={`${dark ? 'bg-gray-900 text-white' : 'bg-gradient-to-br from-blue-100 to-blue-300'} min-h-screen transition-colors duration-500`}>
      
      {/* NAVBAR */}
      <div className="flex justify-between items-center p-4">
        <h1 className="text-xl font-bold tracking-tight">🌍 Air Monitor</h1>
        <div className="relative">
          <button onClick={() => setMenuOpen(!menuOpen)} className="bg-gray-800 text-white px-5 py-2.5 rounded-full shadow-lg hover:scale-105 transition font-medium">
            {user ? `👤 ${user}` : "☰ Menu"}
          </button>
          
          {menuOpen && (
            <div className="absolute right-0 mt-3 w-64 bg-white text-black rounded-2xl shadow-2xl p-4 z-[999] border border-gray-100">
              {!user ? (
                <div className="flex flex-col gap-3">
                  <p className="font-bold text-sm text-center mb-1">Zaloguj się</p>
                  <input type="text" placeholder="Login" value={authForm.username} onChange={e => setAuthForm({...authForm, username: e.target.value})} className="border p-2 rounded-lg text-sm bg-gray-50 focus:ring-2 focus:ring-blue-400 outline-none" />
                  <input type="password" placeholder="Hasło" value={authForm.password} onChange={e => setAuthForm({...authForm, password: e.target.value})} className="border p-2 rounded-lg text-sm bg-gray-50 focus:ring-2 focus:ring-blue-400 outline-none" />
                  <div className="flex gap-2 mt-1">
                    <button onClick={() => handleAuth('/login')} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-bold transition">Zaloguj</button>
                    <button onClick={() => handleAuth('/register')} className="flex-1 bg-green-500 hover:bg-green-600 text-white py-2 rounded-lg text-sm font-bold transition">Rejestracja</button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="p-2 text-sm font-bold text-gray-500 uppercase tracking-widest border-b mb-2">⭐ Ulubione miasta</div>
                  <div className="max-h-40 overflow-y-auto mb-2">
                    {favorites.length === 0 ? <p className="p-2 text-sm text-gray-400 italic">Brak ulubionych</p> : 
                      favorites.map(fav => (
                        <button key={fav} onClick={() => { handleCityChange(fav); setMenuOpen(false); }} className="block w-full text-left p-2 hover:bg-blue-50 hover:text-blue-600 font-medium rounded-lg transition">{fav}</button>
                      ))
                    }
                  </div>
                  <button onClick={handleLogout} className="w-full bg-red-100 text-red-600 hover:bg-red-500 hover:text-white font-bold py-2 rounded-lg transition">🚪 Wyloguj</button>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* === GŁÓWNY UKŁAD DWUKOLUMNOWY === */}
      {/* Używamy flex-col dla telefonów, xl:flex-row dla dużych ekranów */}
      <div className="max-w-[1400px] mx-auto p-4 lg:p-8 flex flex-col xl:flex-row gap-8 xl:gap-12 items-start justify-center">
        
        {/* LEWA KOLUMNA - Wyszukiwarka, Ranking i Karta Miasta */}
        <div className="flex flex-col items-center w-full xl:w-[500px] shrink-0">
          
          {/* WYSZUKIWANIE */}
          <div className="flex gap-2 mb-6 w-full">
            <input type="text" placeholder="Wpisz miasto..." value={inputCity} onChange={e => setInputCity(e.target.value)} className="flex-1 p-3 rounded-xl border-none shadow-md focus:ring-4 focus:ring-blue-400 text-black outline-none font-medium" />
            <button onClick={() => { if (inputCity) handleCityChange(inputCity); setInputCity(''); }} className="bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-xl font-bold shadow-md transition">Szukaj</button>
          </div>

          {/* DYNAMICZNE STATYSTYKI (RANKING) */}
          <div className="mb-6 w-full flex justify-between gap-4">
            <div className={`flex-1 p-4 rounded-2xl shadow-md border ${dark ? 'bg-gray-800 border-gray-700' : 'bg-white/80 border-white'} flex flex-col items-center text-center backdrop-blur-sm`}>
              <div className="text-2xl mb-1">🌿</div>
              <p className="text-[9px] uppercase font-bold opacity-50 tracking-widest mb-1">Najczystsze (TOP 10)</p>
              <p className="font-black text-base text-green-500 leading-tight">{ranking.best ? ranking.best.name : "..."}</p>
            </div>

            <div className={`flex-1 p-4 rounded-2xl shadow-md border ${dark ? 'bg-gray-800 border-gray-700' : 'bg-white/80 border-white'} flex flex-col items-center text-center backdrop-blur-sm`}>
              <div className="text-2xl mb-1">😷</div>
              <p className="text-[9px] uppercase font-bold opacity-50 tracking-widest mb-1">Najgorsze (TOP 10)</p>
              <p className="font-black text-base text-red-500 leading-tight">{ranking.worst ? ranking.worst.name : "..."}</p>
            </div>
          </div>

          {/* POPULARNE */}
          <div className="mb-8 w-full">
            <div className="flex flex-wrap justify-center gap-2">
              {popularCities.map(cityName => (
                <button key={cityName} onClick={() => handleCityChange(cityName)} 
                  className={`px-4 py-1.5 rounded-full text-[11px] font-bold transition shadow-sm ${city === cityName ? 'bg-blue-600 text-white scale-105 shadow-md' : 'bg-white/70 text-gray-700 hover:bg-white backdrop-blur-md'}`}>
                  {cityName}
                </button>
              ))}
            </div>
          </div>

          {/* KARTA GŁÓWNA Z DANYMI MIASTA */}
          <div className={`p-8 rounded-3xl shadow-2xl w-full max-w-[420px] text-center transition-all ${dark ? 'bg-gray-800 border-gray-700' : 'bg-white border-white'} border`}>
            {!data ? (
              <div className="py-12 flex flex-col items-center">
                <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
                <p className="text-gray-400 font-medium animate-pulse">Ładowanie danych z GIOŚ...</p>
              </div>
            ) : (
              <>
                <h2 className="text-4xl font-black mb-1">{data.city}</h2>
                {data.nearest_info && <p className="text-[10px] text-orange-500 italic mb-3 px-2 font-medium">{data.nearest_info}</p>}
                
                {data.available_stations && data.available_stations.length > 1 ? (
                  <div className="mb-5">
                    <select 
                      value={data.station_id || ""} 
                      onChange={(e) => setSelectedStationId(e.target.value)}
                      className="text-[10px] p-2.5 rounded-xl border bg-white text-black border-gray-200 dark:bg-gray-700 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-black dark:focus:ring-white outline-none w-full max-w-[300px] mx-auto block text-center uppercase tracking-widest cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition font-bold"
                    >
                      {data.available_stations.map(st => (
                        <option key={st.id} value={st.id}>{st.name}</option>
                      ))}
                    </select>
                  </div>
                ) : (
                  <p className="text-[10px] text-gray-400 mb-5 uppercase tracking-widest font-bold">Stacja: {data.station_name}</p>
                )}

                <div className="mb-8">
                  <span className={`${status.color} text-white px-8 py-2 rounded-full shadow-lg font-black tracking-wide`}>
                    {data.status_text || status.text}
                  </span>
                </div>

                {/* SKALA WIZUALNA */}
                <div className="mt-4 mb-8 px-2">
                  <div className="flex justify-between text-[10px] mb-2 opacity-50 uppercase font-black tracking-widest">
                    <span>Czysto</span>
                    <span>Smog</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-4 dark:bg-gray-700 overflow-hidden p-[3px] shadow-inner">
                    <div
                      className={`h-full rounded-full transition-all duration-1000 ${status.color} shadow-sm`}
                      style={{ width: `${getAqiPercentage(data.aqi)}%` }}></div>
                  </div>
                </div>

                {/* DYNAMICZNE KAFELKI Z LICZBAMI I WYKRESAMI */}
                <div className="grid grid-cols-2 gap-4 mb-8">
                  {data.sensors && Object.entries(data.sensors).map(([sensorName, sensorData]) => {
                    if (!sensorData || !sensorData.history || sensorData.history.length === 0) return null;

                    const maxVal = Math.max(...sensorData.history.map(h => h.value));
                    const reversedHistory = sensorData.history.slice().reverse();
                    
                    const firstTime = reversedHistory[0]?.time;
                    const midTime = reversedHistory.length > 5 ? reversedHistory[Math.floor(reversedHistory.length / 2)]?.time : "";

                    return (
                      <div key={sensorName} className={`${dark ? 'bg-gray-700/60' : 'bg-white'} p-4 rounded-3xl border ${dark ? 'border-gray-600' : 'border-blue-50'} shadow-lg hover:scale-105 transition-transform flex flex-col justify-between`}>
                        
                        <div className="flex justify-between items-start mb-2">
                          <p className="text-xs uppercase opacity-50 font-bold tracking-widest">{sensorName}</p>
                          <div className="text-right">
                            <p className="text-2xl font-black">
                              {sensorData.current > 10 ? Math.round(sensorData.current) : sensorData.current.toFixed(1)}
                            </p>
                            <p className="text-[9px] opacity-40 uppercase font-bold">µg/m³</p>
                          </div>
                        </div>

                        <div className="flex items-end h-14 gap-[2px] mt-2 opacity-90 hover:opacity-100 transition-opacity">
                          {reversedHistory.map((h, i) => {
                            const heightPct = Math.max((h.value / maxVal) * 100, 5); 
                            const barColor = getBarColor(sensorName, h.value);

                            return (
                              <div 
                                key={i} 
                                className={`flex-1 ${barColor} rounded-t-sm transition-all duration-500`} 
                                style={{ height: `${heightPct}%` }}
                                title={`${h.time} -> ${h.value} µg/m³`} 
                              ></div>
                            );
                          })}
                        </div>
                        
                        <div className="flex justify-between mt-2 text-[8px] opacity-40 font-bold tracking-tighter">
                          <span>{firstTime}</span>
                          <span>{midTime}</span>
                          <span>TERAZ</span>
                        </div>
                        
                      </div>
                    );
                  })}
                </div>

                <button 
                  onClick={addToFavorites} 
                  className="w-full bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-yellow-900 font-black py-3.5 rounded-xl transition-all active:scale-95 shadow-md flex justify-center items-center gap-2"
                >
                  ⭐ Dodaj do ulubionych
                </button>

                <p className="text-[10px] opacity-40 mt-5 font-medium tracking-widest uppercase">Aktualizacja: {data.timestamp}</p>
              </>
            )}
          </div>
        </div>

        {/* PRAWA KOLUMNA - Mapa Leaflet */}
        {/* Na dużych ekranach (xl) zajmie resztę miejsca i przypnie się do ekranu (sticky) */}
        <div className="w-full xl:flex-1 h-[600px] xl:h-[800px] xl:sticky xl:top-8 z-0">
          <div className={`w-full h-full rounded-3xl shadow-2xl overflow-hidden border ${dark ? 'border-gray-700 bg-gray-800' : 'border-white bg-white'}`}>
            
            <div className="p-4 bg-white/50 dark:bg-gray-800/50 backdrop-blur-md absolute top-0 left-0 right-0 z-[400] pointer-events-none">
              <h3 className="text-sm font-black text-center opacity-80 uppercase tracking-widest drop-shadow-md">Mapa Stacji Pomiarowych w Polsce</h3>
            </div>

            <MapContainer center={[52.06, 19.25]} zoom={6} scrollWheelZoom={true} style={{ height: "100%", width: "100%", zIndex: 0 }}>
              <TileLayer
                attribution='&copy; OpenStreetMap'
                url={dark ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}
              />
              
              {mapStations.map((station) => (
                <Marker key={station.id} position={[station.lat, station.lon]}>
                  <Popup>
                    <div className="text-center p-1">
                      <p className="font-bold text-gray-800 mb-1 text-sm">{station.city}</p>
                      <p className="text-[10px] text-gray-500 mb-3">{station.name}</p>
                      <button 
                        onClick={() => {
                          setCity(station.city);
                          setSelectedStationId(station.id);
                          window.scrollTo({ top: 0, behavior: 'smooth' });
                        }}
                        className="bg-blue-600 text-white text-xs px-4 py-1.5 rounded-lg shadow hover:bg-blue-700 transition font-bold"
                      >
                        Sprawdź wyniki
                      </button>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>

          </div>
        </div>

      </div>

      {/* Przełącznik Dark Mode */}
      <button onClick={() => setDark(!dark)} className="fixed bottom-6 right-6 bg-white dark:bg-gray-800 p-4 rounded-full shadow-2xl text-2xl hover:scale-110 transition z-50 border dark:border-gray-700">
        {dark ? '☀️' : '🌙'}
      </button>
    </div>
  )
}

export default App