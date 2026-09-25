#!/usr/bin/env python3
"""Validador de `data/eleicoes/hipoteses.json` (hipóteses pré-especificadas).

Regras, todas verificáveis sem rede:
  - esquema exato por item (15 campos, mais `teste` nas hipóteses de causa), id
    único no padrão h-AAAA-MM-DD-NN, e `registrado_em` igual à data do id;
  - PRÉ-ESPECIFICAÇÃO: a janela começa em ou depois de `registrado_em`. Hipótese
    cuja janela começa antes do registro é retroativa e o arquivo é RECUSADO;
  - alvo: todo sq existe no structure.json e pertence à corrida (ou, em 'MULTI',
    a uma das corridas de origem.corridas);
  - domínio: direção em {+,-}, métrica em {share, eleito, inflexao}, status nos
    válidos, palavra de Kent na escala e número dentro da faixa dela;
  - status != 'aberta' exige `julgado_em` e `evidencia`: ninguém fecha hipótese
    sem dizer com que dado;
  - sem linguagem de causa sobre o passado ("causou", "provocou", "por causa").

v2 (25/09/2026), hipóteses de CAUSA. Uma hipótese com `origem.tipo == "evento"`
liga-se a um evento do registro (`origem.evento_id` tem de existir em
eventos.json) e é OBRIGADA a trazer as três pernas de teste em `teste`:
  - `placebo`: como e quando o M3 compara a janela do evento com janelas placebo
    (depois da apuração);
  - `implicacoes_cruzadas`: quem mais deveria (ou não) ter se movido, cada uma
    com sq, corrida, janela, `esperado` em {move+, move-, nao_move} e um
    `conferido` honesto ({resultado} em {bate, nao_bate, parcial, pendente};
    fora de 'pendente' exige `em` e `evidencia`);
  - `replicacao`: a próxima ocorrência da mesma classe, pré-especificada (janela
    que começa em ou depois do registro, alvo, direção e evento_id, data prevista
    ou condição), ou a declaração `disponivel: false` com `motivo`.
Hipótese de tendência (v1) não pode trazer `teste`: a perna de teste sem evento
seria enfeite.

`--conferir` lê o inflexoes.json publicado e imprime, para cada implicação
cruzada, se o detector bate com o esperado hoje. Só imprime: não escreve, não
julga, não muda status.

Uso:  python3 src/eleicoes_hipoteses.py --check
      python3 src/eleicoes_hipoteses.py --conferir
"""
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
ARQ = os.path.join(ROOT, "data", "eleicoes", "hipoteses.json")
STRUCT = os.path.join(ROOT, "data", "eleicoes2026_structure.json")
EVENTOS = os.path.join(ROOT, "data", "eleicoes", "eventos.json")
INFLEX = os.path.join(ROOT, "data", "eleicoes", "inflexoes.json")

CAMPOS = {"id", "registrado_em", "titulo", "hipotese", "mecanismo", "origem", "corrida", "alvo",
          "direcao_esperada", "metrica", "janela", "limiar_pp", "falsificacao", "probabilidade",
          "status"}
STATUS = {"aberta", "confirmada", "falsa", "nao_testavel"}
METRICAS = {"share", "eleito", "inflexao"}
ESPERADOS = {"move+", "move-", "nao_move"}
RESULTADOS = {"bate", "nao_bate", "parcial", "pendente"}
RX_ID = re.compile(r"^h-(\d{4}-\d{2}-\d{2})-\d{2}$")
RX_CAUSA = re.compile(r"\b(causou|provocou|por causa d[oa]|efeito d[oa] evento)\b", re.I)


def _data(s):
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def _ids_eventos(eventos):
    if eventos is None:
        if not os.path.exists(EVENTOS):
            return set()
        eventos = json.load(open(EVENTOS, encoding="utf-8"))
    return {e.get("id") for e in eventos.get("eventos", [])}


