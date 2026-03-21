import { useState, useEffect, useRef } from "react";

const API_BASE = "http://localhost:8080/api";

// ─── UTILS ──────────────────────────────────────────────────────────────────
function formatDuration(ms) {
  if (ms == null || ms < 0) return "00:00:00";
  const s = Math.floor(ms / 1000);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return [h, m, sec].map((v) => String(v).padStart(2, "0")).join(":");
}
function formatTime(iso) {
  if (!iso) return "--:--:--";
  return new Date(iso).toLocaleTimeString("pt-BR", { hour12: false });
}
function formatDate(iso) {
  if (!iso) return "--";
  return new Date(iso).toLocaleDateString("pt-BR");
}

// ─── MOCK FUNCIONÁRIOS ───────────────────────────────────────────────────────
const MOCK_FUNCIONARIOS = [
  {
    id: 1,
    nome: "Henrique Falasco",
    matricula: 842798431,
    cargo: "FUNCIONARIO",
    ativo: true,
    avatar: "HO",
    cor: "#16a34a",
    corBg: "#dcfce7",
  },
  {
    id: 2,
    nome: "Joao Filipe Betin",
    matricula: 759204816,
    cargo: "ADMIN",
    ativo: true,
    avatar: "BC",
    cor: "#2563eb",
    corBg: "#dbeafe",
  },
  {
    id: 3,
    nome: "Rafael Guerino",
    matricula: 631047529,
    cargo: "FUNCIONARIO",
    ativo: false,
    avatar: "RM",
    cor: "#94a3b8",
    corBg: "#f1f5f9",
  },
];

// ─── MOCK SESSIONS por funcionário ──────────────────────────────────────────
function generateMockSessions(seed = 0) {
  const now = Date.now();
  const sessions = [];
  let cursor = now - 8 * 3600 * 1000;
  const count = 15 + seed * 4;
  for (let i = 0; i < count; i++) {
    const entrou = cursor + Math.random() * 30000;
    const dur = 25000 + Math.random() * 110000;
    const saiu = entrou + dur;
    const idle = i === 0 ? 0 : 8000 + Math.random() * 80000;
    sessions.push({
      id: i + 1,
      entryTime: new Date(entrou).toISOString(),
      exitTime: new Date(saiu).toISOString(),
      processingDuration: Math.round(dur),
      idleBefore: Math.round(idle),
    });
    cursor = saiu + idle;
  }
  return sessions;
}

const SESSIONS_BY_FUNC = {
  1: generateMockSessions(0),
  2: generateMockSessions(1),
  3: generateMockSessions(2),
};

// ─── SPARKLINE ───────────────────────────────────────────────────────────────
function Sparkline({ data, color, width = 120, height = 36 }) {
  if (!data || data.length < 2) return null;
  const max = Math.max(...data, 1);
  const min = Math.min(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((v - min) / range) * (height - 4) - 2;
    return `${x},${y}`;
  });
  const id = `sg${color.replace(/[^a-z0-9]/gi, "")}`;
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.18" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polyline points={`0,${height} ${pts.join(" ")} ${width},${height}`} fill={`url(#${id})`} stroke="none" />
      <polyline points={pts.join(" ")} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ─── ACTIVITY CHART ──────────────────────────────────────────────────────────
