import { useState } from "react";

const css = `
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #0a0c0f;
  --surface: #111318;
  --surface2: #181b22;
  --border: #1e2330;
  --border2: #2a3044;
  --text: #e8eaf0;
  --t2: #8b92a8;
  --t3: #4a5068;
  --green: #22c55e;
  --green-dim: rgba(34,197,94,.12);
  --green-glow: rgba(34,197,94,.25);
  --amber: #f59e0b;
  --red: #ef4444;
  --red-dim: rgba(239,68,68,.12);
  --accent: #3b82f6;
  --accent-dim: rgba(59,130,246,.12);
  --sans: 'Space Grotesk', sans-serif;
  --mono: 'JetBrains Mono', monospace;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  min-height: 100vh;
  overflow: hidden;
}

.login-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: var(--bg);
  overflow: hidden;
}

.grid-lines {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(59,130,246,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,.04) 1px, transparent 1px);
  background-size: 48px 48px;
  animation: grid-drift 20s linear infinite;
}
@keyframes grid-drift {
  0% { transform: translate(0,0); }
  100% { transform: translate(48px,48px); }
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  animation: orb-float 8s ease-in-out infinite alternate;
}
.orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(34,197,94,.08) 0%, transparent 70%);
  top: -100px; left: -100px;
  animation-duration: 11s;
}
.orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(59,130,246,.07) 0%, transparent 70%);
  bottom: -80px; right: -80px;
  animation-duration: 9s;
  animation-delay: -4s;
}
.orb-3 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(245,158,11,.05) 0%, transparent 70%);
  top: 40%; left: 60%;
  animation-duration: 13s;
  animation-delay: -7s;
}
@keyframes orb-float {
  0% { transform: scale(1) translate(0,0); }
  100% { transform: scale(1.15) translate(20px,-20px); }
}

.particle {
  position: absolute;
  width: 2px; height: 2px;
  background: var(--green);
  border-radius: 50%;
  opacity: 0;
  animation: particle-blink 4s ease-in-out infinite;
}
@keyframes particle-blink {
  0%,100% { opacity: 0; }
  50% { opacity: .5; }
}

.login-wrapper {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 40px 36px 36px;
  position: relative;
  overflow: hidden;
  box-shadow:
    0 0 0 1px var(--border),
    0 24px 64px rgba(0,0,0,.6),
    0 0 80px rgba(34,197,94,.04);
  animation: card-in .5s cubic-bezier(.16,1,.3,1) both;
}
@keyframes card-in {
  from { opacity: 0; transform: translateY(24px) scale(.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.card-topline {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--green), transparent);
  opacity: .6;
}

.login-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}
.logo-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: var(--green-dim);
  border: 1px solid rgba(34,197,94,.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
  position: relative;
}
.logo-icon::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 16px;
  border: 1px solid rgba(34,197,94,.12);
}
.logo-name {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -.3px;
  color: var(--text);
}
.logo-tag {
  font-size: 10px;
  font-family: var(--mono);
  color: var(--green);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-top: 1px;
}

.login-heading {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -.4px;
  color: var(--text);
  margin-bottom: 4px;
}
.login-sub {
  font-size: 13px;
  color: var(--t2);
  margin-bottom: 28px;
  line-height: 1.5;
}

.login-form { display: flex; flex-direction: column; gap: 16px; }

.field { display: flex; flex-direction: column; gap: 6px; }

.field-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--t2);
  display: flex;
  align-items: center;
  gap: 6px;
}
.field-label-icon { font-size: 12px; }

.field-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.field-input {
  width: 100%;
  padding: 12px 14px 12px 42px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  font-family: var(--mono);
  font-size: 14px;
  color: var(--text);
  outline: none;
  transition: border-color .2s, box-shadow .2s, background .2s;
  letter-spacing: .5px;
}
.field-input::placeholder { color: var(--t3); letter-spacing: 0; font-family: var(--sans); }
.field-input:focus {
  border-color: var(--green);
  background: #131a14;
  box-shadow: 0 0 0 3px var(--green-dim), 0 0 16px var(--green-glow);
}
.field-input.error {
  border-color: var(--red);
  background: #1a1212;
  box-shadow: 0 0 0 3px var(--red-dim);
}

.field-icon {
  position: absolute;
  left: 14px;
  font-size: 15px;
  pointer-events: none;
  color: var(--t3);
  transition: color .2s;
}
.field-wrap:focus-within .field-icon { color: var(--green); }

.toggle-pass {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: var(--t3);
  padding: 4px;
  transition: color .2s;
  line-height: 1;
}
.toggle-pass:hover { color: var(--t2); }

.field-hint {
  font-size: 10px;
  color: var(--t3);
  font-family: var(--mono);
  letter-spacing: .5px;
}

.erro-msg {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--red-dim);
  border: 1px solid rgba(239,68,68,.2);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 12px;
  color: #fca5a5;
  font-weight: 500;
  animation: shake .4s cubic-bezier(.36,.07,.19,.97);
}
@keyframes shake {
  10%,90% { transform: translateX(-2px); }
  20%,80% { transform: translateX(3px); }
  30%,50%,70% { transform: translateX(-3px); }
  40%,60% { transform: translateX(3px); }
}

.btn-login {
  margin-top: 4px;
  width: 100%;
  padding: 14px;
  background: var(--green);
  border: none;
  border-radius: 10px;
  font-family: var(--sans);
  font-size: 14px;
  font-weight: 700;
  color: #0a1a0e;
  cursor: pointer;
  transition: all .2s;
  letter-spacing: .3px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}
.btn-login::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,.15) 0%, transparent 60%);
  pointer-events: none;
}
.btn-login:hover:not(:disabled) {
  background: #16a34a;
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(34,197,94,.3);
}
.btn-login:active:not(:disabled) { transform: translateY(0); }
.btn-login:disabled { opacity: .6; cursor: not-allowed; }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(10,26,14,.3);
  border-top-color: #0a1a0e;
  border-radius: 50%;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.login-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 4px 0;
}
.divider-line { flex: 1; height: 1px; background: var(--border); }
.divider-text { font-size: 10px; color: var(--t3); font-family: var(--mono); letter-spacing: 1px; }

.roles-info { display: flex; gap: 8px; }
.role-badge {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  text-align: center;
  transition: border-color .2s;
}
.role-badge:hover { border-color: var(--border2); }
.role-icon { font-size: 18px; margin-bottom: 4px; }
.role-name { font-size: 11px; font-weight: 700; color: var(--t2); letter-spacing: .5px; display: block; }
.role-desc { font-size: 9px; color: var(--t3); font-family: var(--mono); margin-top: 2px; display: block; }

.card-footer {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-footer-text { font-size: 10px; color: var(--t3); font-family: var(--mono); }
.status-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-family: var(--mono);
  color: var(--green);
}
.status-dot-sm {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--green);
  animation: blink 1.5s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

@media (max-width: 480px) {
  .login-card { padding: 28px 20px 24px; border-radius: 16px; }
  .roles-info { flex-direction: column; }
}
`;