def _valida_teste(tag, h, sq_corrida, ids_ev, reg, prob):
    """As três pernas de teste de uma hipótese de causa."""
    t = h.get("teste")
    if not isinstance(t, dict):
        prob.append(f"{tag}: hipótese de causa sem o bloco `teste` (placebo, implicações "
                    f"cruzadas e replicação são obrigatórios)")
        return
    sobram = set(t) - {"placebo", "implicacoes_cruzadas", "replicacao"}
    if sobram:
        prob.append(f"{tag}: teste com chaves fora do esquema {sorted(sobram)}")
    pl = t.get("placebo")
    if not (isinstance(pl, dict) and pl.get("como") and pl.get("quando")):
        prob.append(f"{tag}: teste.placebo exige `como` e `quando`")
    ic = t.get("implicacoes_cruzadas")
    if not (isinstance(ic, list) and ic):
        prob.append(f"{tag}: teste.implicacoes_cruzadas tem de ser lista não vazia")
        ic = []
    for j, im in enumerate(ic):
        w = f"{tag}: implicação[{j}]"
        sq = im.get("sq")
        if sq not in sq_corrida:
            prob.append(f"{w}: sq {sq} não existe no structure")
        elif im.get("corrida") != sq_corrida[sq]:
            prob.append(f"{w}: sq {sq} é de {sq_corrida[sq]}, não de {im.get('corrida')!r}")
        if im.get("esperado") not in ESPERADOS:
            prob.append(f"{w}: esperado {im.get('esperado')!r} fora de {sorted(ESPERADOS)}")
        jan = im.get("janela") or {}
        ini, fim = _data(jan.get("inicio")), _data(jan.get("fim"))
        if not (ini and fim) or fim < ini:
            prob.append(f"{w}: janela inválida")
        if not im.get("porque"):
            prob.append(f"{w}: falta `porque` (o mecanismo que prevê essa implicação)")
        cf = im.get("conferido") or {}
        if cf.get("resultado") not in RESULTADOS:
            prob.append(f"{w}: conferido.resultado fora de {sorted(RESULTADOS)}")
        elif cf.get("resultado") != "pendente" and not (_data(cf.get("em")) and cf.get("evidencia")):
            prob.append(f"{w}: conferido fora de 'pendente' exige `em` (data) e `evidencia`")
    rp = t.get("replicacao")
    if not isinstance(rp, dict):
        prob.append(f"{tag}: teste.replicacao ausente")
    elif rp.get("disponivel") is False:
        if not rp.get("motivo"):
            prob.append(f"{tag}: replicação indisponível sem `motivo`")
    else:
        if not rp.get("classe"):
            prob.append(f"{tag}: replicação sem `classe`")
        if rp.get("direcao_esperada") not in ("+", "-"):
            prob.append(f"{tag}: replicação com direcao_esperada fora de {{+,-}}")
        for sq in rp.get("alvo") or []:
            if sq not in sq_corrida:
                prob.append(f"{tag}: replicação com sq {sq} inexistente")
        if not rp.get("alvo"):
            prob.append(f"{tag}: replicação sem alvo")
        jan = rp.get("janela") or {}
        ini, fim = _data(jan.get("inicio")), _data(jan.get("fim"))
        if not (ini and fim) or fim < ini:
            prob.append(f"{tag}: replicação com janela inválida")
        elif reg and ini < reg:
            prob.append(f"{tag}: replicação RETROATIVA, a janela ({ini}) começa antes do "
                        f"registro ({reg})")
        if not (rp.get("evento_id") or rp.get("data_prevista") or rp.get("condicao")):
            prob.append(f"{tag}: replicação precisa de evento_id, data_prevista ou condicao")
        if rp.get("evento_id") and rp["evento_id"] not in ids_ev:
            prob.append(f"{tag}: replicação aponta evento_id {rp['evento_id']!r} inexistente")
        if rp.get("data_prevista") and not _data(rp["data_prevista"]):
            prob.append(f"{tag}: replicação com data_prevista que não é ISO")
    if RX_CAUSA.search(json.dumps(t, ensure_ascii=False)):
        prob.append(f"{tag}: linguagem de causa em `teste`")