function ActivityChart({ sessions }) {
  if (!sessions.length) return <div style={{ color: "#94a3b8", textAlign: "center", padding: 40, fontSize: 13 }}>Sem dados de atividade</div>;
  const W = 800, H = 130;
  const first = new Date(sessions[0].entryTime).getTime();
  const lastExit = sessions[sessions.length - 1].exitTime
    ? new Date(sessions[sessions.length - 1].exitTime).getTime()
    : Date.now();
  const span = lastExit - first || 1;

  const segs = [];
  sessions.forEach((s) => {
    const e = new Date(s.entryTime).getTime();
    const x = new Date(s.exitTime || Date.now()).getTime();
    if (s.idleBefore > 0) {
      segs.push({ type: "idle", start: (e - s.idleBefore - first) / span, width: s.idleBefore / span });
    }
    segs.push({ type: "active", start: (e - first) / span, width: (x - e) / span });
  });

  const hours = [];
  for (let t = first; t < lastExit; t += 3600000) {
    hours.push({ x: ((t - first) / span) * W, label: new Date(t).getHours() + ":00" });
  }

  const maxIdle = Math.max(...sessions.map(s => s.idleBefore || 0), 1);

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: "block", overflow: "visible" }}>
      {[0, 0.25, 0.5, 0.75, 1].map(v => (
        <line key={v} x1={v * W} y1={0} x2={v * W} y2={H - 22} stroke="#e2e8f0" strokeWidth="1" />
      ))}
      {sessions.map((s, i) => {
        const e = new Date(s.entryTime).getTime();
        const exit = new Date(s.exitTime || Date.now()).getTime();
        const x1 = ((e - first) / span) * W;
        const bw = Math.max(((exit - e) / span) * W, 2);
        const bh = ((s.idleBefore || 0) / maxIdle) * 50;
        return <rect key={i} x={x1} y={H - 22 - bh} width={bw * 0.65} height={bh} fill="#f59e0b" opacity="0.2" rx="2" />;
      })}
      {segs.map((seg, i) => (
        <rect key={i} x={seg.start * W} y={seg.type === "active" ? 28 : 52}
          width={Math.max(seg.width * W, 2)} height={seg.type === "active" ? 32 : 14}
          fill={seg.type === "active" ? "#16a34a" : "#f59e0b"}
          opacity={seg.type === "active" ? 0.8 : 0.55} rx={4} />
      ))}
      {hours.map((h, i) => (
        <text key={i} x={h.x} y={H - 5} fontSize={9} fill="#94a3b8" textAnchor="middle" fontFamily="DM Mono,monospace">{h.label}</text>
      ))}
      <rect x={0} y={8} width={10} height={10} fill="#16a34a" rx={2} />
      <text x={14} y={17} fontSize={9} fill="#64748b" fontFamily="DM Sans,sans-serif">Processando caixa</text>
      <rect x={110} y={8} width={10} height={10} fill="#f59e0b" rx={2} />
      <text x={124} y={17} fontSize={9} fill="#64748b" fontFamily="DM Sans,sans-serif">Ociosidade</text>
    </svg>
  );
}