const PARTICLES = Array.from({ length: 12 }, (_, i) => ({
  top: `${10 + Math.floor(Math.sin(i * 1.7) * 40 + 40)}%`,
  left: `${10 + Math.floor(Math.cos(i * 1.3) * 40 + 40)}%`,
  delay: `${(i * 0.7).toFixed(1)}s`,
  duration: `${3 + (i % 4)}s`,
}));

export default function Login({ onLogin }) {
  const [matricula, setMatricula] = useState("");
  const [senha, setSenha] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [erro, setErro] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");

    if (!matricula.trim() || !senha.trim()) {
      setErro("Preencha a matrícula e a senha.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8080/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          matricula: Number(matricula.trim()),
          senha: senha.trim(),
        }),
      });

      if (res.status === 401) {
        setErro("Matrícula ou senha incorretos.");
        return;
      }

      if (res.status === 403) {
        const msg = await res.text();
        setErro(
          msg.toLowerCase().includes("inativo")
            ? "Funcionário inativo. Contate o administrador."
            : "Acesso negado para este perfil."
        );
        return;
      }

      if (res.status === 400) {
        setErro("Matrícula e senha são obrigatórias.");
        return;
      }

      if (!res.ok) {
        setErro("Erro ao conectar com o servidor. Verifique se o backend está rodando.");
        return;
      }

      const usuario = await res.json();

      onLogin({
        id: usuario.id,
        nome: usuario.nome,
        matricula: usuario.matricula,
        cargo: usuario.cargo,
        isAdmin: usuario.cargo === "ADMIN",
      });

    } catch (err) {
      setErro("Erro de conexão com o backend: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <style>{css}</style>

      <div className="login-bg">
        <div className="grid-lines" />
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
        {PARTICLES.map((p, i) => (
          <div
            key={i}
            className="particle"
            style={{
              top: p.top,
              left: p.left,
              animationDelay: p.delay,
              animationDuration: p.duration,
            }}
          />
        ))}
      </div>

      <div className="login-wrapper">
        <div className="login-card">
          <div className="card-topline" />

          <div className="login-logo">
            <div className="logo-icon">📦</div>
            <div className="logo-texts">
              <div className="logo-name">SmartStation</div>
              <div className="logo-tag">Sistema de Monitoramento</div>
            </div>
          </div>

          <div className="login-heading">Acesso ao Sistema</div>
          <div className="login-sub">
            Entre com sua matrícula e senha para acessar o painel.
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="field">
              <label className="field-label">
                <span className="field-label-icon">🪪</span>
                Matrícula (RA)
              </label>
              <div className="field-wrap">
                <span className="field-icon">🔢</span>
                <input
                  className={`field-input${erro ? " error" : ""}`}
                  type="text"
                  placeholder="000000"
                  value={matricula}
                  onChange={(e) => { setMatricula(e.target.value); setErro(""); }}
                  autoComplete="username"
                  autoFocus
                />
              </div>
            </div>

            <div className="field">
              <label className="field-label">
                <span className="field-label-icon">🔒</span>
                Senha
              </label>
              <div className="field-wrap">
                <span className="field-icon">🗝️</span>
                <input
                  className={`field-input${erro ? " error" : ""}`}
                  type={showPass ? "text" : "password"}
                  placeholder="••••••••"
                  value={senha}
                  onChange={(e) => { setSenha(e.target.value); setErro(""); }}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="toggle-pass"
                  onClick={() => setShowPass(!showPass)}
                  tabIndex={-1}
                >
                  👁️
                </button>
              </div>
              <span className="field-hint">Padrão: smart + matrícula &nbsp;·&nbsp; ADM também aceita: admin123</span>
            </div>

            {erro && (
              <div className="erro-msg">
                <span>⚠️</span>
                {erro}
              </div>
            )}

            <button className="btn-login" type="submit" disabled={loading}>
              {loading
                ? <><div className="spinner" /> Verificando...</>
                : <><span>→</span> Entrar no Sistema</>
              }
            </button>
          </form>

          <div className="login-divider" style={{ marginTop: 20 }}>
            <div className="divider-line" />
            <div className="divider-text">NÍVEIS DE ACESSO</div>
            <div className="divider-line" />
          </div>

          <div className="roles-info">
            <div className="role-badge">
              <div className="role-icon">👑</div>
              <span className="role-name">ADM</span>
              <span className="role-desc">Acesso total</span>
            </div>
            <div className="role-badge">
              <div className="role-icon">👷</div>
              <span className="role-name">FUNCIONÁRIO</span>
              <span className="role-desc">Apenas seu perfil</span>
            </div>
          </div>

          <div className="card-footer">
            <span className="card-footer-text">SmartStation v1.0</span>
            <div className="status-pill">
              <div className="status-dot-sm" />
              Sistema Operacional
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