def validar(doc, structure, eventos=None):
    """Lista de problemas; vazia = válido."""
    prob = []
    races = structure["races"]
    sq_corrida = {c["sq"]: k for k, r in races.items() for c in r["candidates"]}
    ids_ev = _ids_eventos(eventos)
    escala = doc.get("escala_kent") or {}
    for k in ("_doc", "_como_julgar", "hipoteses"):
        if k not in doc:
            prob.append(f"arquivo sem `{k}`")
    ids = set()
    for i, h in enumerate(doc.get("hipoteses", [])):
        tag = h.get("id", f"#{i}")
        faltam = CAMPOS - set(h)
        sobram = set(h) - CAMPOS - {"julgado_em", "evidencia", "teste"}
        if faltam:
            prob.append(f"{tag}: faltam campos {sorted(faltam)}")
        if sobram:
            prob.append(f"{tag}: campos fora do esquema {sorted(sobram)}")
        m = RX_ID.match(str(h.get("id", "")))
        if not m:
            prob.append(f"{tag}: id fora do padrão h-AAAA-MM-DD-NN")
        elif h.get("registrado_em") != m.group(1):
            prob.append(f"{tag}: registrado_em ({h.get('registrado_em')}) difere da data do id")
        if h.get("id") in ids:
            prob.append(f"{tag}: id repetido")
        ids.add(h.get("id"))
        reg = _data(h.get("registrado_em"))
        jan = h.get("janela") or {}
        ini, fim = _data(jan.get("inicio")), _data(jan.get("fim"))
        if not (reg and ini and fim):
            prob.append(f"{tag}: datas inválidas (registrado_em/janela)")
        else:
            if ini < reg:
                prob.append(f"{tag}: RETROATIVA, a janela ({ini}) começa antes do registro ({reg})")
            if fim < ini:
                prob.append(f"{tag}: janela termina antes de começar")
        if h.get("direcao_esperada") not in ("+", "-"):
            prob.append(f"{tag}: direcao_esperada fora de {{+,-}}")
        if h.get("metrica") not in METRICAS:
            prob.append(f"{tag}: metrica fora de {sorted(METRICAS)}")
        if h.get("status") not in STATUS:
            prob.append(f"{tag}: status fora de {sorted(STATUS)}")
        elif h.get("status") != "aberta" and not (h.get("julgado_em") and h.get("evidencia")):
            prob.append(f"{tag}: status '{h.get('status')}' sem julgado_em/evidencia")
        corrida = h.get("corrida")
        origem = h.get("origem") or {}
        permitidas = set(origem.get("corridas") or []) if corrida == "MULTI" else {corrida}
        if corrida != "MULTI" and corrida not in races:
            prob.append(f"{tag}: corrida {corrida!r} não existe")
        if corrida == "MULTI" and len(permitidas) < 2:
            prob.append(f"{tag}: 'MULTI' exige 2+ corridas em origem.corridas")
        alvo = h.get("alvo") or []
        if not alvo:
            prob.append(f"{tag}: alvo vazio")
        for sq in alvo:
            if sq not in sq_corrida:
                prob.append(f"{tag}: sq {sq} não existe no structure")
            elif sq_corrida[sq] not in permitidas:
                prob.append(f"{tag}: sq {sq} é de {sq_corrida[sq]}, não de {sorted(permitidas)}")
        pr = h.get("probabilidade") or {}
        kent, aprox = pr.get("kent"), pr.get("aprox")
        if kent not in escala:
            prob.append(f"{tag}: palavra de Kent {kent!r} fora da escala")
        elif not (isinstance(aprox, (int, float)) and escala[kent][0] <= aprox <= escala[kent][1]):
            prob.append(f"{tag}: aprox {aprox} fora da faixa de {kent!r} {escala[kent]}")
        if not isinstance(h.get("limiar_pp"), (int, float)) or h.get("limiar_pp") < 0:
            prob.append(f"{tag}: limiar_pp inválido")
        for campo in ("hipotese", "mecanismo"):
            if RX_CAUSA.search(h.get(campo, "")):
                prob.append(f"{tag}: linguagem de causa em `{campo}`")
        if " — " in json.dumps(h, ensure_ascii=False):
            prob.append(f"{tag}: travessão espaçado")
        # v2: hipótese de CAUSA
        if origem.get("tipo") == "evento":
            ev_id = origem.get("evento_id")
            if not ev_id:
                prob.append(f"{tag}: origem.tipo 'evento' sem origem.evento_id")
            elif ev_id not in ids_ev:
                prob.append(f"{tag}: origem.evento_id {ev_id!r} não existe em eventos.json")
            _valida_teste(tag, h, sq_corrida, ids_ev, reg, prob)
        elif "teste" in h:
            prob.append(f"{tag}: `teste` só cabe em hipótese de causa (origem.tipo 'evento')")
    return prob


