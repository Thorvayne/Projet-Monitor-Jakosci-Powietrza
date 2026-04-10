import { useState } from "react";

export default function UserMenu({ user, setUser }) {
  const [open, setOpen] = useState(false);

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
                onClick={() => setUser("user")}
                className="block w-full text-left p-2 hover:bg-gray-100 rounded"
              >
                🔐 Logowanie
              </button>

              <button
                onClick={() => setUser("user")}
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
                onClick={() => setUser(null)}
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