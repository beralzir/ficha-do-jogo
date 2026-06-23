#!/usr/bin/env python3
"""Set de BANDEIRAS em SVG inline (substitui os emojis de bandeira, que NÃO renderizam no Windows —
o SO não traz fonte de bandeira de país). Desenhadas via huashu-design: simplificadas/vexilológicas,
legíveis como chip ~18px (proporção 4:3), funcionam em tema escuro E claro.

CONTRATO ZERO-DEP (o verificador do atualizar.sh rejeita qualquer `https?://` que não seja a licença CC):
- SVG inline em HTML → SEM `xmlns`, SEM `xlink`, SEM nenhuma URL http(s). Só referência por FRAGMENTO.
- Cada bandeira é um `<symbol id="fl-xx" viewBox="0 0 4 3">`; o uso é `<svg class="fi"><use href="#fl-xx"/></svg>`.
- `SPRITE` entra UMA vez por página (no body, antes do conteúdo). `CSS` (.fi) vai no shell (compartilhado).

Fonte única: `ISO` mapeia nome-EN canônico → id. Importado por pt.py e build_dashboard.py (que sobrescrevem
PT[t][0] = ref(t)). Determinístico (sem aleatório; iteração sobre dict literal preserva ordem de inserção)."""
import math

# nome-EN canônico (as 48 seleções) -> id do símbolo (ISO-2, + subdivisões eng/sct).
ISO = {
    "Spain": "es", "France": "fr", "Argentina": "ar", "England": "eng", "Portugal": "pt",
    "Brazil": "br", "Germany": "de", "Netherlands": "nl", "Belgium": "be", "Norway": "no",
    "Colombia": "co", "Japan": "jp", "Morocco": "ma", "United States": "us", "Uruguay": "uy",
    "Mexico": "mx", "Switzerland": "ch", "Croatia": "hr", "Turkey": "tr", "Ecuador": "ec",
    "Senegal": "sn", "Sweden": "se", "Austria": "at", "Canada": "ca", "Paraguay": "py",
    "Ivory Coast": "ci", "Egypt": "eg", "Algeria": "dz", "Scotland": "sct", "Czechia": "cz",
    "Bosnia and Herzegovina": "ba", "Ghana": "gh", "South Korea": "kr", "Iran": "ir",
    "Tunisia": "tn", "Australia": "au", "DR Congo": "cd", "Cape Verde": "cv", "Iraq": "iq",
    "Jordan": "jo", "New Zealand": "nz", "Panama": "pa", "Qatar": "qa", "Saudi Arabia": "sa",
    "South Africa": "za", "Uzbekistan": "uz", "Curacao": "cw", "Haiti": "ht",
}

# sigla de 3 letras (código FIFA) -> rótulo na ponta da linha do poll tracker (build_resultados).
# Determinístico; cobre as mesmas 48. (FIFA: KSA/RSA/TUR/COD/CUW/HAI/CPV/CIV diferem do ISO-3 alfa.)
ISO3 = {
    "Spain": "ESP", "France": "FRA", "Argentina": "ARG", "England": "ENG", "Portugal": "POR",
    "Brazil": "BRA", "Germany": "GER", "Netherlands": "NED", "Belgium": "BEL", "Norway": "NOR",
    "Colombia": "COL", "Japan": "JPN", "Morocco": "MAR", "United States": "USA", "Uruguay": "URU",
    "Mexico": "MEX", "Switzerland": "SUI", "Croatia": "CRO", "Turkey": "TUR", "Ecuador": "ECU",
    "Senegal": "SEN", "Sweden": "SWE", "Austria": "AUT", "Canada": "CAN", "Paraguay": "PAR",
    "Ivory Coast": "CIV", "Egypt": "EGY", "Algeria": "ALG", "Scotland": "SCO", "Czechia": "CZE",
    "Bosnia and Herzegovina": "BIH", "Ghana": "GHA", "South Korea": "KOR", "Iran": "IRN",
    "Tunisia": "TUN", "Australia": "AUS", "DR Congo": "COD", "Cape Verde": "CPV", "Iraq": "IRQ",
    "Jordan": "JOR", "New Zealand": "NZL", "Panama": "PAN", "Qatar": "QAT", "Saudi Arabia": "KSA",
    "South Africa": "RSA", "Uzbekistan": "UZB", "Curacao": "CUW", "Haiti": "HAI",
}


