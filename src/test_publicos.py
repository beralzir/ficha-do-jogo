#!/usr/bin/env python3
"""GATE cruzado dos públicos (etapa C1a).

`src/extrai_publicos.py` passou a extrair os 5 públicos direto do PPTX, porque ele
tem 6 dimensões a mais que os `audiencia-*.json` que o Bera já tinha. Trocar de
fonte só é seguro se a fonte nova REPRODUZIR a antiga onde as duas se cobrem.
É isso que este gate exige: divergência de valor FALHA, não vira warn.

O que é comparável, e como:
- por rótulo: ages · interests · mediaHabits · purchaseReasons (rótulos idênticos)
- por posição: genders (Masculino/Feminino vs Homem/Mulher) e socialClasses
  (D vs DE), onde o export traduziu ou reagrupou o rótulo mas manteve a ordem
- escalares: percentWithChildren · percentHigherEducation
- rótulo com typo na FONTE: o PPTX traz "u sempre procuro..." onde o export traz
  "Eu sempre procuro..." (o "E" foi perdido no slide, verificado no XML). Rótulo
  que só difere por prefixo/caixa/espaço casa e vira WARN declarado; os NÚMEROS
  continuam com comparação exata. Typo cosmético não pode derrubar o gate, mas
  também não pode passar em silêncio.
- NÃO comparável: lifeStages, que no export vem em 3 grupos agregados e em inglês
  (PreFamily/Dependent/Family) e no PPTX em 5 estágios detalhados em português.
  São recortes diferentes do mesmo dado, e o gate declara isso em vez de fingir
  que confere.

Uso:  python3 src/test_publicos.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
EXTRAIDO = os.path.join(ROOT, "data", "publicos", "audiencias.json")
# Fonte no repo desde 21/09/2026 (ver extrai_publicos.py). Com isto este gate
# passa a rodar no CI, o que era impossível enquanto dependia do iCloud.
REF_DIR = os.environ.get("PUBLICOS_REF_DIR",
                         os.path.join(ROOT, "data", "publicos", "fonte"))

POR_ROTULO = [("ages", "idades", "label"), ("interests", "interesses", "description"),
              ("mediaHabits", "habitos_midia", "description"),
              ("purchaseReasons", "prioridades_voto", "description")]
POR_POSICAO = [("genders", "generos"), ("socialClasses", "classes_sociais")]
# publicDefinition NÃO entra: no export é um resumo curado curto e no PPTX é a
# definição longa do slide. São textos diferentes, não versões do mesmo (o
# extrator guarda os dois, em publicDefinition e definicaoDeck).
ESCALARES = ["percentWithChildren", "percentHigherEducation"]

FALHAS, WARNS = [], []


def falha(msg):
    print(f"  FALHA {msg}")
    FALHAS.append(msg)


def _cosmetico(a, b):
    """Rótulos que diferem só por prefixo curto, caixa ou espaço: typo da fonte."""
    na, nb = " ".join(a.split()).lower(), " ".join(b.split()).lower()
    if na == nb:
        return True
    curto, longo = (na, nb) if len(na) < len(nb) else (nb, na)
    return longo.endswith(curto) and len(longo) - len(curto) <= 3


def rot(x):
    return x.get("label") or x.get("description") or x.get("stage") or x.get("class")


def compara(slug, ref, ext):
    # 1. dimensões cujos rótulos são idênticos nos dois lados
    for jk, mk, chave in POR_ROTULO:
        a = {r[chave]: r for r in ref.get(jk, [])}
        b = {rot(r): r for r in ext.get(mk, [])}
        if set(a) != set(b):
            sob_a, sob_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
            for ka in list(sob_a):              # tenta casar typo cosmético
                alvo = next((kb for kb in sob_b if _cosmetico(ka, kb)), None)
                if alvo:
                    b[ka] = b.pop(alvo)
                    sob_a.remove(ka); sob_b.remove(alvo)
                    WARNS.append(f"{slug}/{jk}: rótulo com typo na FONTE, "
                                 f"export={ka!r} PPTX={alvo!r}; números conferidos")
            if sob_a or sob_b:
                falha(f"{slug}/{jk}: conjunto de rótulos difere "
                      f"(só no export: {sob_a[:3]}; só no PPTX: {sob_b[:3]})")
                continue
        for k in sorted(a):
            for campo in ("percent", "affinityScore"):
                va, vb = a[k].get(campo), b[k].get(campo)
                if va is None and vb is None:
                    continue
                if va is None or vb is None or abs(float(va) - float(vb)) > 0.051:
                    falha(f"{slug}/{jk}/{k}/{campo}: export={va} PPTX={vb}")

    # 2. dimensões em que o rótulo mudou mas a ordem se manteve
    for jk, mk in POR_POSICAO:
        a, b = ref.get(jk, []), ext.get(mk, [])
        if len(a) != len(b):
            falha(f"{slug}/{jk}: {len(a)} linhas no export contra {len(b)} no PPTX")
            continue
        for i, (ra, rb) in enumerate(zip(a, b)):
            for campo in ("percent", "affinityScore"):
                va, vb = ra.get(campo), rb.get(campo)
                if va is None or vb is None or abs(float(va) - float(vb)) > 0.051:
                    falha(f"{slug}/{jk}[{i}] ({rot(ra)} vs {rot(rb)})/{campo}: "
                          f"export={va} PPTX={vb}")

    # 3. escalares
    for campo in ESCALARES:
        va, vb = ref.get(campo), ext.get(campo)
        if isinstance(va, str):
            if (va or "").strip() != (vb or "").strip():
                falha(f"{slug}/{campo}: texto difere")
        elif va is None or vb is None or abs(float(va) - float(vb)) > 0.051:
            falha(f"{slug}/{campo}: export={va} PPTX={vb}")

    # 4. lifeStages: recorte diferente, declarado e não comparado.
    a = {r.get("stage"): r for r in ref.get("lifeStages", [])}
    b = {rot(r): r for r in ext.get("estagios_vida", [])}
    casados = sum(1 for ra in a.values()
                  for rb in b.values()
                  if abs(float(ra["percent"]) - float(rb["percent"])) <= 0.051
                  and ra.get("affinityScore") == rb.get("affinityScore"))
    WARNS.append(f"{slug}/lifeStages: recorte diferente (export {len(a)} grupos agregados "
                 f"em inglês, PPTX {len(b)} estágios em português); {casados} linha(s) "
                 f"coincidem em valor")


def main():
    doc = json.load(open(EXTRAIDO, encoding="utf-8"))
    ext = {p["slug"]: p for p in doc["publicos"]}
    print(f"gate cruzado: {len(ext)} públicos extraídos do PPTX vs os audiencia-*.json\n")

    vistos = 0
    for slug, p in sorted(ext.items()):
        caminho = os.path.join(REF_DIR, f"audiencia-{slug}.json")
        if not os.path.exists(caminho):
            falha(f"{slug}: referência não encontrada em {caminho}")
            continue
        ref = json.load(open(caminho, encoding="utf-8"))
        if (ref.get("name") or "").strip() != p["name"].strip():
            falha(f"{slug}/name: export={ref.get('name')!r} PPTX={p['name']!r}")
        compara(slug, ref, p)
        vistos += 1
        print(f"  ok   {slug}")

    if vistos != 5:
        falha(f"esperava 5 públicos conferidos, conferi {vistos}")

    # invariantes próprios do extrato
    print()
    for p in doc["publicos"]:
        soma = sum(x["percent"] for x in p.get("generos", []))
        if abs(soma - 100.0) > 0.6:
            falha(f"{p['slug']}: gêneros somam {soma:.1f}%, esperado ~100%")
        if not p.get("universo") or p["universo"] < 1_000_000:
            falha(f"{p['slug']}: universo implausível ({p.get('universo')})")
        faltando = [k for k in ("generos", "idades", "racas", "estados_civis",
                                "estagios_vida", "classes_sociais", "religioes",
                                "interesses", "habitos_midia", "prioridades_voto")
                    if not p.get(k)]
        if faltando:
            falha(f"{p['slug']}: dimensões vazias: {faltando}")
    total = sum(p["universo"] for p in doc["publicos"])
    print(f"  ok   universo somado: {total:,}".replace(",", ".") + " eleitores (5 clusters)")

    for w in WARNS:
        print(f"  WARN {w}")
    print()
    if FALHAS:
        print(f"GATE REPROVADO: {len(FALHAS)} divergência(s).")
        sys.exit(1)
    print(f"OK: 5 públicos, 10 dimensões cada, conferidos contra os audiencia-*.json "
          f"({len(WARNS)} warn declarado).")


if __name__ == "__main__":
    main()