// ─── STYLES ──────────────────────────────────────────────────────────────────
const css = `
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f0f4f8;--surface:#fff;--border:#e2e8f0;--border2:#cbd5e1;
  --text:#1e293b;--t2:#475569;--t3:#94a3b8;
  --green:#16a34a;--gl:#dcfce7;--gm:#86efac;
  --amber:#d97706;--al:#fef3c7;
  --red:#dc2626;--rl:#fee2e2;
  --blue:#2563eb;--bl:#dbeafe;
  --sw:220px;--sans:'DM Sans',sans-serif;--mono:'DM Mono',monospace;
}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh}
.layout{display:flex;min-height:100vh}

.sidebar{width:var(--sw);flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;position:fixed;top:0;left:0;bottom:0;z-index:10}
.sidebar-logo{padding:20px 18px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px}
.logo-box{width:32px;height:32px;border-radius:8px;background:var(--green);display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.logo-name{font-size:15px;font-weight:700;letter-spacing:-0.3px}
.logo-ver{font-size:10px;color:var(--t3);font-family:var(--mono)}
.sb-sec{padding:14px 10px 2px}
.sb-sec-label{font-size:10px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--t3);padding:0 8px;margin-bottom:4px}
.nav-btn{display:flex;align-items:center;gap:9px;padding:9px 10px;border-radius:8px;font-size:13px;font-weight:500;color:var(--t2);cursor:pointer;transition:all .15s;margin-bottom:2px;border:none;background:none;width:100%;text-align:left;font-family:var(--sans)}
.nav-btn:hover{background:var(--bg);color:var(--text)}
.nav-btn.active{background:var(--gl);color:var(--green);font-weight:600}
.nav-icon{font-size:15px;width:20px;text-align:center;flex-shrink:0}
.sb-bot{margin-top:auto;padding:14px 10px;border-top:1px solid var(--border)}
.st-pill{display:flex;align-items:center;gap:8px;background:var(--bg);border-radius:8px;padding:10px 12px}
.st-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.st-dot.on{background:var(--green);box-shadow:0 0 0 3px rgba(22,163,74,.2);animation:blink 1.5s infinite}
.st-dot.off{background:var(--amber);box-shadow:0 0 0 3px rgba(217,119,6,.2);animation:blink 1.5s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.35}}
.st-txt{font-size:12px;font-weight:600}
.st-sub{font-size:10px;color:var(--t3);font-family:var(--mono)}

.main{margin-left:var(--sw);flex:1;display:flex;flex-direction:column}
.topbar{background:var(--surface);border-bottom:1px solid var(--border);padding:14px 26px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:5}
.tb-title{font-size:16px;font-weight:700}
.tb-sub{font-size:12px;color:var(--t3);margin-top:1px}
.tb-right{display:flex;align-items:center;gap:10px}
.clock{font-family:var(--mono);font-size:13px;background:var(--bg);border:1px solid var(--border);padding:6px 12px;border-radius:6px;color:var(--t2)}
.demo-tag{font-size:11px;font-weight:600;letter-spacing:1px;background:var(--al);color:var(--amber);border:1px solid #fde68a;border-radius:5px;padding:4px 10px}
.back-btn{display:flex;align-items:center;gap:6px;font-size:12px;font-weight:600;color:var(--t2);background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:6px 12px;cursor:pointer;transition:all .15s;font-family:var(--sans)}
.back-btn:hover{background:var(--surface);color:var(--text);border-color:var(--border2)}

.content{padding:22px 26px}

.banner{border-radius:12px;padding:20px 22px;display:flex;align-items:center;gap:18px;margin-bottom:18px;border:1px solid;transition:all .4s}
.banner.on{background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-color:#86efac}
.banner.off{background:linear-gradient(135deg,#fffbeb,#fef3c7);border-color:#fde68a}
.ban-icon{font-size:30px}
.ban-lbl{font-size:10px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--t3)}
.ban-st{font-size:16px;font-weight:700;margin:2px 0 4px}
.ban-st.on{color:var(--green)}.ban-st.off{color:var(--amber)}
.ban-timer{font-family:var(--mono);font-size:36px;font-weight:500;color:var(--text)}
.ban-div{width:1px;height:58px;background:var(--border2);margin:0 6px}
.ban-ev{}
.ban-ev-lbl{font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--t3);margin-bottom:3px}
.ban-ev-time{font-family:var(--mono);font-size:22px;color:var(--text)}
.ban-ev-date{font-size:11px;color:var(--t3);margin-top:2px}

.kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:18px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:22px 20px}
.kpi-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px}
.kpi-lbl{font-size:12px;font-weight:500;color:var(--t2)}
.kpi-ico{width:30px;height:30px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px}
.kpi-val{font-family:var(--mono);font-size:38px;font-weight:500;color:var(--text);line-height:1}
.kpi-sub{font-size:11px;color:var(--t3);margin-top:3px}
.kpi-spark{margin-top:8px}
.kpi-trend{display:inline-flex;align-items:center;gap:3px;font-size:11px;font-weight:600;margin-top:5px;padding:2px 7px;border-radius:20px}
.tu{background:var(--gl);color:var(--green)}.td2{background:var(--rl);color:var(--red)}.tw{background:var(--al);color:var(--amber)}
.eff-wrap{background:var(--bg);border-radius:20px;height:7px;overflow:hidden;margin-top:7px}
.eff-fill{height:100%;border-radius:20px;transition:width 1.2s cubic-bezier(.4,0,.2,1)}

.sec{background:var(--surface);border:1px solid var(--border);border-radius:12px;margin-bottom:18px;overflow:hidden}
.sec-head{display:flex;align-items:center;justify-content:space-between;padding:15px 20px;border-bottom:1px solid var(--border)}
.sec-title{font-size:13px;font-weight:700}
.sec-sub{font-size:11px;color:var(--t3);margin-top:1px}
.sec-body{padding:16px 20px}
.badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:.5px}
.bg{background:var(--gl);color:var(--green)}.ba{background:var(--al);color:var(--amber)}.bb{background:var(--bl);color:var(--blue)}
.bgray{background:#f1f5f9;color:#64748b}
table{width:100%;border-collapse:collapse}
thead th{text-align:left;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--t3);padding:10px 14px;border-bottom:1px solid var(--border);background:#f8fafc}
tbody tr{border-bottom:1px solid var(--border);transition:background .1s}
tbody tr:last-child{border-bottom:none}
tbody tr:hover{background:#f8fafc}
tbody td{padding:10px 14px;font-size:12px}
.tm{font-family:var(--mono);font-size:12px}.dim{color:var(--t3)}.tg{color:var(--green);font-weight:600}.tb{color:var(--blue)}.tam{color:var(--amber)}
.footer{text-align:center;color:var(--t3);font-size:11px;font-family:var(--mono);margin-top:6px;padding-bottom:20px}

.cfg-field{display:flex;flex-direction:column;gap:4px;margin-bottom:16px}
.cfg-label{font-size:12px;font-weight:600;color:var(--t2)}
.cfg-input{padding:9px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);font-family:var(--mono);font-size:12px;color:var(--text);outline:none;width:100%;max-width:420px}
.cfg-hint{font-size:11px;color:var(--t3)}

/* ── FUNCIONÁRIOS ── */
.func-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:16px;margin-bottom:18px}
.func-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:22px 20px;cursor:pointer;transition:all .2s;position:relative;overflow:hidden}
.func-card:hover{border-color:var(--border2);box-shadow:0 4px 20px rgba(0,0,0,.07);transform:translateY(-2px)}
.func-card.ativo:hover{border-color:var(--gm)}
.func-card.inativo{opacity:.72}
.func-card-top{display:flex;align-items:center;gap:14px;margin-bottom:16px}
.func-avatar{width:46px;height:46px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;letter-spacing:.5px;flex-shrink:0}
.func-nome{font-size:14px;font-weight:700;color:var(--text);margin-bottom:2px}
.func-cargo{font-size:10px;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;color:var(--t3)}
.func-sep{height:1px;background:var(--border);margin-bottom:14px}
.func-info-row{display:flex;align-items:center;justify-content:space-between}
.func-mat-label{font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--t3);margin-bottom:2px}
.func-mat{font-family:var(--mono);font-size:13px;color:var(--text);font-weight:500}
.func-status-badge{display:flex;align-items:center;gap:5px;padding:4px 10px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:.5px}
.func-status-badge.ativo{background:var(--gl);color:var(--green)}
.func-status-badge.inativo{background:#f1f5f9;color:#64748b}
.func-status-dot{width:6px;height:6px;border-radius:50%}
.func-status-badge.ativo .func-status-dot{background:var(--green);animation:blink 1.5s infinite}
.func-status-badge.inativo .func-status-dot{background:#94a3b8}
.func-card-arrow{position:absolute;top:50%;right:16px;transform:translateY(-50%);font-size:16px;color:var(--t3);opacity:0;transition:opacity .2s,right .2s}
.func-card:hover .func-card-arrow{opacity:1;right:14px}
.func-stats-row{display:flex;gap:14px;margin-top:12px;padding-top:12px;border-top:1px solid var(--border)}
.func-stat{flex:1;text-align:center}
.func-stat-val{font-family:var(--mono);font-size:16px;font-weight:600;color:var(--text)}
.func-stat-lbl{font-size:9px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--t3);margin-top:1px}

/* Funcionário ativo header no dashboard */
.func-header-pill{display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:10px 16px;margin-bottom:18px}
.func-header-avatar{width:36px;height:36px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0}
.func-header-nome{font-size:13px;font-weight:700}
.func-header-mat{font-size:11px;color:var(--t3);font-family:var(--mono)}

/* Stats summary no topo da lista de funcionários */
.func-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
.func-summary-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px;display:flex;align-items:center;gap:12px}
.func-summary-ico{width:36px;height:36px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.func-summary-val{font-family:var(--mono);font-size:24px;font-weight:600;color:var(--text);line-height:1}
.func-summary-lbl{font-size:11px;color:var(--t3);margin-top:2px}

@media(max-width:900px){.kpi-row{grid-template-columns:1fr 1fr}.func-grid{grid-template-columns:1fr}.func-summary{grid-template-columns:1fr 1fr}}
@media(max-width:768px){.sidebar{display:none}.main{margin-left:0}.kpi-row{grid-template-columns:1fr 1fr}}
`;