def code3(name):
    """Sigla de 3 letras da seleção (fallback: 3 primeiras letras em maiúsculas)."""
    return ISO3.get(name) or name[:3].upper()


def _star(cx, cy, r, fill):  # estrela de 5 pontas (unitária, ponta p/ cima), escalada+transladada
    return (f'<g transform="translate({cx:g} {cy:g}) scale({r:g})">'
            '<polygon points="0,-1 .225,-.31 .951,-.309 .363,.118 .588,.809 0,.382 '
            '-.588,.809 -.363,.118 -.951,-.309 -.225,-.31" fill="' + fill + '"/></g>')


# --- peças compostas (montadas em código p/ não poluir o dict) ---
# EUA: 13 listras + cantão azul + estrelas (pontos brancos, legíveis a 18px).
_US = ('<rect width="4" height="3" fill="#b22234"/>'
       + ''.join(f'<rect y="{i*0.2308:.4g}" width="4" height=".2308" fill="#fff"/>' for i in (1, 3, 5, 7, 9, 11))
       + '<rect width="1.6" height="1.6156" fill="#3c3b6e"/>'
       + ''.join(f'<circle cx="{x:g}" cy="{y:g}" r=".058" fill="#fff"/>'
                 for y in (0.34, 0.68, 1.02, 1.36) for x in (0.27, 0.67, 1.07, 1.47)))
# Cabo Verde: anel de 10 estrelas amarelas sobre a faixa.
_CV = ('<rect width="4" height="3" fill="#003893"/><rect y="1.5" width="4" height=".62" fill="#fff"/>'
       '<rect y="1.71" width="4" height=".2" fill="#cf2027"/>'
       + ''.join(_star(round(1.5 + 0.56 * math.cos(math.radians(a)), 3),
                       round(1.81 + 0.56 * math.sin(math.radians(a)), 3), 0.13, "#f7d617")
                 for a in range(-90, 270, 36)))
# Union Jack simplificado (cantão 0..1.8 x 0..1.35) — reutilizado por Austrália/Nova Zelândia.
_UJ = ('<path d="M0,0 1.8,1.35 M1.8,0 0,1.35" stroke="#fff" stroke-width=".26"/>'
       '<path d="M0,0 1.8,1.35 M1.8,0 0,1.35" stroke="#cf142b" stroke-width=".1"/>'
       '<path d="M.9,0 .9,1.35 M0,.675 1.8,.675" stroke="#fff" stroke-width=".34"/>'
       '<path d="M.9,0 .9,1.35 M0,.675 1.8,.675" stroke="#cf142b" stroke-width=".18"/>')
_AU = ('<rect width="4" height="3" fill="#00247d"/>' + _UJ + _star(0.9, 2.25, 0.36, "#fff")
       + _star(3.05, 0.62, 0.17, "#fff") + _star(3.5, 1.25, 0.17, "#fff")
       + _star(2.95, 1.85, 0.15, "#fff") + _star(3.55, 2.4, 0.15, "#fff") + _star(3.2, 1.1, 0.1, "#fff"))
_NZ = ('<rect width="4" height="3" fill="#00247d"/>' + _UJ
       + ''.join(_star(x, y, 0.2, "#fff") + _star(x, y, 0.12, "#cf142b")
                 for x, y in ((3.1, 0.65), (3.55, 1.45), (2.95, 1.95), (3.45, 2.4))))

