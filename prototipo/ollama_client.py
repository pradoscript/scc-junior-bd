"""Integracao com o servico local Ollama para traduzir linguagem natural em SQL."""
import os
import re
import requests


def _url() -> str:
    return os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


def _modelo_padrao() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3.2")


SYSTEM_PROMPT = """Voce e um tradutor de portugues para SQL PostgreSQL.

O banco de dados tem as seguintes tabelas:
- Confederacao(IdConfederacao, Nome)
- Pais(Nome, Continente, IdConfederacao)
- Selecao(IdSelecao, NomePais)
- EdicaoCopa(Ano, DataInicio, DataTermino, IdCampea, IdVice, IdTerceiro)
- CidadeSede(IdCidade, NomeCidade, Pais)
- EdicaoCidade(AnoCopa, IdCidade)
- Estadio(IdEstadio, Nome, Capacidade, Localizacao, IdCidade)
- Fase(IdFase, Nome, Tipo, AnoCopa)  -- Tipo: fase_de_grupos, oitavas, quartas, semifinal, terceiro_lugar, final
- Grupo(IdGrupo, Letra, IdFase)
- GrupoSelecao(IdGrupo, IdSelecao)
- Participacao(AnoCopa, IdSelecao, IdTecnico)
- Convocacao(AnoCopa, IdSelecao, IdJogador, NumeroCamisa)
- Partida(IdPartida, DataHora, GolsTime1, GolsTime2, TemProrrogacao, ResultadoPenaltis,
          IdClassificado, IdFase, IdEstadio, IdSelecao1, IdSelecao2)
- Arbitragem(IdPartida, IdArbitro, Funcao)
- Jogador(IdJogador, Nome, Posicao, DataNascimento, Nacionalidade)
- Tecnico(IdTecnico, Nome, Nacionalidade)
- Arbitro(IdArbitro, Nome, Nacionalidade)
- Evento(IdEvento, Minuto, Tipo, IdPartida)
- Gol(IdEvento, TipoGol, IdJogador, IdSelecao)
- Substituicao(IdEvento, IdJogadorSai, IdJogadorEntra)
- Cartao(IdEvento, TipoCartao, IdJogador)

Responda SOMENTE com a query SQL final, sem explicacoes,
sem comentarios e sem blocos de codigo (markdown).
"""


def _limpar_sql(texto: str) -> str:
    """Remove cercas de markdown e prefixos comuns no retorno do modelo."""
    texto = texto.strip()
    texto = re.sub(r"^```(?:sql)?\s*", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\s*```$", "", texto)
    texto = re.sub(r"^(SQL|Query)\s*:\s*", "", texto, flags=re.IGNORECASE)
    return texto.strip()


def traduzir_para_sql(pergunta: str, modelo: str | None = None,
                      url: str | None = None, timeout: int = 60) -> str:
    """Envia a pergunta ao Ollama e devolve o SQL produzido.

    Configuracao via variaveis de ambiente: OLLAMA_URL, OLLAMA_MODEL.
    """
    payload = {
        "model": modelo or _modelo_padrao(),
        "prompt": pergunta,
        "system": SYSTEM_PROMPT,
        "stream": False,
    }
    resposta = requests.post(url or _url(), json=payload, timeout=timeout)
    resposta.raise_for_status()
    dados = resposta.json()
    return _limpar_sql(dados.get("response", ""))
