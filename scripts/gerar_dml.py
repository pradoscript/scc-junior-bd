#!/usr/bin/env python3
"""Gera sql/06.DML.sql com dados das Copas de 2018 (Russia) e 2022 (Catar)."""
import os
import random
from datetime import date, datetime, timedelta

random.seed(42)
OUT = []


def emit(s=""):
    OUT.append(s)


def sql_str(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, datetime):
        return "'" + v.isoformat(sep=" ") + "'"
    if isinstance(v, date):
        return "'" + v.isoformat() + "'"
    return "'" + str(v).replace("'", "''") + "'"


def insert(table, cols, rows):
    if not rows:
        return
    emit(f"INSERT INTO {table} ({', '.join(cols)}) VALUES")
    parts = []
    for r in rows:
        parts.append("  (" + ", ".join(sql_str(v) for v in r) + ")")
    emit(",\n".join(parts) + ";")
    emit()


# =====================================================================
# 1. Confederacao
# =====================================================================
CONFEDERACOES = [("UEFA",), ("CONMEBOL",), ("CONCACAF",),
                 ("CAF",), ("AFC",), ("OFC",)]
CONF_ID = {nome: i + 1 for i, (nome,) in enumerate(CONFEDERACOES)}

# =====================================================================
# 2. Pais
# =====================================================================
PAISES = [
    ("Russia", "Europa", "UEFA"), ("Franca", "Europa", "UEFA"),
    ("Belgica", "Europa", "UEFA"), ("Croacia", "Europa", "UEFA"),
    ("Inglaterra", "Europa", "UEFA"), ("Espanha", "Europa", "UEFA"),
    ("Portugal", "Europa", "UEFA"), ("Alemanha", "Europa", "UEFA"),
    ("Polonia", "Europa", "UEFA"), ("Suica", "Europa", "UEFA"),
    ("Suecia", "Europa", "UEFA"), ("Dinamarca", "Europa", "UEFA"),
    ("Servia", "Europa", "UEFA"), ("Islandia", "Europa", "UEFA"),
    ("Holanda", "Europa", "UEFA"), ("Pais de Gales", "Europa", "UEFA"),
    ("Brasil", "America do Sul", "CONMEBOL"), ("Argentina", "America do Sul", "CONMEBOL"),
    ("Uruguai", "America do Sul", "CONMEBOL"), ("Colombia", "America do Sul", "CONMEBOL"),
    ("Peru", "America do Sul", "CONMEBOL"), ("Equador", "America do Sul", "CONMEBOL"),
    ("Mexico", "America do Norte", "CONCACAF"), ("Estados Unidos", "America do Norte", "CONCACAF"),
    ("Costa Rica", "America Central", "CONCACAF"), ("Panama", "America Central", "CONCACAF"),
    ("Canada", "America do Norte", "CONCACAF"),
    ("Senegal", "Africa", "CAF"), ("Marrocos", "Africa", "CAF"),
    ("Tunisia", "Africa", "CAF"), ("Egito", "Africa", "CAF"),
    ("Nigeria", "Africa", "CAF"), ("Camaroes", "Africa", "CAF"),
    ("Gana", "Africa", "CAF"),
    ("Catar", "Asia", "AFC"), ("Japao", "Asia", "AFC"),
    ("Coreia do Sul", "Asia", "AFC"), ("Ira", "Asia", "AFC"),
    ("Arabia Saudita", "Asia", "AFC"), ("Australia", "Oceania", "AFC"),
]
SELECAO_PAISES = [p[0] for p in PAISES]
SEL_ID = {nome: i + 1 for i, nome in enumerate(SELECAO_PAISES)}

# =====================================================================
# 4. EdicaoCopa
# =====================================================================
EDICOES = [
    (2018, date(2018, 6, 14), date(2018, 7, 15), "Franca", "Croacia", "Belgica"),
    (2022, date(2022, 11, 20), date(2022, 12, 18), "Argentina", "Franca", "Croacia"),
]

# =====================================================================
# 5. CidadeSede
# =====================================================================
CIDADES = [
    ("Moscou", "Russia"), ("Sao Petersburgo", "Russia"), ("Kazan", "Russia"),
    ("Sochi", "Russia"), ("Nizhny Novgorod", "Russia"), ("Rostov", "Russia"),
    ("Samara", "Russia"), ("Saransk", "Russia"), ("Volgogrado", "Russia"),
    ("Ekaterimburgo", "Russia"), ("Kaliningrado", "Russia"),
    ("Doha", "Catar"), ("Lusail", "Catar"), ("Al Khor", "Catar"),
    ("Al Wakrah", "Catar"), ("Al Rayyan", "Catar"),
]
CIDADE_ID = {nome: i + 1 for i, (nome, _) in enumerate(CIDADES)}