# --- as 48 bandeiras (inner SVG de cada <symbol viewBox="0 0 4 3">) ---
_SYM = {
    "es": '<rect width="4" height="3" fill="#c60b1e"/><rect y=".75" width="4" height="1.5" fill="#ffc400"/>',
    "fr": '<rect width="4" height="3" fill="#fff"/><rect width="1.34" height="3" fill="#002395"/>'
          '<rect x="2.66" width="1.34" height="3" fill="#ed2939"/>',
    "ar": '<rect width="4" height="3" fill="#74acdf"/><rect y="1" width="4" height="1" fill="#fff"/>'
          '<circle cx="2" cy="1.5" r=".27" fill="#f6b40e"/>',
    "eng": '<rect width="4" height="3" fill="#fff"/><rect x="1.65" width=".7" height="3" fill="#ce1124"/>'
           '<rect y="1.15" width="4" height=".7" fill="#ce1124"/>',
    "pt": '<rect width="4" height="3" fill="#da291c"/><rect width="1.6" height="3" fill="#046a38"/>'
          '<circle cx="1.6" cy="1.5" r=".42" fill="#ffe000"/><circle cx="1.6" cy="1.5" r=".21" fill="#fff"/>'
          '<circle cx="1.6" cy="1.5" r=".1" fill="#da291c"/>',
    "br": '<rect width="4" height="3" fill="#009c3b"/><polygon points="2,.36 3.64,1.5 2,2.64 .36,1.5" fill="#ffdf00"/>'
          '<circle cx="2" cy="1.5" r=".6" fill="#002776"/>',
    "de": '<rect width="4" height="3" fill="#000"/><rect y="1" width="4" height="1" fill="#dd0000"/>'
          '<rect y="2" width="4" height="1" fill="#ffce00"/>',
    "nl": '<rect width="4" height="3" fill="#fff"/><rect width="4" height="1" fill="#ae1c28"/>'
          '<rect y="2" width="4" height="1" fill="#21468b"/>',
    "be": '<rect width="4" height="3" fill="#000"/><rect x="1.34" width="1.32" height="3" fill="#fae042"/>'
          '<rect x="2.66" width="1.34" height="3" fill="#ed2939"/>',
    "no": '<rect width="4" height="3" fill="#ba0c2f"/><rect x="1" width=".8" height="3" fill="#fff"/>'
          '<rect y="1.1" width="4" height=".8" fill="#fff"/><rect x="1.2" width=".4" height="3" fill="#00205b"/>'
          '<rect y="1.3" width="4" height=".4" fill="#00205b"/>',
    "co": '<rect width="4" height="3" fill="#fcd116"/><rect y="1.5" width="4" height=".75" fill="#003893"/>'
          '<rect y="2.25" width="4" height=".75" fill="#ce1126"/>',
    "jp": '<rect width="4" height="3" fill="#fff"/><circle cx="2" cy="1.5" r=".72" fill="#bc002d"/>',
    "ma": '<rect width="4" height="3" fill="#c1272d"/>' + _star(2, 1.5, 0.62, "#006233"),
    "us": _US,
    "uy": '<rect width="4" height="3" fill="#fff"/><rect y=".58" width="4" height=".3" fill="#0038a8"/>'
          '<rect y="1.16" width="4" height=".3" fill="#0038a8"/><rect y="1.74" width="4" height=".3" fill="#0038a8"/>'
          '<rect y="2.32" width="4" height=".3" fill="#0038a8"/><rect width="1.5" height="1.35" fill="#fff"/>'
          '<circle cx=".75" cy=".67" r=".32" fill="#f6b40e"/>',
    "mx": '<rect width="4" height="3" fill="#fff"/><rect width="1.34" height="3" fill="#006847"/>'
          '<rect x="2.66" width="1.34" height="3" fill="#ce1126"/><circle cx="2" cy="1.5" r=".22" fill="#8b5a2b"/>',
    "ch": '<rect width="4" height="3" fill="#d52b1e"/><rect x="1.75" y=".75" width=".5" height="1.5" fill="#fff"/>'
          '<rect x="1.25" y="1.25" width="1.5" height=".5" fill="#fff"/>',
    "hr": '<rect width="4" height="3" fill="#fff"/><rect width="4" height="1" fill="#ff0000"/>'
          '<rect y="2" width="4" height="1" fill="#171796"/><rect x="1.74" y="1.04" width=".26" height=".31" fill="#ff0000"/>'
          '<rect x="2" y="1.35" width=".26" height=".31" fill="#ff0000"/><rect x="1.74" y="1.66" width=".26" height=".3" fill="#ff0000"/>',
    "tr": '<rect width="4" height="3" fill="#e30a17"/><circle cx="1.75" cy="1.5" r=".6" fill="#fff"/>'
          '<circle cx="1.95" cy="1.5" r=".48" fill="#e30a17"/>' + _star(2.55, 1.5, 0.3, "#fff"),
    "ec": '<rect width="4" height="3" fill="#ffdd00"/><rect y="1.5" width="4" height=".75" fill="#034ea2"/>'
          '<rect y="2.25" width="4" height=".75" fill="#ed1c24"/><circle cx="2" cy="1.5" r=".18" fill="#896a2f"/>',
    "sn": '<rect width="4" height="3" fill="#00853f"/><rect x="1.34" width="1.32" height="3" fill="#fdef42"/>'
          '<rect x="2.66" width="1.34" height="3" fill="#e31b23"/>' + _star(2, 1.5, 0.45, "#00853f"),
    "se": '<rect width="4" height="3" fill="#006aa7"/><rect x="1" width=".7" height="3" fill="#fecc00"/>'
          '<rect y="1.15" width="4" height=".7" fill="#fecc00"/>',
    "at": '<rect width="4" height="3" fill="#ed2939"/><rect y="1" width="4" height="1" fill="#fff"/>',
    "ca": '<rect width="4" height="3" fill="#fff"/><rect width="1" height="3" fill="#ff0000"/>'
          '<rect x="3" width="1" height="3" fill="#ff0000"/>'
          '<polygon points="2,.5 2.09,1.05 2.42,.78 2.27,1.2 2.62,1.18 2.32,1.5 2.62,1.82 2.27,1.8 '
          '2.42,2.22 2.09,1.95 2,2.5 1.91,1.95 1.58,2.22 1.73,1.8 1.38,1.82 1.68,1.5 1.38,1.18 '
          '1.73,1.2 1.58,.78 1.91,1.05" fill="#ff0000"/>',
    "py": '<rect width="4" height="3" fill="#fff"/><rect width="4" height="1" fill="#d52b1e"/>'
          '<rect y="2" width="4" height="1" fill="#0038a8"/>' + _star(2, 1.5, 0.24, "#f6b40e"),
    "ci": '<rect width="4" height="3" fill="#fff"/><rect width="1.34" height="3" fill="#f77f00"/>'
          '<rect x="2.66" width="1.34" height="3" fill="#009e60"/>',
    "eg": '<rect width="4" height="3" fill="#fff"/><rect width="4" height="1" fill="#ce1126"/>'
          '<rect y="2" width="4" height="1" fill="#000"/><circle cx="2" cy="1.5" r=".2" fill="#c09300"/>',
    "dz": '<rect width="4" height="3" fill="#fff"/><rect width="2" height="3" fill="#006233"/>'
          '<circle cx="2.18" cy="1.5" r=".5" fill="#d21034"/><circle cx="2.36" cy="1.5" r=".4" fill="#fff"/>'
          + _star(2.52, 1.5, 0.22, "#d21034"),
    "sct": '<rect width="4" height="3" fill="#0065bf"/><path d="M0,0 4,3 M4,0 0,3" stroke="#fff" stroke-width=".55"/>',
    "cz": '<rect width="4" height="3" fill="#fff"/><rect y="1.5" width="4" height="1.5" fill="#d7141a"/>'
          '<polygon points="0,0 2,1.5 0,3" fill="#11457e"/>',
    "ba": '<rect width="4" height="3" fill="#002395"/><polygon points="1.2,0 3.4,0 1.2,3" fill="#fecb00"/>'
          + ''.join(_star(x, y, 0.12, "#fff") for x, y in ((1.55, 2.5), (1.95, 1.9), (2.35, 1.3), (2.75, 0.7))),
    "gh": '<rect width="4" height="3" fill="#fcd116"/><rect width="4" height="1" fill="#ce1126"/>'
          '<rect y="2" width="4" height="1" fill="#006b3f"/>' + _star(2, 1.5, 0.42, "#000"),
    "kr": '<rect width="4" height="3" fill="#fff"/><circle cx="2" cy="1.5" r=".6" fill="#cd2e3a"/>'
          '<path d="M1.4,1.5 a.6,.6 0 0,0 1.2,0" fill="#0047a0"/>'
          '<circle cx="1.7" cy="1.5" r=".3" fill="#cd2e3a"/><circle cx="2.3" cy="1.5" r=".3" fill="#0047a0"/>',
    "ir": '<rect width="4" height="3" fill="#fff"/><rect width="4" height="1" fill="#239f40"/>'
          '<rect y="2" width="4" height="1" fill="#da0000"/><circle cx="2" cy="1.5" r=".17" fill="#da0000"/>',
    "tn": '<rect width="4" height="3" fill="#e70013"/><circle cx="2" cy="1.5" r=".72" fill="#fff"/>'
          '<circle cx="2.12" cy="1.5" r=".46" fill="#e70013"/><circle cx="2.27" cy="1.5" r=".36" fill="#fff"/>'
          + _star(2.12, 1.5, 0.22, "#e70013"),
    "au": _AU,
    "cd": '<rect width="4" height="3" fill="#007fff"/><path d="M0,3 4,0" stroke="#f7d618" stroke-width=".7"/>'
          '<path d="M0,3 4,0" stroke="#ce1021" stroke-width=".38"/>' + _star(0.55, 0.6, 0.3, "#f7d618"),
    "cv": _CV,
    "iq": '<rect width="4" height="3" fill="#fff"/><rect width="4" height="1" fill="#ce1126"/>'
          '<rect y="2" width="4" height="1" fill="#000"/><g fill="#007a3d"><circle cx="1.55" cy="1.5" r=".11"/>'
          '<circle cx="2" cy="1.5" r=".11"/><circle cx="2.45" cy="1.5" r=".11"/></g>',
    "jo": '<rect width="4" height="3" fill="#fff"/><rect width="4" height="1" fill="#000"/>'
          '<rect y="2" width="4" height="1" fill="#007a3d"/><polygon points="0,0 1.9,1.5 0,3" fill="#ce1126"/>'
          + _star(0.62, 1.5, 0.2, "#fff"),
    "nz": _NZ,
    "pa": '<rect width="4" height="3" fill="#fff"/><rect x="2" width="2" height="1.5" fill="#d21034"/>'
          '<rect y="1.5" width="2" height="1.5" fill="#005293"/>' + _star(1, 0.75, 0.4, "#005293")
          + _star(3, 2.25, 0.4, "#d21034"),
    "qa": '<rect width="4" height="3" fill="#8a1538"/><rect width="1.25" height="3" fill="#fff"/>'
          '<polygon points="1.25,0 1.55,.375 1.25,.75 1.55,1.125 1.25,1.5 1.55,1.875 1.25,2.25 1.55,2.625 1.25,3" fill="#8a1538"/>',
    "sa": '<rect width="4" height="3" fill="#006c35"/><rect x=".55" y="1.9" width="2.9" height=".13" fill="#fff"/>'
          '<g fill="#fff"><rect x=".7" y="1.2" width=".3" height=".12"/><rect x="1.1" y="1.15" width=".5" height=".12"/>'
          '<rect x="1.7" y="1.2" width=".4" height=".12"/><rect x="2.2" y="1.15" width=".5" height=".12"/>'
          '<rect x="2.8" y="1.2" width=".4" height=".12"/></g>',
    "za": '<rect width="4" height="3" fill="#fff"/><rect width="4" height="1" fill="#de3831"/>'
          '<rect y="2" width="4" height="1" fill="#002395"/><rect y="1.1" width="4" height=".8" fill="#007a4d"/>'
          '<polygon points="0,0 1.55,1.5 0,3" fill="#ffb612"/><polygon points="0,.22 1.25,1.5 0,2.78" fill="#000"/>',
    "uz": '<rect width="4" height="3" fill="#fff"/><rect width="4" height=".95" fill="#0099b5"/>'
          '<rect y="2.05" width="4" height=".95" fill="#1eb53a"/><rect y=".95" width="4" height=".06" fill="#ce1126"/>'
          '<rect y="1.99" width="4" height=".06" fill="#ce1126"/><circle cx=".7" cy=".48" r=".28" fill="#fff"/>'
          '<circle cx=".84" cy=".48" r=".22" fill="#0099b5"/>',
    "cw": '<rect width="4" height="3" fill="#002b7f"/><rect y="1.95" width="4" height=".5" fill="#f9d90f"/>'
          + _star(0.65, 0.75, 0.22, "#fff") + _star(1.05, 1.2, 0.16, "#fff"),
    "ht": '<rect width="4" height="3" fill="#00209f"/><rect y="1.5" width="4" height="1.5" fill="#d21034"/>'
          '<rect x="1.4" y="1.02" width="1.2" height=".96" fill="#fff"/><circle cx="2" cy="1.5" r=".18" fill="#007a3d"/>',
}

