#!/usr/bin/env python3
"""
Gera dist/santinho.html: Página isolada de "Santinho Virtual" para o Ficha do Jogo.
Zero dependências externas, estático-primeiro, tema claro/escuro nativo.
Não possui links a partir do hub ou navbar das outras páginas (página unlisted).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell
import theme

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data")
DIST = os.path.join(ROOT, "dist")
CAND_FILE = os.path.join(BASE, "eleicoes", "santinho_candidatos.json")

def carregar_dados():
    if not os.path.exists(CAND_FILE):
        print(f"Erro: {CAND_FILE} não encontrado. Execute scripts/build_santinho_data.py primeiro.")
        sys.exit(1)
    with open(CAND_FILE, encoding="utf-8") as f:
        return json.load(f)

def render_html():
    dados = carregar_dados()
    dados_json_str = json.dumps(dados, ensure_ascii=False)
    
    # CSS específico do Santinho, combinando perfeitamente com os tokens canônicos
    santinho_css = r"""
/* ===== Santinho Virtual: Layout e Componentes ===== */
:root {
  --maxw: 1240px;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  --badge-green-bg: rgba(34, 197, 94, 0.14);
  --badge-green-txt: #22c55e;
  --badge-yellow-bg: rgba(234, 179, 8, 0.16);
  --badge-yellow-txt: #eab308;
  --badge-orange-bg: rgba(249, 115, 22, 0.18);
  --badge-orange-txt: #f97316;
  --badge-red-bg: rgba(239, 68, 68, 0.2);
  --badge-red-txt: #ef4444;
}

body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  line-height: 1.5;
}

#main {
  max-width: var(--maxw);
  margin: 0 auto;
  padding: 24px 16px calc(140px + env(safe-area-inset-bottom, 0px));
}

/* Header isolado da página */
.santinho-header {
  margin-bottom: 24px;
}
.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--acsoft);
  color: var(--ac);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .08em;
  padding: 4px 10px;
  border-radius: 20px;
  margin-bottom: 10px;
}
.santinho-header h1 {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -.03em;
  margin: 0 0 8px;
  color: var(--ink);
}
.santinho-header p {
  color: var(--mut);
  font-size: 15px;
  margin: 0;
  max-width: 820px;
}

/* Layout em duas colunas / Painéis */
.app-layout {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 24px;
  align-items: start;
}
@media (max-width: 900px) {
  .app-layout {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

/* Barra lateral de filtros */
.filters-panel {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 4px 20px var(--dshadow);
}
@media (min-width: 901px) {
  .filters-panel {
    position: sticky;
    top: 60px;
    max-height: calc(100vh - 80px);
    overflow-y: auto;
    overscroll-behavior: contain;
    scrollbar-width: thin;
  }
}
@media (max-width: 900px) {
  .filters-panel {
    padding: 12px 16px;
  }
  .filters-title {
    margin-bottom: 8px !important;
    padding-bottom: 8px !important;
  }
  .filters-body {
    display: none;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px dashed var(--line);
  }
  .filters-body.open {
    display: block;
  }
}
.filters-mobile-toggle-btn {
  display: none;
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--box);
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  transition: all .15s;
}
@media (max-width: 900px) {
  .filters-mobile-toggle-btn {
    display: flex;
  }
}
.filters-mobile-toggle-btn:hover {
  border-color: var(--ac);
  background: var(--acsoft);
}
.badge-filtros-ativos {
  background: var(--acsoft);
  color: var(--ac);
  font-size: 11px;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 12px;
}
.filters-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--line);
}
.filters-title h2 {
  font-size: 16px;
  font-weight: 800;
  margin: 0;
  color: var(--ink);
  letter-spacing: -.01em;
}
.btn-clear-filters {
  background: none;
  border: none;
  color: var(--ac);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}
.btn-clear-filters:hover {
  background: var(--acsoft);
}

.filter-group {
  margin-bottom: 18px;
}
.filter-group:last-child {
  margin-bottom: 0;
}
.filter-label {
  display: block;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--mut);
  margin-bottom: 8px;
}
.search-input, .filter-select {
  width: 100%;
  box-sizing: border-box;
  background: var(--box);
  border: 1px solid var(--line);
  color: var(--ink);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 13.5px;
  outline: none;
  transition: border-color .15s;
}
.search-input:focus, .filter-select:focus {
  border-color: var(--ac);
}

/* Chips clicáveis para filtros rápidos */
.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chip-btn {
  background: var(--box);
  border: 1px solid var(--line);
  color: var(--mut);
  font-size: 12px;
  font-weight: 600;
  padding: 5px 10px;
  border-radius: 20px;
  cursor: pointer;
  transition: all .15s;
  user-select: none;
}
.chip-btn:hover {
  border-color: var(--ac);
  color: var(--ink);
}
.chip-btn.active {
  background: var(--ac);
  color: var(--badge-ink);
  border-color: var(--ac);
  font-weight: 700;
}
.chip-reset-btn {
  padding: 5px 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--box);
  border: 1px solid var(--line);
  color: var(--mut);
  border-radius: 20px;
  cursor: pointer;
  transition: all .15s;
  flex: none;
}
.chip-reset-btn:hover {
  border-color: var(--ac);
  color: var(--ink);
}
.chip-reset-btn.all-selected {
  background: var(--acsoft);
  color: var(--ac);
  border-color: var(--ac);
}
.icon-reset {
  display: block;
}

/* Toggle switch simples */
.toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
  user-select: none;
}
.toggle-item input {
  display: none;
}
.toggle-switch {
  width: 36px;
  height: 20px;
  background: var(--box);
  border: 1px solid var(--line);
  border-radius: 20px;
  position: relative;
  transition: background .2s;
  flex: none;
}
.toggle-switch::after {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  background: var(--mut);
  border-radius: 50%;
  transition: transform .2s, background .2s;
}
.toggle-item input:checked + .toggle-switch {
  background: var(--ac);
  border-color: var(--ac);
}
.toggle-item input:checked + .toggle-switch::after {
  transform: translateX(16px);
  background: var(--badge-ink);
}

/* Área de resultados e candidatos */
.candidates-view {
  min-width: 0;
}
.results-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
  flex-wrap: wrap;
}
.results-count {
  font-size: 14px;
  color: var(--mut);
  font-weight: 600;
}
.results-count b {
  color: var(--ink);
}

.candidates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 280px), 1fr));
  gap: 16px;
}

/* Card do candidato */
.cand-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  transition: transform .15s, border-color .15s, box-shadow .15s;
}
.cand-card:hover {
  border-color: var(--ac);
  box-shadow: 0 6px 20px var(--dshadow);
}
.cand-card.in-santinho {
  border: 2px solid var(--ac);
  background: var(--card2);
}

.cand-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}
.cand-header-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}
.tag-cargo {
  background: var(--acsoft);
  color: var(--ac);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .06em;
  padding: 2px 7px;
  border-radius: 4px;
}
.tag-partido {
  background: var(--box);
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 11px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 4px;
}
.cand-numero-badge {
  font-family: var(--font-mono);
  font-size: 20px;
  font-weight: 900;
  color: var(--ink);
  background: var(--box);
  border: 1px solid var(--line);
  padding: 4px 10px;
  border-radius: 8px;
  letter-spacing: .03em;
  line-height: 1.1;
  text-align: right;
  flex: none;
}

