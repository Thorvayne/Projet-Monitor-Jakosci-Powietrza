import React, { useEffect, useState } from "react";

const popularCities = [
  "Łódź",
  "Warszawa",
  "Kraków",
  "Wrocław",
  "Poznań",
  "Gdańsk",
  "Katowice",
  "Szczecin",
  "Lublin",
  "Białystok"
];

function getStatus(aqi) {
  if (aqi <= 50) return { text: "Dobra", color: "bg-green-500" };
  if (aqi <= 100) return { text: "Średnia", color: "bg-yellow-400" };
  return { text: "Zła", color: "bg-red-500" };
}

function App() {
  const [city, setCity] = useState("Lodz");
  const [inputCity, setInputCity] = useState("");
  const [data, setData] = useState(null);
  const [dark, setDark] = useState(false);

  useEffect(() => {
    fetch(`http://localhost:8000/air-quality?city=${city}`)
      .then(res => res.json())
      .then(data => setData(data))
      .catch(err => console.error(err));
  }, [city]);

  const status = data ? getStatus(data.aqi || 80) : null;

  return (
    <div className={`${dark ? "bg-gray-900 text-white" : "bg-gradient-to-br from-blue-100 to-blue-300"} min-h-screen flex flex-col items-center p-6`}>

      {/* Tytuł */}
      <h1 className="text-3xl font-bold mb-6">
        🌍 Monitor jakości powietrza
      </h1>

      {/* POPULARNE WYSZUKIWANIA */}
      <div className="mb-4 text-center">
        <p className={`${dark ? "text-gray-300" : "text-gray-600"} text-sm mb-2`}>
          Popularne wyszukiwania:
        </p>

        <div className="flex flex-wrap justify-center gap-2">
          {popularCities.map((cityName) => (
            <button
              key={cityName}
              onClick={() => setCity(cityName)}
              className={`px-3 py-1 rounded-full text-sm transition ${
                city === cityName
                  ? "bg-blue-500 text-white"
                  : dark
                  ? "bg-gray-700 text-white hover:bg-gray-600"
                  : "bg-white shadow hover:bg-blue-100"
              }`}
            >
              {cityName}
            </button>
          ))}
        </div>
      </div>

      {/* WYSZUKIWANIE */}
      <div className="flex gap-2 mb-6">
        <input
          type="text"
          placeholder="Wpisz miasto..."
          value={inputCity}
          onChange={(e) => setInputCity(e.target.value)}
          className="p-2 rounded-lg border"
        />

        <button
          onClick={() => {
            if (!inputCity) return alert("Wpisz miasto");
            setCity(inputCity);
          }}
          className="bg-blue-500 text-white px-4 rounded-lg"
        >
          Szukaj miasto
        </button>
      </div>

      {/* KARTA */}
      <div className={`p-6 rounded-3xl shadow-xl w-[350px] text-center ${dark ? "bg-gray-800" : "bg-white"}`}>
        
        {!data ? (
          <p className="animate-pulse text-gray-400">Ładowanie danych...</p>
        ) : (
          <>
            <h2 className="text-xl font-semibold mb-2">{data.city}</h2>

            <div className="mb-3">
              <span className={`${status.color} text-white px-4 py-1 rounded-full`}>
                {status.text}
              </span>
            </div>

            <p className="text-lg">PM2.5: <b>{data.pm25}</b></p>
            <p className="text-lg">PM10: <b>{data.pm10}</b></p>

            <p className="text-sm opacity-70 mt-3">{data.timestamp}</p>
          </>
        )}
      </div>

      {/* DARK MODE */}
      <button
        onClick={() => setDark(!dark)}
        className="fixed bottom-5 right-5 bg-black text-white px-4 py-2 rounded-full"
      >
        {dark ? "☀️" : "🌙"}
      </button>

    </div>
  );
}

export default App;