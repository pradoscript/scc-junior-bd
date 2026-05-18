"""As 10 consultas predefinidas do projeto.

Cada entrada de CONSULTAS contem:
- titulo: descricao exibida no menu
- sql:    SQL parametrizado com %(nome)s
- params: lista de (nome_param, prompt, conversor) para coletar do usuario
"""


CONSULTAS = [
    {
        "titulo": "Listar todas as edicoes da Copa (ano, sedes, campea, vice, 3o)",
        "sql": """
            SELECT
              e.Ano,
              s_campea.NomePais AS Campea,
              s_vice.NomePais   AS Vice,
              s_3o.NomePais     AS Terceiro,
              STRING_AGG(c.NomeCidade, ', ' ORDER BY c.NomeCidade) AS Sedes
            FROM EdicaoCopa e
            LEFT JOIN Selecao s_campea ON s_campea.IdSelecao = e.IdCampea
            LEFT JOIN Selecao s_vice   ON s_vice.IdSelecao   = e.IdVice
            LEFT JOIN Selecao s_3o     ON s_3o.IdSelecao     = e.IdTerceiro
            LEFT JOIN EdicaoCidade ec  ON ec.AnoCopa = e.Ano
            LEFT JOIN CidadeSede c     ON c.IdCidade = ec.IdCidade
            GROUP BY e.Ano, s_campea.NomePais, s_vice.NomePais, s_3o.NomePais
            ORDER BY e.Ano;
        """,
        "params": [],
    },
    {
        "titulo": "Listar selecoes participantes de uma edicao",
        "sql": """
            SELECT s.NomePais AS Selecao, t.Nome AS Tecnico
            FROM Participacao p
            JOIN Selecao s ON s.IdSelecao = p.IdSelecao
            JOIN Tecnico t ON t.IdTecnico = p.IdTecnico
            WHERE p.AnoCopa = %(ano)s
            ORDER BY s.NomePais;
        """,
        "params": [("ano", "Ano da edicao (ex: 2018): ", int)],
    },
    {
        "titulo": "Listar grupos de uma edicao e selecoes de cada grupo",
        "sql": """
            SELECT g.Letra AS Grupo, s.NomePais AS Selecao
            FROM Grupo g
            JOIN Fase f          ON f.IdFase = g.IdFase
            JOIN GrupoSelecao gs ON gs.IdGrupo = g.IdGrupo
            JOIN Selecao s       ON s.IdSelecao = gs.IdSelecao
            WHERE f.AnoCopa = %(ano)s
            ORDER BY g.Letra, s.NomePais;
        """,
        "params": [("ano", "Ano da edicao: ", int)],
    },
    {
        "titulo": "Tabela de classificacao de um grupo (V/E/D, GP, GC, SG, pontos)",
        "sql": """
            WITH part_grupo AS (
              SELECT
                p.IdPartida, p.IdSelecao1, p.IdSelecao2,
                p.GolsTime1, p.GolsTime2
              FROM Partida p
              JOIN Fase f    ON f.IdFase = p.IdFase
              JOIN Grupo g   ON g.IdFase = f.IdFase
              JOIN GrupoSelecao gs1 ON gs1.IdGrupo = g.IdGrupo AND gs1.IdSelecao = p.IdSelecao1
              JOIN GrupoSelecao gs2 ON gs2.IdGrupo = g.IdGrupo AND gs2.IdSelecao = p.IdSelecao2
              WHERE f.AnoCopa = %(ano)s AND g.Letra = %(grupo)s
            ),
            linhas AS (
              SELECT IdSelecao1 AS IdSelecao, GolsTime1 AS gf, GolsTime2 AS gs FROM part_grupo
              UNION ALL
              SELECT IdSelecao2 AS IdSelecao, GolsTime2 AS gf, GolsTime1 AS gs FROM part_grupo
            )
            SELECT
              s.NomePais AS Selecao,
              COUNT(*)                                         AS Jogos,
              SUM(CASE WHEN gf > gs THEN 1 ELSE 0 END)         AS Vitorias,
              SUM(CASE WHEN gf = gs THEN 1 ELSE 0 END)         AS Empates,
              SUM(CASE WHEN gf < gs THEN 1 ELSE 0 END)         AS Derrotas,
              SUM(gf)                                          AS GolsPro,
              SUM(gs)                                          AS GolsContra,
              SUM(gf) - SUM(gs)                                AS SaldoGols,
              SUM(CASE WHEN gf > gs THEN 3
                       WHEN gf = gs THEN 1 ELSE 0 END)         AS Pontos
            FROM linhas l
            JOIN Selecao s ON s.IdSelecao = l.IdSelecao
            GROUP BY s.NomePais
            ORDER BY Pontos DESC, SaldoGols DESC, GolsPro DESC, s.NomePais;
        """,
        "params": [
            ("ano",   "Ano da edicao: ", int),
            ("grupo", "Letra do grupo (A-H): ", str),
        ],
    },
    {
        "titulo": "Listar todas as partidas de uma edicao",
        "sql": """
            SELECT
              p.IdPartida AS Id,
              p.DataHora,
              f.Nome AS Fase,
              s1.NomePais AS Mandante,
              p.GolsTime1 || ' x ' || p.GolsTime2 AS Placar,
              s2.NomePais AS Visitante,
              e.Nome AS Estadio
            FROM Partida p
            JOIN Fase f     ON f.IdFase = p.IdFase
            JOIN Selecao s1 ON s1.IdSelecao = p.IdSelecao1
            JOIN Selecao s2 ON s2.IdSelecao = p.IdSelecao2
            JOIN Estadio e  ON e.IdEstadio = p.IdEstadio
            WHERE f.AnoCopa = %(ano)s
            ORDER BY p.DataHora;
        """,
        "params": [("ano", "Ano da edicao: ", int)],
    },
    {
        "titulo": "Caminho do mata-mata de uma edicao (classificados por fase)",
        "sql": """
            SELECT
              f.Nome AS Fase,
              s1.NomePais AS Selecao1,
              s2.NomePais AS Selecao2,
              p.GolsTime1 || ' x ' || p.GolsTime2 AS Placar,
              sc.NomePais AS Classificado
            FROM Partida p
            JOIN Fase f     ON f.IdFase = p.IdFase
            JOIN Selecao s1 ON s1.IdSelecao = p.IdSelecao1
            JOIN Selecao s2 ON s2.IdSelecao = p.IdSelecao2
            LEFT JOIN Selecao sc ON sc.IdSelecao = p.IdClassificado
            WHERE f.AnoCopa = %(ano)s AND f.Tipo <> 'fase_de_grupos'
            ORDER BY
              CASE f.Tipo
                WHEN 'oitavas' THEN 1
                WHEN 'quartas' THEN 2
                WHEN 'semifinal' THEN 3
                WHEN 'terceiro_lugar' THEN 4
                WHEN 'final' THEN 5
              END,
              p.DataHora;
        """,
        "params": [("ano", "Ano da edicao: ", int)],
    },
    {
        "titulo": "Elenco convocado de uma selecao em uma edicao",
        "sql": """
            SELECT
              c.NumeroCamisa AS Camisa,
              j.Nome         AS Jogador,
              j.Posicao,
              j.DataNascimento
            FROM Convocacao c
            JOIN Jogador j ON j.IdJogador = c.IdJogador
            JOIN Selecao s ON s.IdSelecao = c.IdSelecao
            WHERE c.AnoCopa = %(ano)s AND s.NomePais = %(selecao)s
            ORDER BY c.NumeroCamisa;
        """,
        "params": [
            ("ano",     "Ano da edicao: ", int),
            ("selecao", "Nome da selecao (ex: Brasil): ", str),
        ],
    },
    {
        "titulo": "Eventos de uma partida (gols, cartoes, substituicoes)",
        "sql": """
            SELECT
              ev.Minuto,
              ev.Tipo,
              COALESCE(jg.Nome, jc.Nome, js1.Nome) AS Jogador,
              CASE
                WHEN g.IdEvento  IS NOT NULL THEN 'Selecao: ' || sg.NomePais
                WHEN c.IdEvento  IS NOT NULL THEN 'Cartao: '  || c.TipoCartao
                WHEN sb.IdEvento IS NOT NULL THEN 'Entra: '   || js2.Nome
                ELSE NULL
              END AS Detalhe
            FROM Evento ev
            LEFT JOIN Gol g       ON g.IdEvento = ev.IdEvento
            LEFT JOIN Jogador jg  ON jg.IdJogador = g.IdJogador
            LEFT JOIN Selecao sg  ON sg.IdSelecao = g.IdSelecao
            LEFT JOIN Cartao c    ON c.IdEvento = ev.IdEvento
            LEFT JOIN Jogador jc  ON jc.IdJogador = c.IdJogador
            LEFT JOIN Substituicao sb ON sb.IdEvento = ev.IdEvento
            LEFT JOIN Jogador js1 ON js1.IdJogador = sb.IdJogadorSai
            LEFT JOIN Jogador js2 ON js2.IdJogador = sb.IdJogadorEntra
            WHERE ev.IdPartida = %(partida)s
            ORDER BY ev.Minuto, ev.IdEvento;
        """,
        "params": [("partida", "ID da partida: ", int)],
    },
    {
        "titulo": "Artilheiros de uma edicao",
        "sql": """
            SELECT
              j.Nome AS Jogador,
              s.NomePais AS Selecao,
              COUNT(*) AS Gols
            FROM Gol g
            JOIN Evento ev    ON ev.IdEvento  = g.IdEvento
            JOIN Partida p    ON p.IdPartida  = ev.IdPartida
            JOIN Fase f       ON f.IdFase     = p.IdFase
            JOIN Jogador j    ON j.IdJogador  = g.IdJogador
            JOIN Selecao s    ON s.IdSelecao  = g.IdSelecao
            WHERE f.AnoCopa = %(ano)s AND g.TipoGol <> 'gol_contra'
            GROUP BY j.Nome, s.NomePais
            ORDER BY Gols DESC, j.Nome
            LIMIT 20;
        """,
        "params": [("ano", "Ano da edicao: ", int)],
    },
    {
        "titulo": "Historico de uma selecao (participacoes, posicoes, V/E/D)",
        "sql": """
            WITH part AS (
              SELECT e.Ano,
                     CASE
                       WHEN e.IdCampea   = s.IdSelecao THEN 'Campea'
                       WHEN e.IdVice     = s.IdSelecao THEN 'Vice'
                       WHEN e.IdTerceiro = s.IdSelecao THEN '3o lugar'
                       ELSE '-'
                     END AS Posicao
              FROM EdicaoCopa e
              JOIN Participacao p ON p.AnoCopa = e.Ano
              JOIN Selecao s      ON s.IdSelecao = p.IdSelecao
              WHERE s.NomePais = %(selecao)s
            ),
            partidas AS (
              SELECT f.AnoCopa AS Ano,
                     CASE WHEN p.IdSelecao1 = s.IdSelecao THEN p.GolsTime1 ELSE p.GolsTime2 END AS gf,
                     CASE WHEN p.IdSelecao1 = s.IdSelecao THEN p.GolsTime2 ELSE p.GolsTime1 END AS gs
              FROM Partida p
              JOIN Fase f    ON f.IdFase = p.IdFase
              JOIN Selecao s ON s.NomePais = %(selecao)s
              WHERE p.IdSelecao1 = s.IdSelecao OR p.IdSelecao2 = s.IdSelecao
            )
            SELECT
              part.Ano,
              part.Posicao,
              COUNT(pa.Ano)                                  AS Jogos,
              SUM(CASE WHEN pa.gf > pa.gs THEN 1 ELSE 0 END) AS Vitorias,
              SUM(CASE WHEN pa.gf = pa.gs THEN 1 ELSE 0 END) AS Empates,
              SUM(CASE WHEN pa.gf < pa.gs THEN 1 ELSE 0 END) AS Derrotas
            FROM part
            LEFT JOIN partidas pa ON pa.Ano = part.Ano
            GROUP BY part.Ano, part.Posicao
            ORDER BY part.Ano;
        """,
        "params": [("selecao", "Nome da selecao: ", str)],
    },
]