def conferir(doc, infl):
    """Para cada implicação cruzada, o que o detector publicado diz hoje. Só imprime."""
    as_of = _data(infl.get("as_of")) or dt.date.min
    regs = [r for r in infl.get("inflexoes", []) if r.get("corroborado") and r.get("relevante")]
    print(f"inflexoes.json as_of {as_of} · {len(regs)} destaques corroborados e relevantes")
    for h in doc.get("hipoteses", []):
        t = h.get("teste")
        if not t:
            continue
        print(f"\n{h['id']} · {h['titulo']}")
        for im in t.get("implicacoes_cruzadas", []):
            ini, fim = _data(im["janela"]["inicio"]), _data(im["janela"]["fim"])
            hits = [r for r in regs if r["sq"] == im["sq"] and ini <= _data(r["data"]) <= fim]
            pos = [r for r in hits if r["delta_janela_pp"] > 0]
            neg = [r for r in hits if r["delta_janela_pp"] < 0]
            if ini > as_of:
                veredito = "pendente (janela futura)"
            elif im["esperado"] == "nao_move":
                veredito = "bate (sem destaque)" if not hits else f"não bate ({len(hits)} destaque(s))"
            elif im["esperado"] == "move+":
                veredito = f"bate ({len(pos)} positivo(s))" if pos else "não bate (sem destaque positivo)"
            else:
                veredito = f"bate ({len(neg)} negativo(s))" if neg else "não bate (sem destaque negativo)"
            if fim > as_of and ini <= as_of:
                veredito += " · janela ainda aberta"
            decl = (im.get("conferido") or {}).get("resultado", "?")
            print(f"  {im['corrida']:7s} sq {im['sq']} {im['esperado']:8s} {ini}..{fim}  "
                  f"detector: {veredito}  · declarado no arquivo: {decl}")


def main():
    doc = json.load(open(ARQ, encoding="utf-8"))
    st = json.load(open(STRUCT, encoding="utf-8"))
    prob = validar(doc, st)
    n = len(doc.get("hipoteses", []))
    if prob:
        print(f"REPROVADO: {len(prob)} problema(s) em {n} hipótese(s):", file=sys.stderr)
        for p in prob:
            print("  -", p, file=sys.stderr)
        sys.exit(1)
    abertas = sum(1 for h in doc["hipoteses"] if h["status"] == "aberta")
    causa = sum(1 for h in doc["hipoteses"] if (h.get("origem") or {}).get("tipo") == "evento")
    print(f"OK: {n} hipótese(s) válida(s), {abertas} aberta(s), {causa} de causa com as três "
          f"pernas de teste, todas pré-especificadas.")
    if "--conferir" in sys.argv:
        if not os.path.exists(INFLEX):
            print("sem inflexoes.json: nada a conferir")
            return
        conferir(doc, json.load(open(INFLEX, encoding="utf-8")))


if __name__ == "__main__":
    main()
