#!/usr/bin/env python3
"""
Tokens compartilhados do sistema visual "Ficha do Jogo" (Fase 2.5).
FONTE ÚNICA da paleta — dark (padrão) + light (via prefers-color-scheme).
Decisões (2.5): tipografia system-sans; accent da MARCA é "cromo" (rótulos/bordas/chip/links),
nunca em barra de dado. Dark = fundo morno + accent gold; Light = cream + accent verde.
Semânticas (V/E/D, Kent) são var-izadas: mesmo significado, tom ajustado por tema.
Importado por build_bolao / build_comparativo / build_resultados; o dashboard usa o MESMO
conjunto via PAL_DARK_DASH / PAL_LIGHT_DASH (mais tokens, mesmos valores).
"""

# ---- tokens base (bolão / comparativo / resultados) ----
_DARK = {  # fundo VERDE-floresta (Bera 2026-06-09) + accent gold; semânticas fixas.
    "--bg": "#0f1b13", "--card": "#18271d", "--card2": "#132015", "--box": "#0a140d",
    "--line": "#25382b", "--line2": "#17251b",
    "--ink": "#f1ece0", "--mut": "#9fae9d",
    "--ac": "#f3b03c", "--acsoft": "rgba(243,176,60,.12)",
    "--win": "#22c55e", "--draw": "#eab308", "--loss": "#ef4444", "--badge-ink": "#0a140d",
    "--rowhov": "#1d2e22", "--logo-frame": "#f3b03c", "--logo-bar": "#22c55e",
    "--notetx": "#e6efe2", "--dshadow": "rgba(0,0,0,.55)",
}
_LIGHT = {
    "--bg": "#f5f2e6", "--card": "#fffef9", "--card2": "#faf6ea", "--box": "#ece6d6",
    "--line": "#e3ddc8", "--line2": "#ece7d4",
    "--ink": "#23271b", "--mut": "#6f7259",
    "--ac": "#1a7a43", "--acsoft": "rgba(26,122,67,.12)",
    "--win": "#15803d", "--draw": "#b45309", "--loss": "#dc2626", "--badge-ink": "#ffffff",
    "--rowhov": "#f0ece0", "--logo-frame": "#bd8b1f", "--logo-bar": "#16924a",
    "--notetx": "#3a4030", "--dshadow": "rgba(40,30,15,.18)",
}


def _blk(d):
    return ";".join(f"{k}:{v}" for k, v in d.items())


# :root = ESCURO (padrão fixo, NÃO segue o SO). O toggle (#3) seta data-theme=light p/ o tema claro;
# sem isso, fica sempre escuro. color-scheme avisa o browser (scrollbar/controles nativos).
PALETTE = (":root{color-scheme:dark;" + _blk(_DARK) + "}"
           ":root[data-theme=light]{color-scheme:light;" + _blk(_LIGHT) + "}")
