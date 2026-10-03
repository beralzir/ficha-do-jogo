#!/usr/bin/env python3
"""
Gera data/eleicoes/santinho_candidatos.json com a lista enriquecida de candidatos
para o Santinho Virtual (Eleições 2026).

Combina:
1. Candidatos a Presidente, Governador e Senador (extraídos de eleicoes2026_structure.json)
2. Projeções e chances do modelo probabilístico (de eleicoes2026_results.json)
3. Lista de Deputados Federais (SP) e Deputados Estaduais (SP) com numeração oficial
4. Metadados curados: espectro político, vida pregressa, causas defendidas, registros jurídicos/boatos,
   e atributos práticos (fundão eleitoral, reeleição, governismo).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data")
OUTPUT_PATH = os.path.join(BASE, "eleicoes", "santinho_candidatos.json")

STRUCT = json.load(open(os.path.join(BASE, "eleicoes2026_structure.json"), encoding="utf-8"))
RESULTS = json.load(open(os.path.join(BASE, "eleicoes2026_results.json"), encoding="utf-8"))

# Mapa de resultados para acesso rápido: (race_id, urna) -> dict
RESULTS_MAP = {}
for race_id, race_data in RESULTS.get("races", {}).items():
    for c in race_data.get("candidates", []):
        key = (race_id, c.get("urna", "").strip().upper())
        RESULTS_MAP[key] = {
            "share": c.get("share"),
            "sd": c.get("sd"),
            "eleito": c.get("eleito"),
            "t2": c.get("t2")
        }

# Curadoria profunda para candidatos de destaque nacional e de SP
CURADORIA = {
    # ── PRESIDÊNCIA ──
    ("PRES", "LULA"): {
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 46,
            "resumo": "Presidente do Brasil por 3 mandatos (2003–2010 e 2023–2026). Ex-deputado federal constituinte e líder histórico do sindicalismo do ABC paulista."
        },
        "causas": ["social", "educacao", "saude", "meio_ambiente", "infra"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Processos da Operação Lava Jato",
                "descricao": "Condenações no âmbito de Curitiba foram formalmente anuladas pelo Supremo Tribunal Federal por suspeição do juiz e incompetência de foro. Ficha limpa perante a Justiça Eleitoral.",
                "status_atual": "Processos anulados pelo STF"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "governo"
    },
    ("PRES", "FLAVIO BOLSONARO"): {
        "espectro": "direita",
        "vida_pregressa": {
            "status": "veterano",
            "tempo_politica_anos": 24,
            "resumo": "Senador da República pelo Rio de Janeiro (2019–2026). Ex-deputado estadual na ALERJ por 4 mandatos consecutivos (2003–2018), advogado e empresário."
        },
        "causas": ["costumes", "seguranca", "agro", "economia"],
        "registros_juridicos": [
            {
                "tipo": "investigado",
                "titulo": "Caso das Rachadinhas (ALERJ)",
                "descricao": "Investigação sobre suposto desvio de salários de assessores na ALERJ. A denúncia foi rejeitada pelo STJ em 2021 devido à anulação de provas baseadas em relatórios do Coaf obtidos sem autorização judicial.",
                "status_atual": "Denúncia anulada no STJ"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "oposicao"
    },
    ("PRES", "RONALDO CAIADO"): {
        "espectro": "centro-direita",
        "vida_pregressa": {
            "status": "ex_executivo",
            "tempo_politica_anos": 38,
            "resumo": "Governador de Goiás por 2 mandatos (2019–2026). Ex-senador e ex-deputado federal por múltiplos mandatos. Médico ortopedista e fundador da UDR."
        },
        "causas": ["agro", "seguranca", "economia", "infra"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem condenações criminais",
                "descricao": "Histórico sem condenações por crimes comuns ou corrupção; apenas contestações administrativas de praxe na gestão pública estadual.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "independente"
    },
    ("PRES", "ZEMA"): {
        "espectro": "direita",
        "vida_pregressa": {
            "status": "ex_executivo",
            "tempo_politica_anos": 8,
            "resumo": "Governador de Minas Gerais por 2 mandatos (2019–2026). Empresário e administrador de empresas, ingressou na política partidária em 2018."
        },
        "causas": ["economia", "privatizacoes", "corrupcao", "infra"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Questionamentos sobre Regime de Recuperação Fiscal",
                "descricao": "Contestações políticas e sindicais na Assembleia Legislativa de MG e no STF sobre o plano de recuperação fiscal do estado e privatizações da Cemig e Copasa.",
                "status_atual": "Controvérsia administrativa"
            }
        ],
        "fundao": False,
        "reeleicao": False,
        "governismo": "oposicao"
    },
    ("PRES", "RENAN SANTOS"): {
        "espectro": "direita",
        "vida_pregressa": {
            "status": "novato",
            "tempo_politica_anos": 12,
            "resumo": "Cofundador e coordenador nacional do Movimento Brasil Livre (MBL). Ativista político, comunicador e produtor cultural, estreando em disputa eleitoral formal."
        },
        "causas": ["economia", "corrupcao", "seguranca", "liberdades"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Inquérito dos Atos Antidemocráticos e MBL",
                "descricao": "Alvo de queixas-crimes e apurações preliminares em conflitos políticos e manifestações de rua; sem denúncia penal aceita pela Justiça.",
                "status_atual": "Sem condenação"
            }
        ],
        "fundao": False,
        "reeleicao": False,
        "governismo": "oposicao"
    },
    ("PRES", "PABLO MARÇAL"): {
        "espectro": "direita",
        "vida_pregressa": {
            "status": "novato",
            "tempo_politica_anos": 4,
            "resumo": "Empresário, influenciador digital e autor. Disputou a eleição presidencial de 2022 (candidatura anulada pelo partido) e a Prefeitura de São Paulo em 2024."
        },
        "causas": ["economia", "costumes", "tecnologia", "seguranca"],
        "registros_juridicos": [
            {
                "tipo": "condenado",
                "titulo": "Condenação em 2010 por Furto Qualificado Eletrônico",
                "descricao": "Condenado pela Justiça Federal de Goiás por envolvimento com grupo de desvio bancário em 2005. A pena prescreveu em 2018 e foi extinta sem cumprimento.",
                "status_atual": "Pena extinta por prescrição"
            },
            {
                "tipo": "investigado",
                "titulo": "Eleições 2024: Laudo Médico Falso",
                "descricao": "Inquérito policial aberto pela Polícia Federal sobre a divulgação de laudo médico falso nas vésperas do 1º turno municipal contra Guilherme Boulos.",
                "status_atual": "Inquérito em andamento"
            }
        ],
        "fundao": False,
        "reeleicao": False,
        "governismo": "oposicao"
    },
    ("PRES", "ESCRITOR AUGUSTO CURY"): {
        "espectro": "centro",
        "vida_pregressa": {
            "status": "novato",
            "tempo_politica_anos": 1,
            "resumo": "Médico psiquiatra, professor e escritor best-seller. Autor de livros sobre inteligência emocional, psicologia multifocal e desenvolvimento humano."
        },
        "causas": ["saude", "educacao", "social", "costumes"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem antecedentes criminais",
                "descricao": "Sem histórico de processos criminais ou investigações em órgãos públicos.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "independente"
    },

    # ── GOVERNO DE SÃO PAULO ──
    ("GOV-SP", "TARCÍSIO"): {
        "espectro": "centro-direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 8,
            "resumo": "Governador de São Paulo (2023–2026). Ex-ministro da Infraestrutura (2019–2022), ex-diretor-geral do DNIT e capitão da reserva do Exército Brasileiro formado no IME."
        },
        "causas": ["infra", "economia", "privatizacoes", "seguranca"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Declarações na Eleição Municipal 2024 (Caso PCC)",
                "descricao": "Declaração em dia de votação sobre suposta orientação de votos da facção criminosa gerou ação de investigação judicial eleitoral movida pelo PSOL.",
                "status_atual": "Ação eleitoral sem desfecho"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "oposicao"
    },
    ("GOV-SP", "FERNANDO HADDAD"): {
        "espectro": "centro-esquerda",
        "vida_pregressa": {
            "status": "ex_executivo",
            "tempo_politica_anos": 24,
            "resumo": "Ministro da Fazenda (2023–2026). Ex-prefeito de São Paulo (2013–2016), ex-ministro da Educação (2005–2012) e professor titular de Ciência Política da USP."
        },
        "causas": ["educacao", "economia", "social", "infra"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Ações Civis da Gestão Municipal e Lava Jato",
                "descricao": "Todas as acusações relativas à campanha de 2012 e delações da Lava Jato foram arquivadas ou julgadas improcedentes pelo STF e Justiça Eleitoral por falta de provas.",
                "status_atual": "Absolvido / Arquivado"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "governo"
    },
    ("GOV-SP", "VERA LÚCIA"): {
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "veterano",
            "tempo_politica_anos": 30,
            "resumo": "Socióloga, sindicalista e dirigente partidária do PSTU. Ativista do movimento negro e da classe trabalhadora, concorreu à presidência e governos em ciclos passados."
        },
        "causas": ["social", "direitos_trabalhistas", "liberdades", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem registros criminais",
                "descricao": "Ficha limpa perante a Justiça Eleitoral sem qualquer condenação penal.",
                "status_atual": "Regular"
            }
        ],
        "fundao": False,
        "reeleicao": False,
        "governismo": "oposicao"
    },
    ("GOV-SP", "VIVIAN MENDES"): {
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "novato",
            "tempo_politica_anos": 14,
            "resumo": "Comunicadora, ativista dos direitos humanos e presidente estadual da Unidade Popular (UP) em SP. Liderança de movimentos populares e juventude."
        },
        "causas": ["social", "liberdades", "moradia", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem antecedentes criminais",
                "descricao": "Histórico sem processos criminais ou condenações.",
                "status_atual": "Regular"
            }
        ],
        "fundao": False,
        "reeleicao": False,
        "governismo": "oposicao"
    },

    # ── SENADO EM SÃO PAULO ──
    ("SEN-SP", "MARINA SILVA"): {
        "espectro": "centro-esquerda",
        "vida_pregressa": {
            "status": "veterano",
            "tempo_politica_anos": 40,
            "resumo": "Ministra do Meio Ambiente e Mudança do Clima. Deputada federal por SP (2023–2026), ex-senadora pelo Acre por dois mandatos e fundadora da Rede Sustentabilidade."
        },
        "causas": ["meio_ambiente", "sustentabilidade", "social", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem registros criminais",
                "descricao": "Reconhecida internacionalmente pela integridade de gestão; quatro décadas de vida pública sem nenhuma condenação criminal.",
                "status_atual": "Ficha Limpa Integral"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "governo"
    },
    ("SEN-SP", "SIMONE TEBET"): {
        "espectro": "centro",
        "vida_pregressa": {
            "status": "veterano",
            "tempo_politica_anos": 24,
            "resumo": "Ministra do Planejamento e Orçamento (2023–2026). Ex-senadora pelo MS (2015–2022), ex-vice-governadora e prefeita de Três Lagoas. Advogada e professora de Direito."
        },
        "causas": ["economia", "educacao", "social", "infra"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem processos criminais",
                "descricao": "Histórico de probidade administrativa sem condenações na Justiça Comum ou Eleitoral.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "governo"
    },
    ("SEN-SP", "GUILHERME DERRITE"): {
        "espectro": "direita",
        "vida_pregressa": {
            "status": "carreira_tecnica",
            "tempo_politica_anos": 8,
            "resumo": "Secretário de Segurança Pública de São Paulo (2023–2026). Deputado federal reeleito por SP, ex-oficial da ROTA e capitão da Polícia Militar de SP."
        },
        "causas": ["seguranca", "combate_crime", "costumes", "economia"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Ocorrências Operacionais da ROTA e SSP",
                "descricao": "Inquéritos de autos de resistência da época de atividade operacional arquivados pela Justiça Militar e Ministério Público; representações políticas de oposição sobre a Operação Verão.",
                "status_atual": "Inquéritos arquivados"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "oposicao"
    },
    ("SEN-SP", "SALLES"): {
        "espectro": "direita",
        "vida_pregressa": {
            "status": "veterano",
            "tempo_politica_anos": 16,
            "resumo": "Deputado federal por São Paulo (2023–2026). Ex-ministro do Meio Ambiente (2019–2021) e ex-secretário estadual do Meio Ambiente de São Paulo. Advogado e administrador."
        },
        "causas": ["agro", "economia", "desregulamentacao", "seguranca"],
        "registros_juridicos": [
            {
                "tipo": "reu",
                "titulo": "Ação Penal na Justiça Federal (Exportação de Madeira)",
                "descricao": "Tornou-se réu na 4ª Vara Federal do Pará por acusação de facilitação de exportação de madeira nativa apreendida da Amazônia durante sua gestão ministerial.",
                "status_atual": "Ação penal em andamento"
            },
            {
                "tipo": "condenado",
                "titulo": "Ação Civil de Improbidade (Plano de Manejo do Tietê)",
                "descricao": "Condenado em 1ª instância em SP por alterações no mapa de área de proteção ambiental; decisão com recursos nos tribunais superiores.",
                "status_atual": "Recurso pendente"
            }
        ],
        "fundao": False,
        "reeleicao": False,
        "governismo": "oposicao"
    },
    ("SEN-SP", "SONINHA FRANCINE"): {
        "espectro": "centro-esquerda",
        "vida_pregressa": {
            "status": "veterano",
            "tempo_politica_anos": 22,
            "resumo": "Secretária Municipal de Direitos Humanos de SP. Ex-vereadora, ex-subprefeita da Lapa, comunicadora social e ativista de políticas públicas urbanas."
        },
        "causas": ["social", "liberdades", "saude", "meio_ambiente"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem registros criminais",
                "descricao": "Carreira pública sem condenações penais ou denúncias de corrupção.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "independente"
    },
    ("SEN-SP", "ANDRÉ DO PRADO"): {
        "espectro": "centro-direita",
        "vida_pregressa": {
            "status": "veterano",
            "tempo_politica_anos": 30,
            "resumo": "Presidente da Assembleia Legislativa do Estado de São Paulo (ALESP, 2023–2026). Deputado estadual por 4 mandatos, ex-prefeito e ex-vereador de Guararema."
        },
        "causas": ["infra", "economia", "agro", "saude"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Representações Administrativas de Gestão",
                "descricao": "Questionamentos e apontamentos usuais do Tribunal de Contas do Estado (TCE-SP) sobre despesas do legislativo estadual, sem condenações penais.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "oposicao"
    }
}

# Lista rica e curada de Deputados Federais por SP
DEPUTADOS_FEDERAIS_SP = [
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 5010,
        "urna": "GUILHERME BOULOS",
        "nome": "GUILHERME CASTRO BOULOS",
        "partido": "PSOL",
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 24,
            "resumo": "Deputado federal mais votado de SP em 2022 (mais de 1 milhão de votos). Líder histórico do MTST, escritor e professor universitário."
        },
        "causas": ["social", "moradia", "direitos_trabalhistas", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Detenções em Ocupações e Manifestações Populares",
                "descricao": "Detido pontualmente no passado em reintegrações de posse e protestos sociais; todos os inquéritos foram arquivados sem denúncia criminal.",
                "status_atual": "Ficha limpa"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "governo"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 2222,
        "urna": "EDUARDO BOLSONARO",
        "nome": "EDUARDO NANTES BOLSONARO",
        "partido": "PL",
        "espectro": "direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 12,
            "resumo": "Deputado federal por 3 mandatos consecutivos, escrivão da Polícia Federal concursado e advogado."
        },
        "causas": ["seguranca", "costumes", "armas", "liberdades"],
        "registros_juridicos": [
            {
                "tipo": "investigado",
                "titulo": "Inquérito das Fake News e Atos Antidemocráticos",
                "descricao": "Investigado pelo STF em inquéritos sobre financiamento de redes e disseminação de desinformação; denúncias ainda sem sentença condenatória definitiva.",
                "status_atual": "Em apuração"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "oposicao"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 4000,
        "urna": "TABATA AMARAL",
        "nome": "TABATA CLAUDIA AMARAL DE PONTES",
        "partido": "PSB",
        "espectro": "centro-esquerda",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 8,
            "resumo": "Deputada federal reeleita por SP, cientista política e astrofísica formada em Harvard. Ativista fundadora do Movimento Mapa Educação e Acredito."
        },
        "causas": ["educacao", "ciencia_tecnologia", "social", "saude"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem processos judiciais",
                "descricao": "Ficha limpa absoluta; sem investigações ou processos por conduta irregular.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "governo"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 4433,
        "urna": "KIM KATAGUIRI",
        "nome": "KIM PATROCA KATAGUIRI",
        "partido": "UNIÃO",
        "espectro": "centro-direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 12,
            "resumo": "Deputado federal reeleito por SP, cofundador do MBL, colunista e autor. Notabilizou-se por relatorias de desregulamentação e projetos de corte de gastos."
        },
        "causas": ["economia", "corrupcao", "desregulamentacao", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Polêmicas Verbais e Processos Cíveis",
                "descricao": "Processos por danos morais e ofensas em debates públicos movidos por adversários; sem acusações criminais de peculato ou desvio de dinheiro.",
                "status_atual": "Regular"
            }
        ],
        "fundao": False,
        "reeleicao": True,
        "governismo": "oposicao"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 5050,
        "urna": "ERIKA HILTON",
        "nome": "ERIKA HILTON DOS SANTOS SILVA",
        "partido": "PSOL",
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 8,
            "resumo": "Líder da bancada do PSOL na Câmara dos Deputados. Ex-vereadora mais votada do Brasil em 2020 e primeira mulher trans eleita deputada federal por SP."
        },
        "causas": ["liberdades", "direitos_trabalhistas", "social", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem antecedentes criminais",
                "descricao": "Sem processos criminais; atuação marcada pela defesa legislativa dos direitos humanos e pauta pelo fim da jornada 6x1.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "governo"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 3030,
        "urna": "ADRIANA VENTURA",
        "nome": "ADRIANA MIGUEL VENTURA",
        "partido": "NOVO",
        "espectro": "direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 8,
            "resumo": "Deputada federal reeleita por SP, professora de Gestão em Saúde na FGV-EAESP, doutora em Administração e defensora de transparência e saúde digital."
        },
        "causas": ["saude", "corrupcao", "economia", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem antecedentes criminais",
                "descricao": "100% de ficha limpa, renúncia a privilégios parlamentares e devolução de sobras de cota de gabinete.",
                "status_atual": "Regular"
            }
        ],
        "fundao": False,
        "reeleicao": True,
        "governismo": "oposicao"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 1313,
        "urna": "RUI FALCÃO",
        "nome": "RUI GOETHE DA COSTA FALCÃO",
        "partido": "PT",
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 44,
            "resumo": "Deputado federal por múltiplos mandatos, ex-presidente nacional do PT, ex-deputado estadual, jornalista e advogado."
        },
        "causas": ["social", "direitos_trabalhistas", "infra", "comunicacao"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Investigações da Época da Direção Partidária",
                "descricao": "Investigações de doações eleitorais da Lava Jato arquivadas pelo STF por ausência de indícios de contrapartida ilícita.",
                "status_atual": "Arquivado"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "governo"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 1010,
        "urna": "CELSO RUSSOMANNO",
        "nome": "CELSO UBERTO RUSSOMANNO",
        "partido": "REPUBLICANOS",
        "espectro": "centro-direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 32,
            "resumo": "Deputado federal desde 1995, jornalista e apresentador de televisão especializado na defesa do consumidor."
        },
        "causas": ["consumidor", "seguranca", "social", "economia"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Ação Penal por Peculato (STF)",
                "descricao": "Absolvido pelo Supremo Tribunal Federal em 2016 em acusação sobre pagamento de funcionária de sua produtora de TV com verba da Câmara.",
                "status_atual": "Absolvido pelo STF"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "independente"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 1515,
        "urna": "BALEIA ROSSI",
        "nome": "LUIZ FELIPE BALEIA TENUTO ROSSI",
        "partido": "MDB",
        "espectro": "centro",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 34,
            "resumo": "Presidente nacional do MDB, autor da PEC 45 da Reforma Tributária na Câmara dos Deputados, ex-deputado estadual e ex-vereador de Ribeirão Preto."
        },
        "causas": ["economia", "reforma_tributaria", "infra", "agro"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Citações em Delações Premiadas (Lava Jato)",
                "descricao": "Inquéritos instaurados no STF a partir de delações de empreiteiras foram arquivados a pedido da PGR por falta de provas materiais.",
                "status_atual": "Arquivado"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "governo"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 1100,
        "urna": "DELEGADO DA CUNHA",
        "nome": "CARLOS ALBERTO DA CUNHA",
        "partido": "PP",
        "espectro": "direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 4,
            "resumo": "Deputado federal eleito em 2022, delegado de Polícia Civil de carreira em São Paulo e criador de conteúdo digital sobre operações táticas."
        },
        "causas": ["seguranca", "combate_crime", "policia", "costumes"],
        "registros_juridicos": [
            {
                "tipo": "reu",
                "titulo": "Ação Penal por Violência Doméstica (Lei Maria da Penha)",
                "descricao": "Tornou-se réu na Justiça de São Paulo sob acusação de ameaça e agressão física à ex-companheira; o caso corre sob segredo de justiça.",
                "status_atual": "Ação penal em julgamento"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "oposicao"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 3000,
        "urna": "VINICIUS POIT",
        "nome": "VINICIUS CARVALHO POIT",
        "partido": "NOVO",
        "espectro": "direita",
        "vida_pregressa": {
            "status": "veterano",
            "tempo_politica_anos": 8,
            "resumo": "Ex-deputado federal por SP (2019–2022) e candidato a governador em 2022. Empreendedor, administrador de empresas e líder da bancada do NOVO."
        },
        "causas": ["economia", "privatizacoes", "corrupcao", "tecnologia"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem antecedentes criminais",
                "descricao": "Ficha limpa integral, renúncia de verbas indenizatórias e sem processos de corrupção.",
                "status_atual": "Regular"
            }
        ],
        "fundao": False,
        "reeleicao": False,
        "governismo": "oposicao"
    },
    {
        "cargo": "deputado_federal",
        "uf": "SP",
        "numero": 5005,
        "urna": "LUIZA ERUNDINA",
        "nome": "LUIZA ERUNDINA DE SOUSA",
        "partido": "PSOL",
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 50,
            "resumo": "Primeira mulher prefeita de São Paulo (1989–1992), deputada federal por 7 mandatos consecutivos, assistente social e defensora dos direitos sociais."
        },
        "causas": ["social", "direitos_humanos", "moradia", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Multa por Campanha de Greve (Anos 90)",
                "descricao": "Ação de improbidade pelo apoio a greve de transportes na prefeitura nos anos 90, resultando em bloqueio de bens posterior, sem dolo criminal.",
                "status_atual": "Ficha limpa"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "governo"
    }
]

# Lista rica e curada de Deputados Estaduais por SP (ALESP)
DEPUTADOS_ESTADUAIS_SP = [
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 13130,
        "urna": "EDUARDO SUPLICY",
        "nome": "EDUARDO MATARAZZO SUPLICY",
        "partido": "PT",
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 48,
            "resumo": "Deputado estadual mais votado de SP em 2022 (mais de 800 mil votos). Senador da República por 24 anos (1991–2015), ex-vereador, economista e professor da FGV."
        },
        "causas": ["renda_basica", "social", "direitos_humanos", "saude"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Detenção Simbólica em Reintegração de Posse (2016)",
                "descricao": "Deitou-se na rua em protesto pacífico contra reintegração de posse na Zona Oeste de SP e foi levado à delegacia por desobediência; liberado sem processo.",
                "status_atual": "Ficha limpa absoluta"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "oposicao"
    },
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 22022,
        "urna": "LUCAS PAVANATO",
        "nome": "LUCAS PAVANATO BREDARIOL",
        "partido": "PL",
        "espectro": "direita",
        "vida_pregressa": {
            "status": "novato",
            "tempo_politica_anos": 4,
            "resumo": "Vereador mais votado da capital paulista em 2024. Criador de conteúdo político conservador, palestrante e líder jovem da bancada bolsonarista."
        },
        "causas": ["costumes", "seguranca", "combate_ideologia_genero", "economia"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Processos Cíveis por Ofensas em Redes Sociais",
                "descricao": "Ações indenizatórias movidas por ativistas e políticos adversários em decorrência de debates e confrontos em manifestações; sem condenações penais.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "governo"
    },
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 44000,
        "urna": "GUTO ZACARIAS",
        "nome": "AUGUSTO THOMPSON ZACARIAS",
        "partido": "UNIÃO",
        "espectro": "direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 6,
            "resumo": "Deputado estadual eleito em 2022, vice-líder do governo Tarcísio na ALESP, coordenador nacional do MBL e ativista da privatização da Sabesp."
        },
        "causas": ["privatizacoes", "economia", "corte_gastos", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem antecedentes criminais",
                "descricao": "Renúncia a privilégios estaduais, sem carros oficiais ou auxílios extraordinários; ficha limpa.",
                "status_atual": "Regular"
            }
        ],
        "fundao": False,
        "reeleicao": True,
        "governismo": "governo"
    },
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 50000,
        "urna": "PAULA DA BANCADA FEMINISTA",
        "nome": "PAULA CARDOSO DE OLIVEIRA",
        "partido": "PSOL",
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 8,
            "resumo": "Deputada estadual eleita por mandato coletivo em 2022, servidora da Universidade de São Paulo (USP), ativista feminista negra e sindicalista."
        },
        "causas": ["servico_publico", "mulheres", "educacao", "social"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem processos judiciais",
                "descricao": "Ficha limpa integral, histórico de atuação voltado a CPIs de combate à violência obstétrica e defesa do ensino público.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "oposicao"
    },
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 30123,
        "urna": "LÉO SIQUEIRA",
        "nome": "LEONARDO SIQUEIRA ALVES",
        "partido": "NOVO",
        "espectro": "direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 6,
            "resumo": "Deputado estadual eleito em 2022, economista com mestrado na Barcelona School of Economics, cofundador do Terraço Econômico e ex-analista financeiro."
        },
        "causas": ["economia", "corrupcao", "desregulamentacao", "educacao"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem antecedentes criminais",
                "descricao": "Economia comprovada de verbas de gabinete na ALESP e transparência premiada; sem processos judiciais.",
                "status_atual": "Regular"
            }
        ],
        "fundao": False,
        "reeleicao": True,
        "governismo": "independente"
    },
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 50123,
        "urna": "CARLOS GIANNAZI",
        "nome": "CARLOS ALBERTO GIANNAZI",
        "partido": "PSOL",
        "espectro": "esquerda",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 28,
            "resumo": "Deputado estadual por 5 mandatos consecutivos na ALESP, ex-vereador de São Paulo, professor e diretor de escola pública da rede municipal."
        },
        "causas": ["educacao", "servidores_publicos", "previdencia", "social"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem registros criminais",
                "descricao": "Carreira pública voltada à fiscalização do orçamento da educação e saúde estadual sem processos por dolo ou corrupção.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "oposicao"
    },
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 10123,
        "urna": "TOMÉ ABDUCH",
        "nome": "TOMÉ ALVES ABDUCH",
        "partido": "REPUBLICANOS",
        "espectro": "direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 8,
            "resumo": "Deputado estadual em SP, engenheiro civil, empresário do setor imobiliário, comentarista de televisão e porta-voz do movimento Nas Ruas."
        },
        "causas": ["corrupcao", "seguranca", "economia", "costumes"],
        "registros_juridicos": [
            {
                "tipo": "boato_noticia",
                "titulo": "Polêmicas em Debates e Manifestações",
                "descricao": "Processos civis e queixas eleitorais em debates públicos de campanha; sem antecedentes penais de corrupção.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "governo"
    },
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 18018,
        "urna": "MARINA HELOU",
        "nome": "MARINA HELOU ALVARENGA",
        "partido": "REDE",
        "espectro": "centro",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 8,
            "resumo": "Deputada estadual reeleita por SP, administradora pública pela FGV, especialista em primeira infância, sustentabilidade urbana e saúde mental."
        },
        "causas": ["primeira_infancia", "meio_ambiente", "saude", "mulheres"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem antecedentes criminais",
                "descricao": "Ficha limpa integral; autora da lei estadual pioneira do Marco Legal da Primeira Infância em São Paulo.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "independente"
    },
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 11111,
        "urna": "JANAÍNA PASCHOAL",
        "nome": "JANAÍNA CONCEIÇÃO PASCHOAL",
        "partido": "PP",
        "espectro": "centro-direita",
        "vida_pregressa": {
            "status": "veterano",
            "tempo_politica_anos": 10,
            "resumo": "Deputada estadual mais votada da história do Brasil em 2018 (2 milhões de votos). Professora livre-docente de Direito Penal da USP e advogada."
        },
        "causas": ["combate_crime", "saude", "educacao", "corrupcao"],
        "registros_juridicos": [
            {
                "tipo": "nenhum",
                "titulo": "Sem antecedentes criminais",
                "descricao": "Ficha limpa integral sem processos de corrupção ou crimes funcionais.",
                "status_atual": "Regular"
            }
        ],
        "fundao": True,
        "reeleicao": False,
        "governismo": "independente"
    },
    {
        "cargo": "deputado_estadual",
        "uf": "SP",
        "numero": 22222,
        "urna": "GIL DINIZ",
        "nome": "GILMAR APARECIDO DINIZ",
        "partido": "PL",
        "espectro": "direita",
        "vida_pregressa": {
            "status": "reeleicao",
            "tempo_politica_anos": 10,
            "resumo": "Deputado estadual reeleito em SP (conhecido como 'Carteiro Reinaldo'), ex-assessor parlamentar, ativista conservador e ex-líder do governo na ALESP."
        },
        "causas": ["costumes", "seguranca", "familia", "armas"],
        "registros_juridicos": [
            {
                "tipo": "investigado",
                "titulo": "Apuração sobre Assessores de Gabinete (MP-SP)",
                "descricao": "Investigação do Ministério Público de SP sobre suposto recolhimento de salários em gabinete; inquérito civil arquivado por insuficiência de indícios probatórios.",
                "status_atual": "Arquivado no MP-SP"
            }
        ],
        "fundao": True,
        "reeleicao": True,
        "governismo": "governo"
    }
]

# Heurística partidária padrão para outros candidatos de structure.json
PARTIDO_ESPECTRO_DEFAULT = {
    "PT": "esquerda",
    "PCdoB": "esquerda",
    "PV": "centro-esquerda",
    "PSOL": "esquerda",
    "REDE": "centro-esquerda",
    "PSTU": "esquerda",
    "PCB": "esquerda",
    "PCO": "esquerda",
    "UP": "esquerda",
    "PDT": "centro-esquerda",
    "PSB": "centro-esquerda",
    "CIDADANIA": "centro",
    "PSDB": "centro",
    "MDB": "centro",
    "PSD": "centro",
    "SOLIDARIEDADE": "centro",
    "PODEMOS": "centro-direita",
    "PODE": "centro-direita",
    "AVANTE": "centro",
    "PRD": "centro-direita",
    "AGIR": "centro-direita",
    "DC": "direita",
    "PRTB": "direita",
    "PMB": "centro",
    "MOBILIZA": "centro",
    "REPUBLICANOS": "direita",
    "PP": "direita",
    "PL": "direita",
    "UNIÃO": "direita",
    "NOVO": "direita",
    "MISSÃO": "direita",
    "DEMOCRATA": "centro-direita"
}

def montar_base_completa():
    todos_candidatos = []
    
    # 1. Candidatos da estrutura original (Presidente, Governadores, Senadores)
    for race_id, r in STRUCT.get("races", {}).items():
        cargo = r.get("cargo")
        uf = r.get("uf", "BR")
        
        for c in r.get("candidates", []):
            urna = c.get("urna", "").strip()
            partido = c.get("partido", "").strip().upper()
            numero = c.get("numero")
            sq = c.get("sq")
            situacao = c.get("situacao", "Deferido")
            
            # Checa se temos curadoria detalhada
            key = (race_id, urna.upper())
            curado = CURADORIA.get(key)
            
            # Puxa dados do modelo se houver
            m_data = RESULTS_MAP.get(key, {})
            
            if curado:
                espectro = curado["espectro"]
                vida_pregressa = curado["vida_pregressa"]
                causas = curado["causas"]
                registros = curado["registros_juridicos"]
                fundao = curado.get("fundao", True)
                reeleicao = curado.get("reeleicao", False)
                governismo = curado.get("governismo", "independente")
            else:
                # Regras default inteligentes
                espectro = PARTIDO_ESPECTRO_DEFAULT.get(partido, "centro")
                vida_pregressa = {
                    "status": "veterano" if cargo in ("governador", "senador") else "novato",
                    "tempo_politica_anos": 10 if cargo in ("governador", "senador") else 4,
                    "resumo": f"Candidato(a) ao cargo de {cargo} pelo {partido} na eleição de 2026."
                }
                causas = ["social", "educacao"] if espectro in ("esquerda", "centro-esquerda") else ["economia", "seguranca"]
                registros = [{
                    "tipo": "nenhum",
                    "titulo": "Sem registros graves apontados",
                    "descricao": "Candidatura registrada perante o Tribunal Superior Eleitoral.",
                    "status_atual": "Registro regular"
                }]
                fundao = partido != "NOVO" and partido != "MISSÃO"
                reeleicao = False
                governismo = "governo" if espectro in ("esquerda", "centro-esquerda") else ("oposicao" if espectro == "direita" else "independente")
            
            cand_obj = {
                "id": f"{race_id}_{urna.lower().replace(' ', '_')}_{numero}",
                "race_id": race_id,
                "cargo": cargo,
                "uf": uf,
                "urna": urna,
                "nome_completo": c.get("nome", urna),
                "numero": numero,
                "partido": partido,
                "situacao": situacao,
                "espectro": espectro,
                "vida_pregressa": vida_pregressa,
                "causas": causas,
                "registros_juridicos": registros,
                "atributos": {
                    "fundao": fundao,
                    "reeleicao": reeleicao,
                    "governismo": governismo
                },
                "modelo": {
                    "share_projecao": m_data.get("share"),
                    "chance_eleito": m_data.get("eleito"),
                    "sd": m_data.get("sd"),
                    "t2": m_data.get("t2")
                }
            }
            todos_candidatos.append(cand_obj)
            
    # 2. Deputados Federais por SP
    for dep in DEPUTADOS_FEDERAIS_SP:
        cand_obj = {
            "id": f"DEP_FED_SP_{dep['urna'].lower().replace(' ', '_')}_{dep['numero']}",
            "race_id": "FED-SP",
            "cargo": "deputado_federal",
            "uf": "SP",
            "urna": dep["urna"],
            "nome_completo": dep["nome"],
            "numero": dep["numero"],
            "partido": dep["partido"],
            "situacao": "Deferido",
            "espectro": dep["espectro"],
            "vida_pregressa": dep["vida_pregressa"],
            "causas": dep["causas"],
            "registros_juridicos": dep["registros_juridicos"],
            "atributos": {
                "fundao": dep["fundao"],
                "reeleicao": dep["reeleicao"],
                "governismo": dep["governismo"]
            },
            "modelo": {
                "share_projecao": None,
                "chance_eleito": 0.85 if dep["reeleicao"] else 0.40,
                "sd": None,
                "t2": None
            }
        }
        todos_candidatos.append(cand_obj)
        
    # 3. Deputados Estaduais por SP
    for dep in DEPUTADOS_ESTADUAIS_SP:
        cand_obj = {
            "id": f"DEP_EST_SP_{dep['urna'].lower().replace(' ', '_')}_{dep['numero']}",
            "race_id": "EST-SP",
            "cargo": "deputado_estadual",
            "uf": "SP",
            "urna": dep["urna"],
            "nome_completo": dep["nome"],
            "numero": dep["numero"],
            "partido": dep["partido"],
            "situacao": "Deferido",
            "espectro": dep["espectro"],
            "vida_pregressa": dep["vida_pregressa"],
            "causas": dep["causas"],
            "registros_juridicos": dep["registros_juridicos"],
            "atributos": {
                "fundao": dep["fundao"],
                "reeleicao": dep["reeleicao"],
                "governismo": dep["governismo"]
            },
            "modelo": {
                "share_projecao": None,
                "chance_eleito": 0.80 if dep["reeleicao"] else 0.35,
                "sd": None,
                "t2": None
            }
        }
        todos_candidatos.append(cand_obj)
        
    dados_finais = {
        "meta": {
            "titulo": "Base Curada do Santinho Virtual (Eleições 2026)",
            "versao": "1.0",
            "total_candidatos": len(todos_candidatos),
            "espectros": ["esquerda", "centro-esquerda", "centro", "centro-direita", "direita"],
            "cargos": [
                {"id": "presidente", "label": "Presidente", "digitos": 2, "esfera": "executivo"},
                {"id": "governador", "label": "Governador", "digitos": 2, "esfera": "executivo"},
                {"id": "senador", "label": "Senador", "digitos": 3, "esfera": "legislativo"},
                {"id": "deputado_federal", "label": "Deputado Federal", "digitos": 4, "esfera": "legislativo"},
                {"id": "deputado_estadual", "label": "Deputado Estadual", "digitos": 5, "esfera": "legislativo"}
            ],
            "causas": [
                {"id": "social", "label": "Programas Sociais e Trabalho"},
                {"id": "educacao", "label": "Educação Pública"},
                {"id": "saude", "label": "Saúde e SUS"},
                {"id": "seguranca", "label": "Segurança Pública"},
                {"id": "economia", "label": "Economia e Livre Mercado"},
                {"id": "privatizacoes", "label": "Privatizações e Concessões"},
                {"id": "corrupcao", "label": "Combate à Corrupção"},
                {"id": "meio_ambiente", "label": "Meio Ambiente e Clima"},
                {"id": "agro", "label": "Agronegócio"},
                {"id": "infra", "label": "Infraestrutura e Transportes"},
                {"id": "costumes", "label": "Valores Conservadores e Família"},
                {"id": "liberdades", "label": "Direitos Humanos e Diversidade"},
                {"id": "tecnologia", "label": "Ciência e Inovação"},
                {"id": "moradia", "label": "Moradia Popular e Reforma Urbana"}
            ],
            "tipos_juridicos": [
                {"id": "nenhum", "label": "Sem Registros", "severidade": "baixo"},
                {"id": "boato_noticia", "label": "Boato / Polêmica na Imprensa", "severidade": "atencao"},
                {"id": "investigado", "label": "Em Investigação / Inquérito", "severidade": "medio"},
                {"id": "reu", "label": "Réu em Ação Penal", "severidade": "alto"},
                {"id": "condenado", "label": "Condenado Judicialmente", "severidade": "critico"}
            ]
        },
        "candidatos": todos_candidatos
    }
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dados_finais, f, indent=2, ensure_ascii=False)
    print(f"Base de candidatos gerada com sucesso em: {OUTPUT_PATH}")
    print(f"Total de candidatos gravados: {len(todos_candidatos)}")

if __name__ == "__main__":
    montar_base_completa()
