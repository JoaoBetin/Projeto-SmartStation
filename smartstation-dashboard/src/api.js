const BASE = "http://localhost:8080";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`Erro ${res.status}: ${res.statusText}`);
  return res.json();
}

// ── FUNCIONÁRIOS ──
export const getFuncionarios       = ()      => request("/funcionario/listar");
export const getFuncionarioById    = (id)    => request(`/funcionario/listarID/${id}`);
export const getFuncionariosAtivos = ()      => request("/funcionario/listarAtivos");
export const verificarAtivo        = (id)    => request(`/funcionario/verificarAtivo/${id}`);
export const criarFuncionario      = (body)  => request("/funcionario/criar", { method: "POST", body: JSON.stringify(body) });
export const alterarFuncionario    = (id, b) => request(`/funcionario/alterar/${id}`, { method: "PATCH", body: JSON.stringify(b) });
export const deletarFuncionario    = (id)    => request(`/funcionario/deletar/${id}`, { method: "DELETE" });

// ── SESSÕES ──
export const getSessoes    = ()      => request("/sessao/listar");
export const getSessaoById = (id)    => request(`/sessao/listar/${id}`);
export const criarSessao   = (body)  => request("/sessao/criar", { method: "POST", body: JSON.stringify(body) });
export const alterarSessao = (id, b) => request(`/sessao/alterar/${id}`, { method: "PATCH", body: JSON.stringify(b) });
export const deletarSessao = (id)    => request(`/sessao/deletar/${id}`, { method: "DELETE" });

// ── CAIXAS ──
export const getCaixas         = ()     => request("/caixa/listar");
export const getCaixaById      = (id)   => request(`/caixa/listar/${id}`);
export const registrarDeteccao = (body) => request("/caixa/detectada", { method: "POST", body: JSON.stringify(body) });
export const deletarCaixa      = (id)   => request(`/caixa/deletar/${id}`, { method: "DELETE" });