EDICAO_CIDADES = {
    2018: ["Moscou", "Sao Petersburgo", "Kazan", "Sochi", "Nizhny Novgorod",
           "Rostov", "Samara", "Saransk", "Volgogrado", "Ekaterimburgo",
           "Kaliningrado"],
    2022: ["Doha", "Lusail", "Al Khor", "Al Wakrah", "Al Rayyan"],
}

# =====================================================================
# 7. Estadio
# =====================================================================
ESTADIOS = [
    ("Luzhniki", 81000, "Moscou Centro", "Moscou"),
    ("Spartak", 45000, "Moscou Norte", "Moscou"),
    ("Krestovsky", 68000, "Ilha Krestovsky", "Sao Petersburgo"),
    ("Kazan Arena", 45000, "Centro de Kazan", "Kazan"),
    ("Fisht", 47000, "Parque Olimpico", "Sochi"),
    ("Nizhny Novgorod Stadium", 45000, "Beira-rio", "Nizhny Novgorod"),
    ("Rostov Arena", 45000, "Margem do Don", "Rostov"),
    ("Samara Arena", 45000, "Cosmoport", "Samara"),
    ("Mordovia Arena", 44000, "Centro", "Saransk"),
    ("Volgograd Arena", 45000, "Margens do Volga", "Volgogrado"),
    ("Ekaterinburg Arena", 35000, "Centro", "Ekaterimburgo"),
    ("Kaliningrad Stadium", 35000, "Ilha Oktyabrsky", "Kaliningrado"),
    ("Lusail Iconic", 80000, "Lusail Marina", "Lusail"),
    ("Al Bayt", 60000, "Al Khor norte", "Al Khor"),
    ("Estadio 974", 40000, "Doha porto", "Doha"),
    ("Khalifa International", 45000, "Aspire Zone", "Doha"),
    ("Education City", 45000, "Al Rayyan", "Al Rayyan"),
    ("Ahmad bin Ali", 40000, "Al Rayyan", "Al Rayyan"),
    ("Al Janoub", 40000, "Al Wakrah", "Al Wakrah"),
    ("Al Thumama", 40000, "Doha sul", "Doha"),
]
ESTADIO_ID = {nome: i + 1 for i, (nome, *_rest) in enumerate(ESTADIOS)}
ESTADIOS_EDICAO = {
    2018: [ESTADIO_ID[n] for n, _, _, c in ESTADIOS if c in EDICAO_CIDADES[2018]],
    2022: [ESTADIO_ID[n] for n, _, _, c in ESTADIOS if c in EDICAO_CIDADES[2022]],
}

# =====================================================================
# 9. Grupos oficiais
# =====================================================================
GRUPOS_2018 = {
    "A": ["Russia", "Arabia Saudita", "Egito", "Uruguai"],
    "B": ["Portugal", "Espanha", "Marrocos", "Ira"],
    "C": ["Franca", "Australia", "Peru", "Dinamarca"],
    "D": ["Argentina", "Islandia", "Croacia", "Nigeria"],
    "E": ["Brasil", "Suica", "Costa Rica", "Servia"],
    "F": ["Alemanha", "Mexico", "Suecia", "Coreia do Sul"],
    "G": ["Belgica", "Panama", "Tunisia", "Inglaterra"],
    "H": ["Polonia", "Senegal", "Colombia", "Japao"],
}
GRUPOS_2022 = {
    "A": ["Catar", "Equador", "Senegal", "Holanda"],
    "B": ["Inglaterra", "Ira", "Estados Unidos", "Pais de Gales"],
    "C": ["Argentina", "Arabia Saudita", "Mexico", "Polonia"],
    "D": ["Franca", "Australia", "Dinamarca", "Tunisia"],
    "E": ["Espanha", "Costa Rica", "Alemanha", "Japao"],
    "F": ["Belgica", "Canada", "Marrocos", "Croacia"],
    "G": ["Brasil", "Servia", "Suica", "Camaroes"],
    "H": ["Portugal", "Gana", "Uruguai", "Coreia do Sul"],
}
GRUPOS_EDICAO = {2018: GRUPOS_2018, 2022: GRUPOS_2022}

