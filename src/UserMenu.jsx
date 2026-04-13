import { useState } from "react";

export default function UserMenu({ user, setUser }) {
  const [open, setOpen] = useState(false);

  const handleLogin = async () => {
    const username = prompt("Podaj login:");
    const password = prompt("Podaj hasło:");

    const response = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      setUser(data.username);
      localStorage.setItem("username", data.username);
      alert("Zalogowano!");
    } else {
      alert("Błąd logowania");
    }
  };

  const handleRegister = async () => {
    const username = prompt("Wybierz login:");
    const password = prompt("Wybierz hasło:");

    const response = await fetch("http://localhost:8000/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      alert("Konto utworzone!");
    } else {
      alert(data.detail || "Błąd rejestracji");
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("username");
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="bg-gray-800 text-white px-4 py-2 rounded-full"
      >
        ☰
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-48 bg-white shadow-lg rounded-xl p-2">
          
          {!user ? (
            <>
              <button
                onClick={handleLogin}
                className="block w-full text-left p-2 hover:bg-gray-100 rounded"
              >
                🔐 Logowanie
              </button>

              <button
                onClick={handleRegister}
                className="block w-full text-left p-2 hover:bg-gray-100 rounded"
              >
                📝 Rejestracja
              </button>
            </>
          ) : (
            <>
              <button className="block w-full text-left p-2 hover:bg-gray-100 rounded">
                ⭐ Ulubione miasta
              </button>

              <button
                onClick={handleLogout}
                className="block w-full text-left p-2 hover:bg-gray-100 rounded"
              >
                🚪 Wyloguj
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
