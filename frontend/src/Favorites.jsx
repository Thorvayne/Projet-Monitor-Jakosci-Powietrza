import { useEffect, useState } from "react";

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);

  const username = localStorage.getItem("username");

  const loadFavorites = async () => {
    if (!username) return;

    const res = await fetch(`http://localhost:8000/favorites/${username}`);
    const data = await res.json();

    setFavorites(data);
  };

  const removeFavorite = async (city) => {
    await fetch("http://localhost:8000/favorites", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        city_name: city,
      }),
    });

    loadFavorites();
  };

  useEffect(() => {
    loadFavorites();
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">⭐ Ulubione miasta</h2>

      {favorites.length === 0 ? (
        <p>Brak ulubionych miast</p>
      ) : (
        favorites.map((city) => (
          <div
            key={city}
            className="flex justify-between items-center bg-gray-100 p-2 mb-2 rounded"
          >
            <span>{city}</span>

            <button
              onClick={() => removeFavorite(city)}
              className="text-red-500"
            >
              ❌
            </button>
          </div>
        ))
      )}
    </div>
  );
}