// ─── MAIN COMPONENT ──────────────────────────────────────────────────────────
export default function SmartStationDashboard() {
  const [page, setPage] = useState("funcionarios");
  const [selectedFunc, setSelectedFunc] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [now, setNow] = useState(new Date());

  // Sessões e status do funcionário selecionado
  const sessions = selectedFunc ? SESSIONS_BY_FUNC[selectedFunc.id] || [] : [];
  const status = {
    isActive: selectedFunc ? selectedFunc.ativo : false,
    entryTime: sessions.length > 0 ? sessions[sessions.length - 1].entryTime : null,
    exitTime: null,
    lastIdleStart: null,
  };

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (!status.entryTime) return;
    const ref = status.entryTime;
    const upd = () => setElapsed(Date.now() - new Date(ref).getTime());
    upd();
    const t = setInterval(upd, 1000);
    return () => clearInterval(t);
  }, [status.entryTime]);

  const totalIdle = sessions.reduce((a, s) => a + (s.idleBefore || 0), 0);
  const totalProc = sessions.reduce((a, s) => a + (s.processingDuration || 0), 0);
  const avgProc = sessions.length ? totalProc / sessions.length : 0;
  const sparkProc = sessions.slice(-10).map(s => s.processingDuration / 1000);
  const sparkIdle = sessions.slice(-10).map(s => (s.idleBefore || 0) / 1000);
  const sparkCount = sessions.slice(-10).map((_, i) => i + 1);

  const handleSelectFunc = (func) => {
    setSelectedFunc(func);
    setPage("dashboard");
  };

  const handleBack = () => {
    setPage("funcionarios");
    setSelectedFunc(null);
  };

  const navItems = [
    { id: "funcionarios", icon: "👥", label: "Funcionários" },
    { id: "dashboard", icon: "▦", label: "Visão Geral" },
    { id: "history", icon: "≡", label: "Histórico" },
    { id: "config", icon: "⚙", label: "Configurações" },
  ];

  const ativosCount = MOCK_FUNCIONARIOS.filter(f => f.ativo).length;
  const inativosCount = MOCK_FUNCIONARIOS.filter(f => !f.ativo).length;

  const getPageTitle = () => {
    if (page === "funcionarios") return "Funcionários";
    if (page === "dashboard") return selectedFunc ? `Visão Geral — ${selectedFunc.nome.split(" ")[0]}` : "Visão Geral";
    if (page === "history") return selectedFunc ? `Histórico — ${selectedFunc.nome.split(" ")[0]}` : "Histórico";
    if (page === "config") return "Configurações";
    return "";
  };

  return (
    <>
      <style>{css}</style>
      <div className="layout">

        {/* ── SIDEBAR ── */}
        <aside className="sidebar">
          <div className="sidebar-logo">
            <div className="logo-box">📦</div>
            <div>
              <div className="logo-name">SmartStation</div>
              <div className="logo-ver">v1.0.0</div>
            </div>
          </div>
          <div className="sb-sec">
            <div className="sb-sec-label">Menu</div>
            {navItems.map(n => (
              <button
                key={n.id}
                className={`nav-btn ${page === n.id ? "active" : ""}`}
                onClick={() => {
                  if (n.id === "funcionarios") {
                    setPage("funcionarios");
                    setSelectedFunc(null);
                  } else {
                    setPage(n.id);
                  }
                }}
              >
                <span className="nav-icon">{n.icon}</span>{n.label}
              </button>
            ))}
          </div>
          <div className="sb-bot">
            <div className="st-pill">
              <div className={`st-dot ${selectedFunc?.ativo ? "on" : "off"}`} />
              <div>
                <div className="st-txt" style={{ color: selectedFunc?.ativo ? "var(--green)" : "var(--amber)" }}>
                  {selectedFunc ? (selectedFunc.ativo ? "Bancada Ativa" : "Ociosa") : "Nenhum selecionado"}
                </div>
                <div className="st-sub">{now.toLocaleTimeString("pt-BR", { hour12: false })}</div>
              </div>
            </div>
          </div>
        </aside>

        {/* ── MAIN ── */}
        <div className="main">
          <div className="topbar">
            <div>
              <div className="tb-title">{getPageTitle()}</div>
              <div className="tb-sub">{formatDate(new Date().toISOString())} · Turno atual</div>
            </div>
            <div className="tb-right">
              {(page === "dashboard" || page === "history") && selectedFunc && (
                <button className="back-btn" onClick={handleBack}>
                  ← Funcionários
                </button>
              )}
              <div className="demo-tag">MODO DEMO</div>
              <div className="clock">{now.toLocaleTimeString("pt-BR", { hour12: false })}</div>
            </div>
          </div>

          <div className="content">

            {/* ══ FUNCIONÁRIOS ══ */}
            {page === "funcionarios" && (
              <>
                {/* Summary bar */}
                <div className="func-summary">
                  <div className="func-summary-card">
                    <div className="func-summary-ico" style={{ background: "#f1f5f9" }}>👥</div>
                    <div>
                      <div className="func-summary-val">{MOCK_FUNCIONARIOS.length}</div>
                      <div className="func-summary-lbl">Total de funcionários</div>
                    </div>
                  </div>
                  <div className="func-summary-card">
                    <div className="func-summary-ico" style={{ background: "var(--gl)" }}>✅</div>
                    <div>
                      <div className="func-summary-val" style={{ color: "var(--green)" }}>{ativosCount}</div>
                      <div className="func-summary-lbl">Ativos agora</div>
                    </div>
                  </div>
                  <div className="func-summary-card">
                    <div className="func-summary-ico" style={{ background: "#f1f5f9" }}>⏸</div>
                    <div>
                      <div className="func-summary-val" style={{ color: "#64748b" }}>{inativosCount}</div>
                      <div className="func-summary-lbl">Inativos</div>
                    </div>
                  </div>
                </div>

                <div className="func-grid">
                  {MOCK_FUNCIONARIOS.map(func => {
                    const funcSessions = SESSIONS_BY_FUNC[func.id] || [];
                    const funcTotalProc = funcSessions.reduce((a, s) => a + (s.processingDuration || 0), 0);
                    const funcAvgProc = funcSessions.length ? funcTotalProc / funcSessions.length : 0;
                    return (
                      <div
                        key={func.id}
                        className={`func-card ${func.ativo ? "ativo" : "inativo"}`}
                        onClick={() => handleSelectFunc(func)}
                      >
                        <div className="func-card-top">
                          <div
                            className="func-avatar"
                            style={{ background: func.corBg, color: func.cor }}
                          >
                            {func.avatar}
                          </div>
                          <div style={{ flex: 1 }}>
                            <div className="func-nome">{func.nome}</div>
                            <div className="func-cargo">{func.cargo}</div>
                          </div>
                          <div
                            className={`func-status-badge ${func.ativo ? "ativo" : "inativo"}`}
                          >
                            <div className="func-status-dot" />
                            {func.ativo ? "Ativo" : "Inativo"}
                          </div>
                        </div>

                        <div className="func-sep" />

                        <div className="func-info-row">
                          <div>
                            <div className="func-mat-label">Matrícula</div>
                            <div className="func-mat">{func.matricula}</div>
                          </div>
                          <div style={{ textAlign: "right" }}>
                            <div className="func-mat-label">Caixas hoje</div>
                            <div className="func-mat" style={{ color: func.cor }}>{funcSessions.length}</div>
                          </div>
                        </div>

                        <div className="func-stats-row">
                          <div className="func-stat">
                            <div className="func-stat-val">{funcSessions.length}</div>
                            <div className="func-stat-lbl">Sessões</div>
                          </div>
                          <div className="func-stat">
                            <div className="func-stat-val" style={{ fontSize: 12 }}>
                              {funcSessions.length ? formatDuration(funcAvgProc) : "--"}
                            </div>
                            <div className="func-stat-lbl">Média/Caixa</div>
                          </div>
                          <div className="func-stat">
                            <div className="func-stat-val">{funcSessions.length > 0 ? "✓" : "—"}</div>
                            <div className="func-stat-lbl">Sessão</div>
                          </div>
                        </div>

                        <div className="func-card-arrow">›</div>
                      </div>
                    );
                  })}
                </div>
              </>
            )}

            {/* ══ VISÃO GERAL ══ */}
            {page === "dashboard" && (
              <>
                {/* Pill de identificação do funcionário */}
                {selectedFunc && (
                  <div className="func-header-pill">
                    <div
                      className="func-header-avatar"
                      style={{ background: selectedFunc.corBg, color: selectedFunc.cor }}
                    >
                      {selectedFunc.avatar}
                    </div>
                    <div>
                      <div className="func-header-nome">{selectedFunc.nome}</div>
                      <div className="func-header-mat">Mat. {selectedFunc.matricula} · {selectedFunc.cargo}</div>
                    </div>
                    <div style={{ marginLeft: "auto" }}>
                      <span className={`badge ${selectedFunc.ativo ? "bg" : "bgray"}`}>
                        {selectedFunc.ativo ? "● Ativo" : "○ Inativo"}
                      </span>
                    </div>
                  </div>
                )}

                {/* Banner de status */}
                <div className={`banner ${status.isActive ? "on" : "off"}`}>
                  <div className="ban-icon">{status.isActive ? "📦" : "⏳"}</div>
                  <div>
                    <div className="ban-lbl">Status da Bancada</div>
                    <div className={`ban-st ${status.isActive ? "on" : "off"}`}>
                      {status.isActive ? "Caixa em Processamento" : "Estação Ociosa"}
                    </div>
                    <div className="ban-timer">{formatDuration(elapsed)}</div>
                  </div>
                  <div className="ban-div" />
                  <div className="ban-ev">
                    <div className="ban-ev-lbl">📥 Caixa Entrou</div>
                    <div className="ban-ev-time">{formatTime(status.entryTime)}</div>
                    <div className="ban-ev-date">{formatDate(status.entryTime)}</div>
                  </div>
                  <div className="ban-div" />
                  <div className="ban-ev">
                    <div className="ban-ev-lbl">📤 Caixa Saiu</div>
                    <div className="ban-ev-time">
                      {status.isActive
                        ? <span style={{ color: "var(--t3)", fontSize: 15 }}>Aguardando…</span>
                        : formatTime(status.exitTime)
                      }
                    </div>
                    {!status.isActive && <div className="ban-ev-date">{formatDate(status.exitTime)}</div>}
                  </div>
                </div>

                {/* KPIs */}
                <div className="kpi-row">
                  <div className="kpi">
                    <div className="kpi-top">
                      <div className="kpi-lbl">Caixas Processadas</div>
                      <div className="kpi-ico" style={{ background: "var(--gl)" }}>📦</div>
                    </div>
                    <div className="kpi-val">{sessions.length}</div>
                    <div className="kpi-sub">hoje no turno</div>
                    <div className="kpi-spark"><Sparkline data={sparkCount} color="#16a34a" /></div>
                    <div className="kpi-trend tu">↑ turno ativo</div>
                  </div>
                  <div className="kpi">
                    <div className="kpi-top">
                      <div className="kpi-lbl">Tempo Médio / Caixa</div>
                      <div className="kpi-ico" style={{ background: "var(--bl)" }}>⏱</div>
                    </div>
                    <div className="kpi-val" style={{ fontSize: 32, paddingTop: 4 }}>{formatDuration(avgProc)}</div>
                    <div className="kpi-sub">média de processamento</div>
                    <div className="kpi-spark"><Sparkline data={sparkProc} color="#2563eb" /></div>
                  </div>
                  <div className="kpi">
                    <div className="kpi-top">
                      <div className="kpi-lbl">Tempo Total Ocioso</div>
                      <div className="kpi-ico" style={{ background: "var(--al)" }}>⏸</div>
                    </div>
                    <div className="kpi-val" style={{ fontSize: 32, paddingTop: 4 }}>{formatDuration(totalIdle)}</div>
                    <div className="kpi-sub">soma das ociosidades</div>
                    <div className="kpi-spark"><Sparkline data={sparkIdle} color="#d97706" /></div>
                    <div className="kpi-trend tw">⚠ monitorar</div>
                  </div>
                </div>
              </>
            )}

            {/* ══ HISTÓRICO ══ */}
            {page === "history" && (
              <>
                {selectedFunc && (
                  <div className="func-header-pill" style={{ marginBottom: 16 }}>
                    <div
                      className="func-header-avatar"
                      style={{ background: selectedFunc.corBg, color: selectedFunc.cor }}
                    >
                      {selectedFunc.avatar}
                    </div>
                    <div>
                      <div className="func-header-nome">{selectedFunc.nome}</div>
                      <div className="func-header-mat">Mat. {selectedFunc.matricula}</div>
                    </div>
                  </div>
                )}
                <div className="sec">
                  <div className="sec-head">
                    <div>
                      <div className="sec-title">Histórico Completo</div>
                      <div className="sec-sub">
                        {selectedFunc ? `Registros de ${selectedFunc.nome.split(" ")[0]}` : "Todos os registros do turno"}
                      </div>
                    </div>
                    <span className="badge bb">{sessions.length} registros</span>
                  </div>
                  <table>
                    <thead>
                      <tr><th>#</th><th>Data</th><th>Caixa Entrou</th><th>Caixa Saiu</th><th>Duração Processo</th><th>Ociosidade Anterior</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                      {[...sessions].reverse().map(s => (
                        <tr key={s.id}>
                          <td className="tm dim">#{String(s.id).padStart(3, "0")}</td>
                          <td className="dim" style={{ fontSize: 14 }}>{formatDate(s.entryTime)}</td>
                          <td className="tm tg">{formatTime(s.entryTime)}</td>
                          <td className="tm tb">{formatTime(s.exitTime)}</td>
                          <td className="tm">{formatDuration(s.processingDuration)}</td>
                          <td>{(s.idleBefore || 0) > 0 ? <span className="badge ba">{formatDuration(s.idleBefore)}</span> : <span className="dim">—</span>}</td>
                          <td><span className="badge bg">Concluído</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {/* ══ CONFIG ══ */}
            {page === "config" && (
              <div className="sec">
                <div className="sec-head">
                  <div className="sec-title">Configurações</div>
                </div>
                <div className="sec-body">
                  {[
                    { label: "URL do Backend", value: API_BASE, hint: "Endereço da API Java" },
                    { label: "Intervalo de Atualização", value: "3000ms", hint: "Frequência do polling" },
                    { label: "Câmera", value: "Camera 0 (padrão)" },
                  ].map(item => (
                    <div key={item.label} className="cfg-field">
                      <label className="cfg-label">{item.label}</label>
                      <input className="cfg-input" defaultValue={item.value} />
                      <span className="cfg-hint">{item.hint}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="footer">SMARTSTATION v1.0 · MODO DEMONSTRAÇÃO · API: {API_BASE}</div>
          </div>
        </div>
      </div>
    </>
  );
}