# sprite: entra UMA vez por página (body). position:absolute+0x0 (NÃO display:none — referência via <use> falha em alguns navegadores).
SPRITE = ('<svg class="fdj-flags" aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden">'
          + ''.join(f'<symbol id="fl-{k}" viewBox="0 0 4 3">{v}</symbol>' for k, v in _SYM.items())
          + '</svg>')

# CSS do chip (vai no shell, compartilhado). 4:3, escala com font-size; hairline serve p/ bandeiras claras nos 2 temas.
CSS = (".fi{display:inline-block;width:1.34em;height:1em;vertical-align:-.14em;border-radius:2px;"
       "overflow:hidden;box-shadow:0 0 0 1px rgba(128,128,128,.3)}")


def ref(name):
    """Snippet de uso da bandeira (vai em PT[name][0]). Funciona em HTML estático E em innerHTML (JS)."""
    return f'<svg class="fi" aria-hidden="true"><use href="#fl-{ISO[name]}"/></svg>'


if __name__ == "__main__":  # auto-teste: cobertura + contrato zero-dep
    assert len(ISO) == 48 and len(_SYM) == 48, (len(ISO), len(_SYM))
    miss = [n for n in ISO if ISO[n] not in _SYM]
    assert not miss, f"sem símbolo: {miss}"
    bad = [c for c in ("xmlns", "xlink", "http", "://") if c in SPRITE or c in CSS]
    assert not bad, f"viola zero-dep: {bad}"
    # ISO3: cobre as mesmas 48, todas 3 letras maiúsculas, sem colisão.
    assert set(ISO3) == set(ISO), f"ISO3 difere de ISO: {set(ISO) ^ set(ISO3)}"
    assert all(len(v) == 3 and v.isupper() for v in ISO3.values()), "sigla deve ter 3 letras maiúsculas"
    assert len(set(ISO3.values())) == 48, f"siglas duplicadas: {len(set(ISO3.values()))}"
    print(f"flags OK: {len(ISO)} bandeiras · {len(ISO3)} siglas · sprite {len(SPRITE)} chars · 0 xmlns/xlink/http")
