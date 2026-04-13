import UserMenu from "./UserMenu";

export default function Navbar({ user, setUser }) {
  return (
    <div className="w-full flex justify-between items-center p-4">
      <h1 className="text-xl font-bold">🌍 Air Monitor</h1>

      <UserMenu user={user} setUser={setUser} />
    </div>
  );
}