# =====================================================================
# Tecnicos
# =====================================================================
TECNICOS_REAIS = {
    (2018, "Brasil"): "Tite",
    (2018, "Argentina"): "Jorge Sampaoli",
    (2018, "Franca"): "Didier Deschamps",
    (2018, "Croacia"): "Zlatko Dalic",
    (2018, "Belgica"): "Roberto Martinez",
    (2018, "Inglaterra"): "Gareth Southgate",
    (2018, "Alemanha"): "Joachim Low",
    (2018, "Espanha"): "Fernando Hierro",
    (2018, "Russia"): "Stanislav Cherchesov",
    (2018, "Portugal"): "Fernando Santos",
    (2022, "Argentina"): "Lionel Scaloni",
    (2022, "Franca"): "Didier Deschamps",
    (2022, "Croacia"): "Zlatko Dalic",
    (2022, "Marrocos"): "Walid Regragui",
    (2022, "Brasil"): "Tite",
    (2022, "Inglaterra"): "Gareth Southgate",
    (2022, "Portugal"): "Fernando Santos",
    (2022, "Catar"): "Felix Sanchez",
    (2022, "Holanda"): "Louis van Gaal",
    (2022, "Espanha"): "Luis Enrique",
}
NOMES_TEC = ["Carlos Mendes", "John Smith", "Hans Mueller", "Jean Dupont",
             "Marco Rossi", "Pedro Garcia", "Ali Hassan", "Yuki Tanaka",
             "Kim Park", "Diego Lopez", "Sergei Ivanov", "Anders Olsen",
             "Lars Nielsen", "Stefan Novak", "Igor Petric", "Mehdi Karimi",
             "Omar Diallo", "Kwame Boateng", "Pablo Ramirez", "Felipe Costa",
             "Bruno Almeida", "Lucas Silva", "Mateo Fernandez", "Alejandro Vidal",
             "Andrei Popov", "Bjorn Larsson", "Olaf Hansen", "Mikkel Sorensen",
             "Ivan Horvat", "Petar Kovac", "Tarek Bouazizi", "Sami El-Amin",
             "Karim Cherif", "Kojiro Sato", "Hiroshi Yamada", "Min Jae Lee",
             "Daichi Suzuki", "Hassan Mohamed", "Yusuf Bilal", "Salim Nasser",
             "Vladimir Sokolov", "Dmitri Volkov", "Anton Belov",
             "Roberto Pellegrini", "Antonio Conte"]

# =====================================================================
# Jogadores
# =====================================================================
POSICOES = ["goleiro", "zagueiro", "lateral", "volante", "meio_campo", "atacante"]
NOMES_PRIMEIRO = ["Alex", "Bruno", "Carlos", "Daniel", "Eduardo", "Felipe",
                  "Gabriel", "Hugo", "Ivan", "Joao", "Kevin", "Lucas", "Mateus",
                  "Nicolas", "Otavio", "Pedro", "Rafael", "Sergio", "Thiago",
                  "Vinicius", "Yuri", "Andre", "Marcos", "Diego", "Rodrigo",
                  "Fabio", "Ricardo", "Mario", "Antonio", "Manuel"]
NOMES_SOBRENOME = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira",
                   "Costa", "Rodrigues", "Almeida", "Nascimento", "Carvalho",
                   "Gomes", "Martins", "Araujo", "Ribeiro", "Alves", "Monteiro",
                   "Mendes", "Barros", "Freitas", "Rocha", "Dias", "Cardoso",
                   "Reis", "Lopes", "Teixeira", "Correia", "Pinto", "Moreira",
                   "Cavalcante", "Ferreira", "Vieira", "Pires"]


def nome_aleatorio():
    return random.choice(NOMES_PRIMEIRO) + " " + random.choice(NOMES_SOBRENOME)


def nascimento_aleatorio():
    return date(random.randint(1985, 2002), random.randint(1, 12), random.randint(1, 28))


# =====================================================================
# Cabecalho
# =====================================================================
emit("-- =====================================================================")
emit("-- SCC0640 - Projeto Copa do Mundo FIFA")
emit("-- Arquivo: 06.DML.sql  (gerado por scripts/gerar_dml.py)")
emit("-- Dados: edicoes 2018 (Russia) e 2022 (Catar)")
emit("-- =====================================================================")
emit()