.cand-main-info {
  display: flex;
  gap: 12px;
  align-items: center;
}
.cand-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--box);
  border: 1.5px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 16px;
  color: var(--ac);
  flex: none;
}
.cand-titles {
  min-width: 0;
  flex: 1;
}
.cand-urna {
  font-size: 17px;
  font-weight: 800;
  color: var(--ink);
  margin: 0 0 2px;
  line-height: 1.2;
}
.cand-nome-oficial {
  font-size: 12px;
  color: var(--mut);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cand-badges-row {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 2px;
}
.badge-pill {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
}
.pill-espectro-esquerda { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.pill-espectro-centro-esquerda { background: rgba(249, 115, 22, 0.15); color: #f97316; }
.pill-espectro-centro { background: rgba(234, 179, 8, 0.15); color: #eab308; }
.pill-espectro-centro-direita { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.pill-espectro-direita { background: rgba(99, 102, 241, 0.15); color: #818cf8; }

.pill-vida {
  background: var(--box);
  color: var(--mut);
  border: 1px solid var(--line);
}

.cand-bio-resumo {
  font-size: 12.5px;
  color: var(--mut);
  line-height: 1.45;
  background: var(--box);
  padding: 8px 10px;
  border-radius: 6px;
  border-left: 3px solid var(--ac);
}

.cand-causas {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.causa-chip {
  font-size: 10.5px;
  font-weight: 600;
  background: var(--box);
  color: var(--mut);
  padding: 2px 7px;
  border-radius: 4px;
  border: 1px solid var(--line);
}

/* Seção de Transparência Jurídica / Boatos */
.cand-juridico {
  border-top: 1px dashed var(--line);
  padding-top: 10px;
}
.juridico-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.juridico-label {
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--mut);
}
.juridico-badge {
  font-size: 11px;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 4px;
}
.status-baixo { background: var(--badge-green-bg); color: var(--badge-green-txt); }
.status-atencao { background: var(--badge-yellow-bg); color: var(--badge-yellow-txt); }
.status-medio { background: var(--badge-orange-bg); color: var(--badge-orange-txt); }
.status-alto, .status-critico { background: var(--badge-red-bg); color: var(--badge-red-txt); }

.juridico-desc {
  font-size: 11.5px;
  color: var(--mut);
  line-height: 1.4;
  margin: 0;
}

/* Viabilidade eleitoral (modelo FDJ) */
.cand-modelo-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11.5px;
  color: var(--mut);
}
.modelo-bar-outer {
  flex: 1;
  height: 6px;
  background: var(--box);
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid var(--line);
}
.modelo-bar-inner {
  height: 100%;
  background: var(--win);
  border-radius: 3px;
}

/* Botão de Adicionar ao Santinho */
.cand-actions {
  margin-top: auto;
  padding-top: 8px;
}
.btn-select-cand {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all .15s;
  border: 1px solid var(--ac);
  background: var(--acsoft);
  color: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.btn-select-cand:hover {
  background: var(--ac);
  color: var(--badge-ink);
}
.cand-card.in-santinho .btn-select-cand {
  background: var(--ac);
  color: var(--badge-ink);
}
.cand-card.in-santinho .btn-select-cand:hover {
  background: var(--loss);
  border-color: var(--loss);
  color: #fff;
}

/* Dock Fixo Inferior: Meu Santinho */
.santinho-dock {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background: var(--card);
  border-top: 2px solid var(--ac);
  box-shadow: 0 -8px 30px rgba(0,0,0,0.4);
  transition: transform .25s ease-in-out;
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
.dock-bar {
  max-width: var(--maxw);
  margin: 0 auto;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.dock-summary {
  display: flex;
  align-items: center;
  gap: 12px;
}
.dock-counter {
  font-size: 16px;
  font-weight: 800;
  color: var(--ink);
}
.dock-counter b {
  color: var(--ac);
}
.dock-toggle-btn {
  background: var(--box);
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 12px;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.dock-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.btn-colinha {
  background: var(--win);
  color: #fff;
  border: none;
  font-size: 13.5px;
  font-weight: 800;
  padding: 9px 18px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 10px rgba(34, 197, 94, 0.3);
}
.btn-colinha:hover {
  opacity: .92;
}

/* Gaveta expandida dos slots do Santinho */
.dock-drawer {
  max-width: var(--maxw);
  margin: 0 auto;
  padding: 0 16px 16px;
  display: none;
  max-height: 60vh;
  overflow-y: auto;
}
.santinho-dock.open .dock-drawer {
  display: block;
}
.slots-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  margin-top: 10px;
}
@media (max-width: 900px) {
  .slots-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 500px) {
  .slots-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.slot-card {
  background: var(--box);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: relative;
  min-height: 80px;
}
.slot-card.filled {
  border-color: var(--ac);
  background: var(--card2);
}
.slot-cargo {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--mut);
  letter-spacing: .05em;
}
.slot-numero {
  font-family: var(--font-mono);
  font-size: 18px;
  font-weight: 900;
  color: var(--ink);
  line-height: 1.1;
}
.slot-nome {
  font-size: 12px;
  font-weight: 800;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.slot-partido {
  font-size: 10px;
  font-weight: 700;
  color: var(--mut);
}
.slot-vazio {
  color: var(--mut);
  font-size: 11px;
  font-style: italic;
  margin-top: auto;
}
.slot-remove-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  background: var(--box);
  color: var(--mut);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
}
.slot-remove-btn:hover {
  background: var(--loss);
  color: #fff;
}

/* Modal de Colinha Eleitoral de Bolso */
.colinha-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.colinha-modal-backdrop.open {
  display: flex;
}
.colinha-sheet {
  background: #ffffff;
  color: #111827;
  width: 100%;
  max-width: 440px;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  max-height: 90vh;
  overflow-y: auto;
}
.colinha-header {
  text-align: center;
  border-bottom: 2px dashed #d1d5db;
  padding-bottom: 14px;
  margin-bottom: 16px;
}
.colinha-header h2 {
  font-size: 20px;
  font-weight: 900;
  letter-spacing: -.02em;
  margin: 0 0 4px;
  color: #111827;
}
.colinha-header p {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: .08em;
  font-weight: 700;
}
.colinha-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.colinha-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}
.colinha-item-info {
  min-width: 0;
}
.colinha-order {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  color: #9ca3af;
  margin-bottom: 2px;
}
.colinha-cand-name {
  font-size: 14px;
  font-weight: 800;
  color: #111827;
}
.colinha-cand-party {
  font-size: 11px;
  color: #6b7280;
  font-weight: 600;
}
.colinha-cand-num {
  font-family: var(--font-mono);
  font-size: 24px;
  font-weight: 900;
  color: #15803d;
  letter-spacing: .04em;
  flex: none;
  padding-left: 10px;
}
.colinha-footer {
  margin-top: 20px;
  border-top: 2px dashed #d1d5db;
  padding-top: 16px;
  display: flex;
  gap: 10px;
}
.btn-modal-action {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid #d1d5db;
  background: #f3f4f6;
  color: #1f2937;
  text-align: center;
}
.btn-modal-action.primary {
  background: #15803d;
  color: #fff;
  border-color: #15803d;
}
.btn-modal-close {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 12px;
  cursor: pointer;
  padding: 6px;
  text-align: center;
  display: block;
  width: 100%;
  margin-top: 8px;
}

/* Badges de Gênero / Identidade */
.badge-genero {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;
  display: inline-block;
}
.genero-mulher { background: rgba(236, 72, 153, 0.15); color: #f472b6; }
.genero-homem { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.genero-mulher_trans { background: rgba(168, 85, 247, 0.2); color: #c084fc; }
.genero-homem_trans { background: rgba(20, 184, 166, 0.2); color: #2dd4bf; }
.genero-nao_binario { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }

[data-theme="light"] .genero-mulher { background: #fce7f3; color: #be185d; }
[data-theme="light"] .genero-homem { background: #dbeafe; color: #1d4ed8; }
[data-theme="light"] .genero-mulher_trans { background: #f3e8ff; color: #7e22ce; }
[data-theme="light"] .genero-homem_trans { background: #ccfbf1; color: #0f766e; }
[data-theme="light"] .genero-nao_binario { background: #fef3c7; color: #b45309; }

/* Filtro de Pautas e Segmented Controls */
.pautas-filter-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 380px;
  overflow-y: auto;
  padding-right: 4px;
}
.pauta-filter-row {
  background: var(--box);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 8px 10px;
}
.pauta-filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.pauta-filter-title {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
}
.pauta-segmented {
  display: flex;
  gap: 2px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 2px;
}
.pauta-opt-btn {
  flex: 1;
  min-height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  border: none;
  background: transparent;
  color: var(--mut);
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: all .15s;
  text-align: center;
  white-space: nowrap;
}
.pauta-opt-btn:hover {
  color: var(--ink);
}
.pauta-opt-btn.active.opt-todos {
  background: var(--box);
  color: var(--ink);
  font-weight: 700;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.pauta-opt-btn.active.opt-favor {
  background: var(--badge-green-bg);
  color: var(--badge-green-txt);
  font-weight: 800;
}
.pauta-opt-btn.active.opt-contra {
  background: var(--badge-red-bg);
  color: var(--badge-red-txt);
  font-weight: 800;
}
.pauta-opt-btn.active.opt-neutro {
  background: var(--badge-yellow-bg);
  color: var(--badge-yellow-txt);
  font-weight: 800;
}

/* Posicionamentos no Card do Candidato */
.cand-posicionamentos-box {
  background: var(--box);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 8px 10px;
}
.pos-box-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
}
.pos-box-label {
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--mut);
  letter-spacing: .04em;
}
.pos-box-toggle {
  font-size: 11px;
  color: var(--ac);
  font-weight: 700;
}
.pos-highlights-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}
.pos-chip {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 3px;
}
.pos-chip.pos-favor {
  background: var(--badge-green-bg);
  color: var(--badge-green-txt);
}
.pos-chip.pos-contra {
  background: var(--badge-red-bg);
  color: var(--badge-red-txt);
}
.pos-chip.pos-neutro {
  background: var(--card);
  color: var(--mut);
  border: 1px solid var(--line);
}
.pautas-expanded-grid {
  display: none;
  grid-template-columns: 1fr;
  gap: 6px 12px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--line);
}
@media (min-width: 580px) {
  .pautas-expanded-grid {
    grid-template-columns: 1fr 1fr;
  }
}
.cand-posicionamentos-box.expanded .pautas-expanded-grid {
  display: grid;
}
.pauta-expanded-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  padding: 2px 0;
}
.pauta-expanded-name {
  color: var(--ink);
  font-weight: 600;
}

/* Otimização de Impressão */
@media print {
  body {
    background: #ffffff !important;
    color: #000000 !important;
  }
  .topbar, .filters-panel, .results-meta, .candidates-grid, .santinho-dock, .btn-modal-close, .colinha-footer {
    display: none !important;
  }
  .colinha-modal-backdrop {
    display: block !important;
    position: static !important;
    background: none !important;
    padding: 0 !important;
  }
  .colinha-sheet {
    max-width: 100% !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
  }
}
"""

    # Topbar especial isolada: marca e toggle de tema, SEM abas de outras páginas
    topbar_html = (
        '<header class="topbar"><div class="bar">'
        '<div class="brand">'
        + shell.LOGO + '<span class="nm">Ficha <span>do Jogo</span></span></div>'
        '<span class="sp"></span>'
        '<button class="tg" id="tg" type="button" onclick="cycleTheme()" title="Tema escuro · clique para alternar" aria-label="Alternar tema">☾</button>'
        '</div></header>'
    )

    # Documento HTML completo montado estático-primeiro
    doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Meu Santinho Virtual · Ficha do Jogo</title>
<meta name="description" content="Selecione e filtre seus candidatos para Presidente, Governador, Senador e Deputados no seu santinho virtual das Eleições 2026.">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<style>
{theme.PALETTE}
{shell.CSS}
{santinho_css}
</style>
<script>
// Pré-paint do tema salvo para evitar flash
(function(){{
  try{{
    var t=localStorage.getItem("fdj-theme");
    if(t==="light")document.documentElement.setAttribute("data-theme","light");
  }}catch(e){{}}
}})();
</script>
</head>
<body data-page="santinho">
{topbar_html}

<main id="main">
  <div class="santinho-header">
    <div class="header-badge">Eleições 2026 · Ferramenta Pessoal</div>
    <h1>Meu Santinho Virtual</h1>
    <p>
      Filtre candidatos por espectro político, histórico de vida pública, causas defendidas, registros jurídicos e viabilidade eleitoral para montar sua cola oficial para a urna. Suas escolhas ficam salvas no navegador.
    </p>
  </div>

  <div class="app-layout">
    <!-- Painel Lateral de Filtros -->
    <aside class="filters-panel" aria-label="Filtros de candidatos">
      <div class="filters-title">
        <h2>Filtros <span class="badge-filtros-ativos" id="badge-filtros-ativos" style="display:none;">0 ativos</span></h2>
        <button type="button" class="btn-clear-filters" id="btn-reset-filters">Limpar filtros</button>
      </div>

      <!-- Botão para colapsar/expandir filtros no celular -->
      <button type="button" class="filters-mobile-toggle-btn" id="btn-toggle-filters-mobile" aria-expanded="false">
        <span>Filtros & Pautas</span>
        <span id="label-toggle-filters-status">Toque para expandir ▾</span>
      </button>

      <div class="filters-body" id="filters-body">
        <!-- Busca textual -->
        <div class="filter-group">
          <label class="filter-label" for="search-box">Buscar por Nome ou Número</label>
          <input type="text" id="search-box" class="search-input" placeholder="Ex: Tarcísio, 13, Boulos, 2222..." autocomplete="off">
        </div>

      <!-- Cargo -->
      <div class="filter-group">
        <label class="filter-label">Cargo na Urna</label>
        <div class="chip-group" id="chips-cargo">
          <button type="button" class="chip-btn chip-reset-btn all-selected" title="Alternar: todos / nenhum" aria-label="Alternar todos os cargos">
            <svg class="icon-reset" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 8a5.5 5.5 0 0 1 9.3-3.9l1.7-1.6V7h-4.5l1.6-1.6A4 4 0 0 0 4 8zM13.5 8a5.5 5.5 0 0 1-9.3 3.9l-1.7 1.6V9h4.5l-1.6 1.6A4 4 0 0 0 12 8z"/></svg>
          </button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="presidente">Presidente</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="governador">Governador</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="senador">Senador</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="deputado_federal">Dep. Federal</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="deputado_estadual">Dep. Estadual</button>
        </div>
      </div>

      <!-- Estado / UF -->
      <div class="filter-group">
        <label class="filter-label" for="select-uf">Estado (UF)</label>
        <select id="select-uf" class="filter-select">
          <option value="SP" selected>São Paulo (SP)</option>
          <option value="BR">Brasil Geral / Outros Estados</option>
          <option value="todos">Todos os Estados</option>
        </select>
      </div>

      <!-- Espectro Político -->
      <div class="filter-group">
        <label class="filter-label">Espectro Político</label>
        <div class="chip-group" id="chips-espectro">
          <button type="button" class="chip-btn chip-reset-btn all-selected" title="Alternar: todos / nenhum" aria-label="Alternar todos os espectros">
            <svg class="icon-reset" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 8a5.5 5.5 0 0 1 9.3-3.9l1.7-1.6V7h-4.5l1.6-1.6A4 4 0 0 0 4 8zM13.5 8a5.5 5.5 0 0 1-9.3 3.9l-1.7 1.6V9h4.5l-1.6 1.6A4 4 0 0 0 12 8z"/></svg>
          </button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="esquerda">Esquerda</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="centro-esquerda">Centro-Esq.</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="centro">Centro</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="centro-direita">Centro-Dir.</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="direita">Direita</button>
        </div>
      </div>

      <!-- Gênero / Identidade -->
      <div class="filter-group">
        <label class="filter-label">Gênero / Identidade</label>
        <div class="chip-group" id="chips-genero">
          <button type="button" class="chip-btn chip-reset-btn all-selected" title="Alternar: todos / nenhum" aria-label="Alternar todos os gêneros">
            <svg class="icon-reset" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 8a5.5 5.5 0 0 1 9.3-3.9l1.7-1.6V7h-4.5l1.6-1.6A4 4 0 0 0 4 8zM13.5 8a5.5 5.5 0 0 1-9.3 3.9l-1.7 1.6V9h4.5l-1.6 1.6A4 4 0 0 0 12 8z"/></svg>
          </button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="mulher">Mulher</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="homem">Homem</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="mulher_trans">Mulher Trans</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="homem_trans">Homem Trans</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="nao_binario">Não-Binário</button>
        </div>
      </div>

      <!-- Vida Pregressa -->
      <div class="filter-group">
        <label class="filter-label">Vida Pregressa na Política</label>
        <div class="chip-group" id="chips-vida">
          <button type="button" class="chip-btn chip-reset-btn all-selected" title="Alternar: todos / nenhum" aria-label="Alternar todas as trajetórias">
            <svg class="icon-reset" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 8a5.5 5.5 0 0 1 9.3-3.9l1.7-1.6V7h-4.5l1.6-1.6A4 4 0 0 0 4 8zM13.5 8a5.5 5.5 0 0 1-9.3 3.9l-1.7 1.6V9h4.5l-1.6 1.6A4 4 0 0 0 12 8z"/></svg>
          </button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="novato">Novato</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="reeleicao">Reeleição</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="veterano">Veterano</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="ex_executivo">Ex-Executivo</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="carreira_tecnica">Carreira Técnica</button>
        </div>
      </div>

      <!-- Partido -->
      <div class="filter-group">
        <label class="filter-label" for="select-partido">Partido</label>
        <select id="select-partido" class="filter-select">
          <option value="todos">Todos os partidos</option>
        </select>
      </div>

      <!-- Filtro Jurídico / Boatos -->
      <div class="filter-group">
        <label class="filter-label">Transparência Jurídica & Boatos</label>
        <div class="chip-group" id="chips-juridico">
          <button type="button" class="chip-btn chip-reset-btn all-selected" title="Alternar: todos / nenhum" aria-label="Alternar todos os status jurídicos">
            <svg class="icon-reset" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 8a5.5 5.5 0 0 1 9.3-3.9l1.7-1.6V7h-4.5l1.6-1.6A4 4 0 0 0 4 8zM13.5 8a5.5 5.5 0 0 1-9.3 3.9l-1.7 1.6V9h4.5l-1.6 1.6A4 4 0 0 0 12 8z"/></svg>
          </button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="nenhum">Ficha Limpa</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="boato_noticia">Boato / Imprensa</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="investigado">Investigado</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="reu">Réu</button>
          <button type="button" class="chip-btn chip-item-btn active" data-val="condenado">Condenado</button>
        </div>
      </div>

      <!-- Causas prioritárias -->
      <div class="filter-group">
        <label class="filter-label">Causas Defendidas</label>
        <div class="chip-group" id="chips-causas">
          <button type="button" class="chip-btn chip-reset-btn" id="btn-reset-causas" title="Limpar seleção de causas" aria-label="Limpar causas">
            <svg class="icon-reset" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 8a5.5 5.5 0 0 1 9.3-3.9l1.7-1.6V7h-4.5l1.6-1.6A4 4 0 0 0 4 8zM13.5 8a5.5 5.5 0 0 1-9.3 3.9l-1.7 1.6V9h4.5l-1.6 1.6A4 4 0 0 0 12 8z"/></svg>
          </button>
          <!-- preenchido dinamicamente via JS -->
        </div>
      </div>

      <!-- Posicionamentos em Pautas Chave -->
      <div class="filter-group">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
          <label class="filter-label" style="margin-bottom:0;">Pautas & Posicionamento</label>
          <button type="button" class="btn-clear-filters" id="btn-reset-pautas" style="font-size:11px;padding:2px 6px;">Resetar pautas</button>
        </div>
        <div class="pautas-filter-box" id="pautas-filter-list">
          <!-- preenchido dinamicamente via JS com as 15 pautas -->
        </div>
      </div>

      <!-- Toggles adicionais -->
      <div class="filter-group">
        <label class="toggle-item">
          <span>Abre mão do Fundão Eleitoral</span>
          <input type="checkbox" id="toggle-fundao">
          <span class="toggle-switch"></span>
        </label>
      </div>
      </div>
    </aside>

    <!-- Área Principal de Candidatos -->
    <section class="candidates-view">
      <div class="results-meta">
        <div class="results-count" id="results-count">Exibindo <b>0</b> candidatos</div>
        <div class="results-sort">
          <select id="select-sort" class="filter-select" style="width: auto; padding: 6px 10px;">
            <option value="numero">Ordenar por Número</option>
            <option value="nome">Ordenar por Nome</option>
            <option value="viabilidade">Maior viabilidade no modelo</option>
          </select>
        </div>
      </div>

      <div class="candidates-grid" id="candidates-grid">
        <!-- Renderizado dinamicamente pelo JS -->
      </div>
    </section>
  </div>
</main>

<!-- Dock Fixo Inferior: Meu Santinho -->
<div class="santinho-dock" id="santinho-dock">
  <div class="dock-bar">
    <div class="dock-summary">
      <button type="button" class="dock-toggle-btn" id="btn-toggle-dock">▲ Abrir gaveta</button>
      <div class="dock-counter" id="dock-counter">Meu Santinho: <b>0 de 6</b> definidos</div>
    </div>
    <div class="dock-actions">
      <button type="button" class="btn-clear-filters" id="btn-limpar-santinho" style="color: var(--mut);">Limpar tudo</button>
      <button type="button" class="btn-colinha" id="btn-abrir-colinha">
        <span aria-hidden="true">📋</span> Ver Colinha de Bolso
      </button>
    </div>
  </div>
  <div class="dock-drawer">
    <div class="slots-grid" id="slots-grid">
      <!-- 6 slots gerados pelo JS -->
    </div>
  </div>
</div>

<!-- Modal da Colinha Eleitoral -->
<div class="colinha-modal-backdrop" id="colinha-modal">
  <div class="colinha-sheet">
    <div class="colinha-header">
      <h2>Minha Cola Eleitoral</h2>
      <p>Eleições 2026 · Ordem de Votação na Urna</p>
    </div>
    <div class="colinha-list" id="colinha-list">
      <!-- Ordem oficial TSE preenchida via JS -->
    </div>
    <div class="colinha-footer">
      <button type="button" class="btn-modal-action primary" id="btn-imprimir-colinha">🖨 Imprimir / Salvar PDF</button>
      <button type="button" class="btn-modal-action" id="btn-copiar-colinha">📋 Copiar Texto</button>
    </div>
    <button type="button" class="btn-modal-close" id="btn-fechar-colinha">Fechar colinha</button>
  </div>
</div>

<!-- Payload de dados estruturados -->
<script id="santinho-data" type="application/json">
{dados_json_str}
</script>

<script>
// Motor de Filtros e Persistência do Santinho Virtual
(function() {{
  var RAW_DATA = JSON.parse(document.getElementById("santinho-data").textContent);
  var CANDIDATOS = RAW_DATA.candidatos || [];
  var META = RAW_DATA.meta || {{}};

  // Slots canônicos e ordem oficial do TSE na urna eletrônica
  var SLOTS_CONFIG = [
    {{ id: "deputado_federal", label: "Deputado Federal", digitos: 4, ordem_urna: 1 }},
    {{ id: "deputado_estadual", label: "Deputado Estadual", digitos: 5, ordem_urna: 2 }},
    {{ id: "senador_1", label: "Senador (1ª Vaga)", digitos: 3, cargo_filtro: "senador", ordem_urna: 3 }},
    {{ id: "senador_2", label: "Senador (2ª Vaga)", digitos: 3, cargo_filtro: "senador", ordem_urna: 4 }},
    {{ id: "governador", label: "Governador", digitos: 2, ordem_urna: 5 }},
    {{ id: "presidente", label: "Presidente", digitos: 2, ordem_urna: 6 }}
  ];

  // Definições canônicas de valores para cada filtro multi-seleção
  var ALL_CARGOS = ["presidente", "governador", "senador", "deputado_federal", "deputado_estadual"];
  var ALL_ESPECTROS = ["esquerda", "centro-esquerda", "centro", "centro-direita", "direita"];
  var ALL_GENEROS = ["mulher", "homem", "mulher_trans", "homem_trans", "nao_binario"];
  var ALL_VIDAS = ["novato", "reeleicao", "veterano", "ex_executivo", "carreira_tecnica"];
  var ALL_JURIDICOS = ["nenhum", "boato_noticia", "investigado", "reu", "condenado"];

  // Estado da aplicação
  var state = {{
    filtro_cargos: ALL_CARGOS.slice(),
    filtro_uf: "SP",
    filtro_espectros: ALL_ESPECTROS.slice(),
    filtro_generos: ALL_GENEROS.slice(),
    filtro_vidas: ALL_VIDAS.slice(),
    filtro_partido: "todos",
    filtro_juridicos: ALL_JURIDICOS.slice(),
    filtro_causas: [],
    filtro_pautas: {{}}, // pauta_id -> "todos" | "favor" | "contra" | "neutro"
    filtro_busca: "",
    filtro_fundao: false,
    ordem: "numero",
    escolhas: {{}} // slot_id -> cand_id
  }};

  var syncCargosGlobal = null;

  // Recupera escolhas salvas no localStorage
  try {{
    var salvo = localStorage.getItem("fdj_santinho_escolhas");
    if (salvo) state.escolhas = JSON.parse(salvo);
  }} catch(e) {{}}

  function salvarEscolhas() {{
    try {{
      localStorage.setItem("fdj_santinho_escolhas", JSON.stringify(state.escolhas));
    }} catch(e) {{}}
  }}

  // Inicialização de Dropdowns e Tags
  function initFilters() {{
    var partidos = {{}};
    CANDIDATOS.forEach(function(c) {{ if (c.partido) partidos[c.partido] = true; }});
    var selPartido = document.getElementById("select-partido");
    Object.keys(partidos).sort().forEach(function(p) {{
      var opt = document.createElement("option");
      opt.value = p;
      opt.textContent = p;
      selPartido.appendChild(opt);
    }});

    // Helper universal para grupos de chips multi-seleção com botão de reset em ícone
    function bindMultiGroup(containerId, allList, stateKey) {{
      var container = document.getElementById(containerId);
      if (!container) return function(){{}};
      var resetBtn = container.querySelector(".chip-reset-btn");
      var itemBtns = container.querySelectorAll(".chip-item-btn");

      function sync() {{
        var arr = state[stateKey];
        itemBtns.forEach(function(b) {{
          var val = b.dataset.val;
          b.classList.toggle("active", arr.indexOf(val) >= 0);
        }});
        if (resetBtn) {{
          var isAll = arr.length === allList.length;
          resetBtn.classList.toggle("all-selected", isAll);
          resetBtn.title = isAll ? "Desmarcar todos" : "Selecionar todos";
        }}
      }}

      if (resetBtn) {{
        resetBtn.onclick = function() {{
          if (state[stateKey].length === allList.length) {{
            state[stateKey] = [];
          }} else {{
            state[stateKey] = allList.slice();
          }}
          sync();
          renderCandidatos();
        }};
      }}

      itemBtns.forEach(function(b) {{
        b.onclick = function() {{
          var val = b.dataset.val;
          var idx = state[stateKey].indexOf(val);
          if (idx >= 0) {{
            state[stateKey].splice(idx, 1);
          }} else {{
            state[stateKey].push(val);
          }}
          sync();
          renderCandidatos();
        }};
      }});

      sync();
      return sync;
    }}

    var syncCargos = bindMultiGroup("chips-cargo", ALL_CARGOS, "filtro_cargos");
    syncCargosGlobal = syncCargos;
    var syncEspectros = bindMultiGroup("chips-espectro", ALL_ESPECTROS, "filtro_espectros");
    var syncGeneros = bindMultiGroup("chips-genero", ALL_GENEROS, "filtro_generos");
    var syncVidas = bindMultiGroup("chips-vida", ALL_VIDAS, "filtro_vidas");
    var syncJuridicos = bindMultiGroup("chips-juridico", ALL_JURIDICOS, "filtro_juridicos");

    // Chips de causas
    var chipsCausas = document.getElementById("chips-causas");
    var resetCausasBtn = document.getElementById("btn-reset-causas");

    if (resetCausasBtn) {{
      resetCausasBtn.onclick = function() {{
        state.filtro_causas = [];
        document.querySelectorAll("#chips-causas .chip-item-btn").forEach(function(b) {{
          b.classList.remove("active");
        }});
        resetCausasBtn.classList.remove("all-selected");
        resetCausasBtn.title = "Nenhuma causa selecionada";
        renderCandidatos();
      }};
    }}

    (META.causas || []).forEach(function(cau) {{
      var b = document.createElement("button");
      b.type = "button";
      b.className = "chip-btn chip-item-btn";
      b.textContent = cau.label;
      b.dataset.val = cau.id;
      b.onclick = function() {{
        var idx = state.filtro_causas.indexOf(cau.id);
        if (idx >= 0) {{
          state.filtro_causas.splice(idx, 1);
          b.classList.remove("active");
        }} else {{
          state.filtro_causas.push(cau.id);
          b.classList.add("active");
        }}
        if (resetCausasBtn) {{
          resetCausasBtn.classList.toggle("all-selected", state.filtro_causas.length > 0);
          resetCausasBtn.title = state.filtro_causas.length > 0 ? "Limpar causas" : "Nenhuma causa selecionada";
        }}
        renderCandidatos();
      }};
      chipsCausas.appendChild(b);
    }});

    // Filtro de Pautas Posicionais (A favor / Contra / Neutro)
    var pautasContainer = document.getElementById("pautas-filter-list");
    var btnResetPautas = document.getElementById("btn-reset-pautas");

    function atualizarBtnResetPautas() {{
      var ativas = 0;
      for (var k in state.filtro_pautas) {{
        if (state.filtro_pautas[k] && state.filtro_pautas[k] !== "todos") ativas++;
      }}
      if (btnResetPautas) {{
        btnResetPautas.textContent = ativas > 0 ? "Resetar (" + ativas + " ativas)" : "Resetar pautas";
        btnResetPautas.style.color = ativas > 0 ? "var(--loss)" : "var(--ac)";
      }}
    }}

    if (btnResetPautas) {{
      btnResetPautas.onclick = function() {{
        state.filtro_pautas = {{}};
        atualizarBtnResetPautas();
        document.querySelectorAll(".pauta-opt-btn").forEach(function(b) {{
          b.classList.toggle("active", b.dataset.val === "todos");
        }});
        renderCandidatos();
      }};
    }}

    if (pautasContainer) {{
      (META.pautas || []).forEach(function(pauta) {{
        var row = document.createElement("div");
        row.className = "pauta-filter-row";

        var header = document.createElement("div");
        header.className = "pauta-filter-header";

        var title = document.createElement("span");
        title.className = "pauta-filter-title";
        title.textContent = pauta.label;
        title.title = pauta.descricao || "";
        header.appendChild(title);
        row.appendChild(header);

        var seg = document.createElement("div");
        seg.className = "pauta-segmented";

        var opts = [
          {{ id: "todos", label: "Todos", cls: "opt-todos" }},
          {{ id: "favor", label: "✓ A favor", cls: "opt-favor" }},
          {{ id: "contra", label: "✗ Contra", cls: "opt-contra" }},
          {{ id: "neutro", label: "○ Neutro", cls: "opt-neutro" }}
        ];

        opts.forEach(function(opt) {{
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "pauta-opt-btn " + opt.cls + (opt.id === "todos" ? " active" : "");
          btn.textContent = opt.label;
          btn.dataset.val = opt.id;
          btn.onclick = function() {{
            seg.querySelectorAll(".pauta-opt-btn").forEach(function(b) {{ b.classList.remove("active"); }});
            btn.classList.add("active");
            if (opt.id === "todos") {{
              delete state.filtro_pautas[pauta.id];
            }} else {{
              state.filtro_pautas[pauta.id] = opt.id;
            }}
            atualizarBtnResetPautas();
            renderCandidatos();
          }};
          seg.appendChild(btn);
        }});

        row.appendChild(seg);
        pautasContainer.appendChild(row);
      }});
    }}

    // Busca textual
    var searchBox = document.getElementById("search-box");
    searchBox.oninput = function() {{
      state.filtro_busca = searchBox.value.trim().toLowerCase();
      renderCandidatos();
    }};

    // Selects restantes (UF, Partido, Ordem, Fundão)
    document.getElementById("select-uf").onchange = function(e) {{
      state.filtro_uf = e.target.value;
      renderCandidatos();
    }};
    document.getElementById("select-partido").onchange = function(e) {{
      state.filtro_partido = e.target.value;
      renderCandidatos();
    }};
    document.getElementById("select-sort").onchange = function(e) {{
      state.ordem = e.target.value;
      renderCandidatos();
    }};
    document.getElementById("toggle-fundao").onchange = function(e) {{
      state.filtro_fundao = e.target.checked;
      renderCandidatos();
    }};

    document.getElementById("btn-reset-filters").onclick = function() {{
      state.filtro_cargos = ALL_CARGOS.slice();
      state.filtro_uf = "SP";
      state.filtro_espectros = ALL_ESPECTROS.slice();
      state.filtro_generos = ALL_GENEROS.slice();
      state.filtro_vidas = ALL_VIDAS.slice();
      state.filtro_partido = "todos";
      state.filtro_juridicos = ALL_JURIDICOS.slice();
      state.filtro_causas = [];
      state.filtro_pautas = {{}};
      state.filtro_busca = "";
      state.filtro_fundao = false;
      document.getElementById("search-box").value = "";
      document.getElementById("select-uf").value = "SP";
      document.getElementById("select-partido").value = "todos";
      document.getElementById("toggle-fundao").checked = false;
      syncCargos();
      syncEspectros();
      syncGeneros();
      syncVidas();
      syncJuridicos();
      if (resetCausasBtn) resetCausasBtn.classList.remove("all-selected");
      document.querySelectorAll("#chips-causas .chip-item-btn").forEach(function(b) {{
        b.classList.remove("active");
      }});
      if (btnResetPautas) {{
        document.querySelectorAll(".pauta-opt-btn").forEach(function(b) {{
          b.classList.toggle("active", b.dataset.val === "todos");
        }});
        atualizarBtnResetPautas();
      }}
      renderCandidatos();
    }};

    // Alternar gaveta de filtros no celular
    var btnToggleMobile = document.getElementById("btn-toggle-filters-mobile");
    var filtersBody = document.getElementById("filters-body");
    var labelToggleStatus = document.getElementById("label-toggle-filters-status");
    if (btnToggleMobile && filtersBody) {{
      btnToggleMobile.onclick = function() {{
        var isOpen = filtersBody.classList.toggle("open");
        btnToggleMobile.setAttribute("aria-expanded", isOpen ? "true" : "false");
        if (labelToggleStatus) {{
          labelToggleStatus.textContent = isOpen ? "Recolher ▴" : "Toque para expandir ▾";
        }}
      }};
    }}
  }}

  // Atualiza contador de filtros ativos e badges
  function atualizarContadorFiltrosAtivos() {{
    var ativos = 0;
    if (state.filtro_cargos.length < ALL_CARGOS.length) ativos++;
    if (state.filtro_uf !== "SP") ativos++;
    if (state.filtro_espectros.length < ALL_ESPECTROS.length) ativos++;
    if (state.filtro_generos.length < ALL_GENEROS.length) ativos++;
    if (state.filtro_vidas.length < ALL_VIDAS.length) ativos++;
    if (state.filtro_partido !== "todos") ativos++;
    if (state.filtro_juridicos.length < ALL_JURIDICOS.length) ativos++;
    if (state.filtro_causas.length > 0) ativos++;
    var temPauta = false;
    for (var k in state.filtro_pautas) {{
      if (state.filtro_pautas[k] && state.filtro_pautas[k] !== "todos") {{
        temPauta = true;
        break;
      }}
    }}
    if (temPauta) ativos++;
    if (state.filtro_fundao) ativos++;
    if (state.filtro_busca) ativos++;

    var badge = document.getElementById("badge-filtros-ativos");
    if (badge) {{
      if (ativos > 0) {{
        badge.textContent = ativos + (ativos === 1 ? " ativo" : " ativos");
        badge.style.display = "inline-block";
      }} else {{
        badge.style.display = "none";
      }}
    }}

    var labelToggleStatus = document.getElementById("label-toggle-filters-status");
    var filtersBody = document.getElementById("filters-body");
    if (labelToggleStatus && filtersBody && !filtersBody.classList.contains("open")) {{
      labelToggleStatus.textContent = ativos > 0 ? (ativos + " ativo" + (ativos > 1 ? "s" : "") + " ▾") : "Toque para expandir ▾";
    }}
  }}

  // Filtra e classifica candidatos
  function getFiltrados() {{
    return CANDIDATOS.filter(function(c) {{
      // Cargo
      if (state.filtro_cargos.indexOf(c.cargo) === -1) return false;

      // UF
      if (state.filtro_uf === "SP") {{
        if (c.uf !== "SP" && c.uf !== "BR") return false;
      }} else if (state.filtro_uf === "BR") {{
        if (c.uf === "SP") return false;
      }}

      // Espectro
      var esp = c.espectro || "centro";
      if (state.filtro_espectros.indexOf(esp) === -1) return false;

      // Gênero / Identidade
      var gen = c.genero || "homem";
      if (state.filtro_generos.indexOf(gen) === -1) return false;

      // Vida pregressa
      var vStat = (c.vida_pregressa && c.vida_pregressa.status) || "novato";
      if (state.filtro_vidas.indexOf(vStat) === -1) return false;

      // Partido
      if (state.filtro_partido !== "todos" && c.partido !== state.filtro_partido) return false;

      // Transparência jurídica / boatos
      var piorTipo = "nenhum";
      (c.registros_juridicos || []).forEach(function(r) {{
        if (r.tipo === "condenado") piorTipo = "condenado";
        else if (r.tipo === "reu" && piorTipo !== "condenado") piorTipo = "reu";
        else if (r.tipo === "investigado" && piorTipo !== "condenado" && piorTipo !== "reu") piorTipo = "investigado";
        else if (r.tipo === "boato_noticia" && piorTipo === "nenhum") piorTipo = "boato_noticia";
      }});
      if (state.filtro_juridicos.indexOf(piorTipo) === -1) return false;

      // Causas
      if (state.filtro_causas.length > 0) {{
        var cCausas = c.causas || [];
        var temAlguma = state.filtro_causas.some(function(cau) {{ return cCausas.indexOf(cau) >= 0; }});
        if (!temAlguma) return false;
      }}

      // Pautas posicionais (A favor / Contra / Neutro)
      for (var pId in state.filtro_pautas) {{
        var exigido = state.filtro_pautas[pId];
        if (exigido && exigido !== "todos") {{
          var posCand = (c.posicionamentos && c.posicionamentos[pId]) || "neutro";
          if (posCand !== exigido) return false;
        }}
      }}

      // Fundão
      if (state.filtro_fundao && c.atributos && c.atributos.fundao) return false;

      // Busca textual
      if (state.filtro_busca) {{
        var term = state.filtro_busca;
        var numStr = String(c.numero || "");
        var urnaStr = (c.urna || "").toLowerCase();
        var nomeStr = (c.nome_completo || "").toLowerCase();
        var partStr = (c.partido || "").toLowerCase();
        if (numStr.indexOf(term) === -1 && urnaStr.indexOf(term) === -1 && nomeStr.indexOf(term) === -1 && partStr.indexOf(term) === -1) {{
          return false;
        }}
      }}

      return true;
    }}).sort(function(a, b) {{
      if (state.ordem === "nome") return (a.urna || "").localeCompare(b.urna || "");
      if (state.ordem === "viabilidade") {{
        var vA = (a.modelo && a.modelo.share_projecao) || 0;
        var vB = (b.modelo && b.modelo.share_projecao) || 0;
        return vB - vA;
      }}
      return (a.numero || 0) - (b.numero || 0);
    }});
  }}

  // Renderiza Grid de Candidatos
  function renderCandidatos() {{
    atualizarContadorFiltrosAtivos();
    var lista = getFiltrados();
    var grid = document.getElementById("candidates-grid");
    var countEl = document.getElementById("results-count");
    countEl.innerHTML = "Exibindo <b>" + lista.length + "</b> candidatos";
    grid.innerHTML = "";

    if (lista.length === 0) {{
      grid.innerHTML = '<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--mut); background: var(--card); border: 1px solid var(--line); border-radius: 12px;">' +
        'Nenhum candidato encontrado com os filtros selecionados.<br><button type="button" class="btn-clear-filters" id="btn-empty-reset" style="margin-top: 10px;">Limpar filtros</button></div>';
      var bReset = document.getElementById("btn-empty-reset");
      if (bReset) bReset.onclick = function() {{ document.getElementById("btn-reset-filters").click(); }};
      return;
    }}

    lista.forEach(function(c) {{
      var estaEscolhido = false;
      var slotEscolhido = null;
      Object.keys(state.escolhas).forEach(function(sId) {{
        if (state.escolhas[sId] === c.id) {{
          estaEscolhido = true;
          slotEscolhido = sId;
        }}
      }});

      var card = document.createElement("div");
      card.className = "cand-card" + (estaEscolhido ? " in-santinho" : "");

      // Pior status jurídico para o badge
      var piorTipo = "nenhum";
      var piorTitulo = "Sem registros criminais apontados";
      var piorDesc = "Candidatura perante a Justiça Eleitoral sem condenações penais.";
      var piorSeveridade = "baixo";

      if (c.registros_juridicos && c.registros_juridicos.length > 0) {{
        var r = c.registros_juridicos[0];
        piorTipo = r.tipo;
        piorTitulo = r.titulo;
        piorDesc = r.descricao;
        if (r.tipo === "condenado") piorSeveridade = "critico";
        else if (r.tipo === "reu") piorSeveridade = "alto";
        else if (r.tipo === "investigado") piorSeveridade = "medio";
        else if (r.tipo === "boato_noticia") piorSeveridade = "atencao";
      }}

      var badgeJurLabel = "Ficha Limpa";
      if (piorTipo === "boato_noticia") badgeJurLabel = "Boato / Imprensa";
      else if (piorTipo === "investigado") badgeJurLabel = "Em Investigação";
      else if (piorTipo === "reu") badgeJurLabel = "Réu em Ação Penal";
      else if (piorTipo === "condenado") badgeJurLabel = "Condenação Judicial";

      // Espectro badge class
      var espSlug = (c.espectro || "centro").replace(/\\s+/g, "-");
      var espLabel = c.espectro ? c.espectro.charAt(0).toUpperCase() + c.espectro.slice(1) : "Centro";

      // Gênero badge
      var genMap = {{ mulher: "Mulher", homem: "Homem", mulher_trans: "Mulher Trans", homem_trans: "Homem Trans", nao_binario: "Não-Binário" }};
      var genLabel = genMap[c.genero] || "Homem";
      var genBadgeHtml = '<span class="badge-genero genero-' + (c.genero || 'homem') + '">' + genLabel + '</span>';

      // Modelo Bar (se houver)
      var modeloHtml = "";
      if (c.modelo && c.modelo.share_projecao !== null && c.modelo.share_projecao !== undefined) {{
        var pct = (c.modelo.share_projecao * 100).toFixed(1);
        var winPct = c.modelo.chance_eleito !== null && c.modelo.chance_eleito !== undefined ? (c.modelo.chance_eleito * 100).toFixed(0) : null;
        modeloHtml = '<div class="cand-modelo-bar">' +
          '<span>Projeção: <b>' + pct + '%</b></span>' +
          '<div class="modelo-bar-outer"><div class="modelo-bar-inner" style="width: ' + pct + '%;"></div></div>' +
          (winPct ? '<span style="font-size:10.5px;color:var(--ink);">Eleição: <b>' + winPct + '%</b></span>' : '') +
          '</div>';
      }}

      // Causas chips
      var causasHtml = (c.causas || []).slice(0, 4).map(function(cauId) {{
        var cMeta = (META.causas || []).filter(function(x){{ return x.id === cauId; }})[0];
        var lbl = cMeta ? cMeta.label : cauId;
        return '<span class="causa-chip">' + lbl + '</span>';
      }}).join("");

      // Posicionamentos em Pautas (destaques + grade completa)
      var posDestaques = [];
      var pautasTotaisHtml = [];
      (META.pautas || []).forEach(function(pMeta) {{
        var val = (c.posicionamentos && c.posicionamentos[pMeta.id]) || "neutro";
        var icon = val === "favor" ? "✓" : (val === "contra" ? "✗" : "○");
        var txtVal = val === "favor" ? "A favor" : (val === "contra" ? "Contra" : "Neutro");

        if (val !== "neutro" && posDestaques.length < 3) {{
          posDestaques.push('<span class="pos-chip pos-' + val + '">' + icon + ' ' + pMeta.label + '</span>');
        }}
        pautasTotaisHtml.push(
          '<div class="pauta-expanded-item">' +
            '<span class="pauta-expanded-name">' + pMeta.label + '</span>' +
            '<span class="pos-chip pos-' + val + '">' + icon + ' ' + txtVal + '</span>' +
          '</div>'
        );
      }});

      var posicionamentosBoxHtml = 
        '<div class="cand-posicionamentos-box">' +
          '<div class="pos-box-header">' +
            '<span class="pos-box-label">Posicionamento em Pautas</span>' +
            '<span class="pos-box-toggle">Ver todas (15) ▾</span>' +
          '</div>' +
          '<div class="pos-highlights-chips">' +
            (posDestaques.length > 0 ? posDestaques.join("") : '<span style="font-size:10.5px;color:var(--mut);">Sem posições extremas registradas</span>') +
          '</div>' +
          '<div class="pautas-expanded-grid">' +
            pautasTotaisHtml.join("") +
          '</div>' +
        '</div>';

      // Iniciais do Avatar
      var iniciais = (c.urna || "C").split(" ").map(function(w){{ return w[0]; }}).slice(0, 2).join("");

      card.innerHTML = 
        '<div class="cand-top">' +
          '<div class="cand-header-tags">' +
            '<span class="tag-cargo">' + c.cargo.replace("_", " ") + '</span>' +
            '<span class="tag-partido">' + c.partido + '</span>' +
            '<span class="tag-partido" style="color:var(--mut);">' + c.uf + '</span>' +
            genBadgeHtml +
          '</div>' +
          '<div class="cand-numero-badge">' + c.numero + '</div>' +
        '</div>' +
        '<div class="cand-main-info">' +
          '<div class="cand-avatar">' + iniciais + '</div>' +
          '<div class="cand-titles">' +
            '<h3 class="cand-urna">' + c.urna + '</h3>' +
            '<p class="cand-nome-oficial" title="' + c.nome_completo + '">' + c.nome_completo + '</p>' +
          '</div>' +
        '</div>' +
        '<div class="cand-badges-row">' +
          '<span class="badge-pill pill-espectro-' + espSlug + '">' + espLabel + '</span>' +
          (c.vida_pregressa && c.vida_pregressa.status === "reeleicao" ? '<span class="badge-pill pill-vida">Reeleição</span>' : '') +
          (c.atributos && !c.atributos.fundao ? '<span class="badge-pill pill-vida" style="color:var(--win);">Sem Fundão</span>' : '') +
        '</div>' +
        (c.vida_pregressa && c.vida_pregressa.resumo ? '<div class="cand-bio-resumo">' + c.vida_pregressa.resumo + '</div>' : '') +
        '<div class="cand-causas">' + causasHtml + '</div>' +
        posicionamentosBoxHtml +
        '<div class="cand-juridico">' +
          '<div class="juridico-header">' +
            '<span class="juridico-label">Histórico & Ficha</span>' +
            '<span class="juridico-badge status-' + piorSeveridade + '">' + badgeJurLabel + '</span>' +
          '</div>' +
          '<p class="juridico-desc"><b>' + piorTitulo + ':</b> ' + piorDesc + '</p>' +
        '</div>' +
        modeloHtml +
        '<div class="cand-actions">' +
          '<button type="button" class="btn-select-cand">' +
            (estaEscolhido ? '✓ Escolhido para meu Santinho' : '+ Adicionar ao meu Santinho') +
          '</button>' +
        '</div>';

      // Alternar expansão das 15 pautas
      var posBox = card.querySelector(".cand-posicionamentos-box");
      var posHeader = card.querySelector(".pos-box-header");
      var posToggle = card.querySelector(".pos-box-toggle");
      if (posHeader && posBox) {{
        posHeader.onclick = function(e) {{
          e.stopPropagation();
          var isExp = posBox.classList.toggle("expanded");
          posToggle.textContent = isExp ? "Recolher ▴" : "Ver todas (15) ▾";
        }};
      }}

      // Evento de seleção / atribuição ao slot correto
      var btnSel = card.querySelector(".btn-select-cand");
      btnSel.onclick = function() {{
        toggleCandidatoNoSantinho(c);
      }};

      grid.appendChild(card);
    }});
  }}

  // Atribui ou remove candidato dos slots do santinho
  function toggleCandidatoNoSantinho(cand) {{
    // Se já estiver em algum slot, remove
    var slotExistente = null;
    Object.keys(state.escolhas).forEach(function(sId) {{
      if (state.escolhas[sId] === cand.id) slotExistente = sId;
    }});

    if (slotExistente) {{
      delete state.escolhas[slotExistente];
      salvarEscolhas();
      renderSantinhoSlots();
      renderCandidatos();
      return;
    }}

    // Procura slot compatível vago
    var slotAlvo = null;
    if (cand.cargo === "presidente") slotAlvo = "presidente";
    else if (cand.cargo === "governador") slotAlvo = "governador";
    else if (cand.cargo === "deputado_federal") slotAlvo = "deputado_federal";
    else if (cand.cargo === "deputado_estadual") slotAlvo = "deputado_estadual";
    else if (cand.cargo === "senador") {{
      if (!state.escolhas["senador_1"]) slotAlvo = "senador_1";
      else if (!state.escolhas["senador_2"]) slotAlvo = "senador_2";
      else slotAlvo = "senador_1"; // substitui vaga 1
    }}

    if (slotAlvo) {{
      state.escolhas[slotAlvo] = cand.id;
      salvarEscolhas();
      renderSantinhoSlots();
      renderCandidatos();
      // Anima dock
      document.getElementById("santinho-dock").classList.add("open");
      document.getElementById("btn-toggle-dock").textContent = "▼ Recolher";
    }}
  }}

  // Renderiza slots na gaveta do Santinho
  function renderSantinhoSlots() {{
    var gridSlots = document.getElementById("slots-grid");
    gridSlots.innerHTML = "";
    var totalPreenchidos = 0;

    SLOTS_CONFIG.forEach(function(cfg) {{
      var candId = state.escolhas[cfg.id];
      var cand = candId ? CANDIDATOS.filter(function(x){{ return x.id === candId; }})[0] : null;
      if (cand) totalPreenchidos++;

      var sc = document.createElement("div");
      sc.className = "slot-card" + (cand ? " filled" : "");

      if (cand) {{
        sc.innerHTML = 
          '<button type="button" class="slot-remove-btn" title="Remover">✕</button>' +
          '<div class="slot-cargo">' + cfg.label + '</div>' +
          '<div class="slot-numero">' + cand.numero + '</div>' +
          '<div class="slot-nome">' + cand.urna + '</div>' +
          '<div class="slot-partido">' + cand.partido + ' · ' + cand.uf + '</div>';
        
        sc.querySelector(".slot-remove-btn").onclick = function(e) {{
          e.stopPropagation();
          delete state.escolhas[cfg.id];
          salvarEscolhas();
          renderSantinhoSlots();
          renderCandidatos();
        }};
      }} else {{
        sc.innerHTML = 
          '<div class="slot-cargo">' + cfg.label + '</div>' +
          '<div class="slot-numero" style="color:var(--line);">' + ("0".repeat(cfg.digitos)) + '</div>' +
          '<div class="slot-vazio">Toque para filtrar</div>';
        
        sc.style.cursor = "pointer";
        sc.onclick = function() {{
          var cargoTarget = cfg.cargo_filtro || cfg.id;
          state.filtro_cargos = [cargoTarget];
          if (typeof syncCargosGlobal === "function") syncCargosGlobal();
          renderCandidatos();
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }};
      }}

      gridSlots.appendChild(sc);
    }});

    // Atualiza contador do dock
    var counterEl = document.getElementById("dock-counter");
    counterEl.innerHTML = "Meu Santinho: <b>" + totalPreenchidos + " de " + SLOTS_CONFIG.length + "</b> definidos";
  }}

  // Modal da Colinha
  function initColinhaModal() {{
    var modal = document.getElementById("colinha-modal");
    var btnAbrir = document.getElementById("btn-abrir-colinha");
    var btnFechar = document.getElementById("btn-fechar-colinha");
    var btnImprimir = document.getElementById("btn-imprimir-colinha");
    var btnCopiar = document.getElementById("btn-copiar-colinha");

    btnAbrir.onclick = function() {{
      renderColinhaSheet();
      modal.classList.add("open");
    }};

    btnFechar.onclick = function() {{
      modal.classList.remove("open");
    }};

    modal.onclick = function(e) {{
      if (e.target === modal) modal.classList.remove("open");
    }};

    btnImprimir.onclick = function() {{
      window.print();
    }};

    btnCopiar.onclick = function() {{
      var texto = "📋 MEU SANTINHO ELEITORAL 2026\\n\\n";
      SLOTS_CONFIG.sort(function(a,b){{ return a.ordem_urna - b.ordem_urna; }}).forEach(function(cfg) {{
        var cId = state.escolhas[cfg.id];
        var c = cId ? CANDIDATOS.filter(function(x){{ return x.id === cId; }})[0] : null;
        texto += cfg.ordem_urna + ". " + cfg.label + ": ";
        if (c) texto += c.numero + " (" + c.urna + " - " + c.partido + ")\\n";
        else texto += "Não definido\\n";
      }});
      texto += "\\nGerado pelo Ficha do Jogo (bera.ia.br)";

      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(texto).then(function() {{
          var originalHtml = btnCopiar.innerHTML;
          btnCopiar.innerHTML = "✓ Colinha copiada!";
          btnCopiar.style.background = "#15803d";
          btnCopiar.style.color = "#ffffff";
          btnCopiar.style.borderColor = "#15803d";
          setTimeout(function() {{
            btnCopiar.innerHTML = originalHtml;
            btnCopiar.style.background = "";
            btnCopiar.style.color = "";
            btnCopiar.style.borderColor = "";
          }}, 2500);
        }}).catch(function() {{
          prompt("Copie sua colinha abaixo:", texto);
        }});
      }} else {{
        prompt("Copie sua colinha abaixo:", texto);
      }}
    }};
  }}

  function renderColinhaSheet() {{
    var list = document.getElementById("colinha-list");
    list.innerHTML = "";

    // Ordena pela ordem oficial de digitação na urna eletrônica
    var ordenados = SLOTS_CONFIG.slice().sort(function(a,b){{ return a.ordem_urna - b.ordem_urna; }});
    ordenados.forEach(function(cfg) {{
      var cId = state.escolhas[cfg.id];
      var c = cId ? CANDIDATOS.filter(function(x){{ return x.id === cId; }})[0] : null;

      var it = document.createElement("div");
      it.className = "colinha-item";
      it.innerHTML = 
        '<div class="colinha-item-info">' +
          '<div class="colinha-order">' + cfg.ordem_urna + 'º na Urna · ' + cfg.label + '</div>' +
          '<div class="colinha-cand-name">' + (c ? c.urna : '<span style="color:#9ca3af;font-weight:500;">Em branco</span>') + '</div>' +
          '<div class="colinha-cand-party">' + (c ? c.partido + ' (' + c.uf + ')' : 'Toque para escolher') + '</div>' +
        '</div>' +
        '<div class="colinha-cand-num">' + (c ? c.numero : '--') + '</div>';
      
      list.appendChild(it);
    }});
  }}

  // Toggle do dock
  document.getElementById("btn-toggle-dock").onclick = function() {{
    var dock = document.getElementById("santinho-dock");
    var aberto = dock.classList.toggle("open");
    this.textContent = aberto ? "▼ Recolher" : "▲ Abrir gaveta";
  }};

  // Limpar santinho
  document.getElementById("btn-limpar-santinho").onclick = function() {{
    if (confirm("Deseja realmente limpar todos os candidatos do seu santinho?")) {{
      state.escolhas = {{}};
      salvarEscolhas();
      renderSantinhoSlots();
      renderCandidatos();
    }}
  }};

  // Inicializa tudo
  initFilters();
  renderSantinhoSlots();
  renderCandidatos();
  initColinhaModal();

}})();
</script>
{shell.JS}
</body>
</html>
"""

    os.makedirs(DIST, exist_ok=True)
    out_file = os.path.join(DIST, "santinho.html")
    # Higiene editorial: sanitiza qualquer travessão espaçado residual
    doc = doc.replace(" — ", " · ")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"Página do Santinho gerada com sucesso em: {out_file}")

if __name__ == "__main__":
    render_html()
