import { useState, useEffect } from "react";
import Login from "./Login";
import SmartStationDashboard from "./SmartStationDashboard";

export default function App() {
  const [usuario, setUsuario] = useState(null);

  useEffect(() => {
    try {
      const saved = sessionStorage.getItem("ss_user");
      if (saved) setUsuario(JSON.parse(saved));
    } catch (_) {}
  }, []);

  function handleLogin(user) {
    sessionStorage.setItem("ss_user", JSON.stringify(user));
    setUsuario(user);
  }

  function handleLogout() {
    sessionStorage.removeItem("ss_user");
    setUsuario(null);
  }

  if (!usuario) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <SmartStationDashboard
      usuarioLogado={usuario}
      onLogout={handleLogout}
    />
  );
}