# Confederacao
emit("-- Confederacao")
insert("Confederacao", ["Nome"], CONFEDERACOES)

# Pais
emit("-- Pais")
insert("Pais", ["Nome", "Continente", "IdConfederacao"],
       [(n, c, CONF_ID[conf]) for n, c, conf in PAISES])

# Selecao
emit("-- Selecao")
insert("Selecao", ["NomePais"], [(n,) for n in SELECAO_PAISES])

# EdicaoCopa
emit("-- EdicaoCopa (campea/vice/terceiro atualizados ao final)")
insert("EdicaoCopa", ["Ano", "DataInicio", "DataTermino"],
       [(e[0], e[1], e[2]) for e in EDICOES])

# CidadeSede
emit("-- CidadeSede")
insert("CidadeSede", ["NomeCidade", "Pais"], CIDADES)

# EdicaoCidade
emit("-- EdicaoCidade")
ec_rows = []
for ano, cidades in EDICAO_CIDADES.items():
    for c in cidades:
        ec_rows.append((ano, CIDADE_ID[c]))
insert("EdicaoCidade", ["AnoCopa", "IdCidade"], ec_rows)

# Estadio
emit("-- Estadio")
insert("Estadio", ["Nome", "Capacidade", "Localizacao", "IdCidade"],
       [(n, cap, loc, CIDADE_ID[cid]) for n, cap, loc, cid in ESTADIOS])

# Tecnico
emit("-- Tecnico")
tecnicos = []
TEC_ID = {}
random.shuffle(NOMES_TEC)
nome_iter = iter(NOMES_TEC * 4)
for ano in [2018, 2022]:
    for letra in "ABCDEFGH":
        for p in GRUPOS_EDICAO[ano][letra]:
            nome = TECNICOS_REAIS.get((ano, p), next(nome_iter))
            tecnicos.append((nome, p))
            TEC_ID[(ano, p)] = len(tecnicos)
insert("Tecnico", ["Nome", "Nacionalidade"], tecnicos)

# Jogador
emit("-- Jogador (23 por selecao-edicao)")
jogadores = []
JOG_POR_SEL = {}
for ano in [2018, 2022]:
    for letra in "ABCDEFGH":
        for p in GRUPOS_EDICAO[ano][letra]:
            ids = []
            for _ in range(23):
                jogadores.append((nome_aleatorio(), random.choice(POSICOES),
                                  nascimento_aleatorio(), p))
                ids.append(len(jogadores))
            JOG_POR_SEL[(ano, p)] = ids
insert("Jogador", ["Nome", "Posicao", "DataNascimento", "Nacionalidade"], jogadores)

# Arbitro
emit("-- Arbitro")
ARB_NAC = ["Italia", "Argentina", "Inglaterra", "Brasil", "Mexico", "Polonia",
           "Japao", "Senegal", "Franca", "Holanda", "Espanha", "Alemanha",
           "Uruguai", "Turquia", "Iemen", "Catar", "Egito", "Australia",
           "Suica", "Eslovenia", "Romenia", "Servia", "Marrocos", "Ira",
           "Estados Unidos", "Coreia do Sul", "Colombia", "Costa Rica",
           "Paraguai", "Iraque"]
arbitros = [(f"Arbitro {i:02d}", nac) for i, nac in enumerate(ARB_NAC, 1)]
insert("Arbitro", ["Nome", "Nacionalidade"], arbitros)

# Fase
emit("-- Fase")
FASES_TIPOS = [
    ("Fase de Grupos", "fase_de_grupos"),
    ("Oitavas de Final", "oitavas"),
    ("Quartas de Final", "quartas"),
    ("Semifinal", "semifinal"),
    ("Disputa do 3o Lugar", "terceiro_lugar"),
    ("Final", "final"),
]
fases = []
FASE_ID = {}
for ano in [2018, 2022]:
    for nome, tipo in FASES_TIPOS:
        fases.append((nome, tipo, ano))
        FASE_ID[(ano, tipo)] = len(fases)
insert("Fase", ["Nome", "Tipo", "AnoCopa"], fases)

# Grupo
emit("-- Grupo")
grupos = []
GRUPO_ID = {}
for ano in [2018, 2022]:
    for letra in "ABCDEFGH":
        grupos.append((letra, FASE_ID[(ano, "fase_de_grupos")]))
        GRUPO_ID[(ano, letra)] = len(grupos)
insert("Grupo", ["Letra", "IdFase"], grupos)

# GrupoSelecao
emit("-- GrupoSelecao")
gs_rows = []
for ano in [2018, 2022]:
    for letra, paises in GRUPOS_EDICAO[ano].items():
        for p in paises:
            gs_rows.append((GRUPO_ID[(ano, letra)], SEL_ID[p]))
insert("GrupoSelecao", ["IdGrupo", "IdSelecao"], gs_rows)

# Participacao
emit("-- Participacao")
part_rows = []
for ano in [2018, 2022]:
    for letra, paises in GRUPOS_EDICAO[ano].items():
        for p in paises:
            part_rows.append((ano, SEL_ID[p], TEC_ID[(ano, p)]))
insert("Participacao", ["AnoCopa", "IdSelecao", "IdTecnico"], part_rows)

# Convocacao
emit("-- Convocacao")
conv_rows = []
for ano in [2018, 2022]:
    for letra, paises in GRUPOS_EDICAO[ano].items():
        for p in paises:
            for num, jid in enumerate(JOG_POR_SEL[(ano, p)], 1):
                conv_rows.append((ano, SEL_ID[p], jid, num))
insert("Convocacao", ["AnoCopa", "IdSelecao", "IdJogador", "NumeroCamisa"], conv_rows)

# =====================================================================
# Partidas
# =====================================================================
partidas = []
PARTIDA_INFO = []


def add_partida(ano, p1, p2, tipo_fase, datahora, g1, g2,
                tem_prorr=False, penaltis=None, classificado=None):
    idsel1, idsel2 = SEL_ID[p1], SEL_ID[p2]
    idfase = FASE_ID[(ano, tipo_fase)]
    idestadio = random.choice(ESTADIOS_EDICAO[ano])
    idclass = SEL_ID[classificado] if classificado else None
    partidas.append({
        "DataHora": datahora, "TemProrrogacao": tem_prorr,
        "ResultadoPenaltis": penaltis, "IdClassificado": idclass,
        "IdFase": idfase, "IdEstadio": idestadio,
        "IdSelecao1": idsel1, "IdSelecao2": idsel2,
    })
    PARTIDA_INFO.append({
        "id": len(partidas), "ano": ano,
        "sel1": idsel1, "sel2": idsel2, "gols1": g1, "gols2": g2,
    })


def gerar_fase_grupos(ano, data_inicio):
    dia = 0
    for letra, paises in GRUPOS_EDICAO[ano].items():
        pares = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]
        for i, j in pares:
            p1, p2 = paises[i], paises[j]
            dh = datetime.combine(data_inicio + timedelta(days=dia // 4),
                                  datetime.min.time()) + timedelta(hours=12 + (dia % 4) * 3)
            add_partida(ano, p1, p2, "fase_de_grupos", dh,
                        random.randint(0, 3), random.randint(0, 3))
            dia += 1


def gerar_mata_mata(ano, base, confrontos):
    dia = 0
    for tipo, jogos in confrontos.items():
        for p1, p2, g1, g2, vencedor in jogos:
            dh = datetime.combine(base + timedelta(days=dia // 2),
                                  datetime.min.time()) + timedelta(hours=15 + (dia % 2) * 3)
            tem_prorr = (g1 == g2)
            penaltis = "decidido nos penaltis" if g1 == g2 else None
            add_partida(ano, p1, p2, tipo, dh, g1, g2, tem_prorr=tem_prorr,
                        penaltis=penaltis, classificado=vencedor)
            dia += 1


# 2018
gerar_fase_grupos(2018, date(2018, 6, 14))
gerar_mata_mata(2018, date(2018, 6, 30), {
    "oitavas": [
        ("Franca", "Argentina", 4, 3, "Franca"),
        ("Uruguai", "Portugal", 2, 1, "Uruguai"),
        ("Brasil", "Mexico", 2, 0, "Brasil"),
        ("Belgica", "Japao", 3, 2, "Belgica"),
        ("Espanha", "Russia", 1, 1, "Russia"),
        ("Croacia", "Dinamarca", 1, 1, "Croacia"),
        ("Suecia", "Suica", 1, 0, "Suecia"),
        ("Colombia", "Inglaterra", 1, 1, "Inglaterra"),
    ],
    "quartas": [
        ("Uruguai", "Franca", 0, 2, "Franca"),
        ("Brasil", "Belgica", 1, 2, "Belgica"),
        ("Russia", "Croacia", 2, 2, "Croacia"),
        ("Suecia", "Inglaterra", 0, 2, "Inglaterra"),
    ],
    "semifinal": [
        ("Franca", "Belgica", 1, 0, "Franca"),
        ("Croacia", "Inglaterra", 2, 1, "Croacia"),
    ],
    "terceiro_lugar": [("Belgica", "Inglaterra", 2, 0, "Belgica")],
    "final": [("Franca", "Croacia", 4, 2, "Franca")],
})

# 2022
gerar_fase_grupos(2022, date(2022, 11, 20))
gerar_mata_mata(2022, date(2022, 12, 3), {
    "oitavas": [
        ("Holanda", "Estados Unidos", 3, 1, "Holanda"),
        ("Argentina", "Australia", 2, 1, "Argentina"),
        ("Franca", "Polonia", 3, 1, "Franca"),
        ("Inglaterra", "Senegal", 3, 0, "Inglaterra"),
        ("Japao", "Croacia", 1, 1, "Croacia"),
        ("Brasil", "Coreia do Sul", 4, 1, "Brasil"),
        ("Marrocos", "Espanha", 0, 0, "Marrocos"),
        ("Portugal", "Suica", 6, 1, "Portugal"),
    ],
    "quartas": [
        ("Croacia", "Brasil", 1, 1, "Croacia"),
        ("Holanda", "Argentina", 2, 2, "Argentina"),
        ("Marrocos", "Portugal", 1, 0, "Marrocos"),
        ("Inglaterra", "Franca", 1, 2, "Franca"),
    ],
    "semifinal": [
        ("Argentina", "Croacia", 3, 0, "Argentina"),
        ("Franca", "Marrocos", 2, 0, "Franca"),
    ],
    "terceiro_lugar": [("Croacia", "Marrocos", 2, 1, "Croacia")],
    "final": [("Argentina", "Franca", 3, 3, "Argentina")],
})

# Emitir Partida (placar zerado — triggers preenchem via Gol)
emit("-- Partida (GolsTime1/GolsTime2 atualizados via trigger ao inserir Gol)")
partida_rows = [(p["DataHora"], 0, 0, p["TemProrrogacao"],
                 p["ResultadoPenaltis"], p["IdClassificado"], p["IdFase"],
                 p["IdEstadio"], p["IdSelecao1"], p["IdSelecao2"])
                for p in partidas]
insert("Partida",
       ["DataHora", "GolsTime1", "GolsTime2", "TemProrrogacao",
        "ResultadoPenaltis", "IdClassificado", "IdFase", "IdEstadio",
        "IdSelecao1", "IdSelecao2"], partida_rows)

# Arbitragem (3 por partida)
emit("-- Arbitragem")
arb_rows = []
n_arb = len(ARB_NAC)
for info in PARTIDA_INFO:
    escolhidos = random.sample(range(1, n_arb + 1), 3)
    arb_rows.append((info["id"], escolhidos[0], "principal"))
    arb_rows.append((info["id"], escolhidos[1], "assistente_1"))
    arb_rows.append((info["id"], escolhidos[2], "assistente_2"))
insert("Arbitragem", ["IdPartida", "IdArbitro", "Funcao"], arb_rows)

# =====================================================================
# Eventos / Gols / Cartoes / Substituicoes
# =====================================================================
eventos = []
gols_pendentes = []
cartoes_pendentes = []
subs_pendentes = []


def jogadores_de(ano, idsel):
    return JOG_POR_SEL[(ano, SELECAO_PAISES[idsel - 1])]


for info in PARTIDA_INFO:
    ano, idp = info["ano"], info["id"]
    sel1, sel2 = info["sel1"], info["sel2"]
    g1, g2 = info["gols1"], info["gols2"]
    j1, j2 = jogadores_de(ano, sel1), jogadores_de(ano, sel2)
    minutos = set()

    def proxmin(lo=1, hi=90):
        m = random.randint(lo, hi)
        while m in minutos:
            m = random.randint(lo, hi)
        minutos.add(m)
        return m

    # gols time 1
    for _ in range(g1):
        m = proxmin()
        r = random.random()
        if r < 0.10:
            jogador, tipo_evt, tipo_gol, sel_gol = random.choice(j2), "gol_contra", "gol_contra", sel2
        elif r < 0.25:
            jogador, tipo_evt, tipo_gol, sel_gol = random.choice(j1), "penalti_convertido", "penalti_convertido", sel1
        else:
            jogador, tipo_evt, tipo_gol, sel_gol = random.choice(j1), "gol", "normal", sel1
        eventos.append((m, tipo_evt, idp))
        gols_pendentes.append((len(eventos), tipo_gol, jogador, sel_gol))

    # gols time 2
    for _ in range(g2):
        m = proxmin()
        r = random.random()
        if r < 0.10:
            jogador, tipo_evt, tipo_gol, sel_gol = random.choice(j1), "gol_contra", "gol_contra", sel1
        elif r < 0.25:
            jogador, tipo_evt, tipo_gol, sel_gol = random.choice(j2), "penalti_convertido", "penalti_convertido", sel2
        else:
            jogador, tipo_evt, tipo_gol, sel_gol = random.choice(j2), "gol", "normal", sel2
        eventos.append((m, tipo_evt, idp))
        gols_pendentes.append((len(eventos), tipo_gol, jogador, sel_gol))

    # cartoes amarelos (0-3)
    amarelos_usados = set()
    for _ in range(random.randint(0, 3)):
        m = random.randint(10, 90)
        jogador = random.choice(random.choice([j1, j2]))
        # evitar 2 amarelos para o mesmo jogador
        if jogador in amarelos_usados:
            continue
        amarelos_usados.add(jogador)
        eventos.append((m, "cartao_amarelo", idp))
        cartoes_pendentes.append((len(eventos), "amarelo", jogador))

    # vermelho (10%)
    if random.random() < 0.10:
        m = random.randint(20, 90)
        jogador = random.choice(random.choice([j1, j2]))
        eventos.append((m, "cartao_vermelho", idp))
        cartoes_pendentes.append((len(eventos), "vermelho", jogador))

    # substituicoes: 2-3 por time
    for jteam in [j1, j2]:
        sai_usados, entra_usados = set(), set()
        for _ in range(random.randint(2, 3)):
            sai = random.choice(jteam)
            t = 0
            while sai in sai_usados and t < 10:
                sai = random.choice(jteam); t += 1
            entra = random.choice(jteam)
            t = 0
            while (entra == sai or entra in entra_usados or entra in sai_usados) and t < 10:
                entra = random.choice(jteam); t += 1
            if sai == entra or entra in sai_usados or sai in entra_usados:
                continue
            sai_usados.add(sai); entra_usados.add(entra)
            m = random.randint(45, 90)
            eventos.append((m, "substituicao", idp))
            subs_pendentes.append((len(eventos), sai, entra))

emit("-- Evento")
insert("Evento", ["Minuto", "Tipo", "IdPartida"], eventos)

emit("-- Gol (triggers atualizam GolsTime1/GolsTime2)")
insert("Gol", ["IdEvento", "TipoGol", "IdJogador", "IdSelecao"],
       [(idx, tg, j, s) for (idx, tg, j, s) in gols_pendentes])

emit("-- Cartao")
insert("Cartao", ["IdEvento", "TipoCartao", "IdJogador"],
       [(idx, tc, j) for (idx, tc, j) in cartoes_pendentes])

emit("-- Substituicao")
insert("Substituicao", ["IdEvento", "IdJogadorSai", "IdJogadorEntra"],
       [(idx, sai, entra) for (idx, sai, entra) in subs_pendentes])

# Atualizar EdicaoCopa
emit("-- Atualizar EdicaoCopa com campea/vice/terceiro")
for ano, _, _, campea, vice, terceiro in EDICOES:
    emit(f"UPDATE EdicaoCopa SET IdCampea = {SEL_ID[campea]}, "
         f"IdVice = {SEL_ID[vice]}, IdTerceiro = {SEL_ID[terceiro]} "
         f"WHERE Ano = {ano};")
emit()

# Salvar
out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        "sql", "06.DML.sql")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))

print(f"DML gerado em {out_path}")
print(f"Linhas: {len(OUT)} | Partidas: {len(partidas)} | "
      f"Eventos: {len(eventos)} | Gols: {len(gols_pendentes)} | "
      f"Cartoes: {len(cartoes_pendentes)} | Subs: {len(subs_pendentes)} | "
      f"Convocacoes: {len(conv_rows)}")
