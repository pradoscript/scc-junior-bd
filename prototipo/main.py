"""Menu interativo do prototipo Copa do Mundo."""
import os
import sys
import traceback
from pathlib import Path

import psycopg2
import requests
from tabulate import tabulate

from db import conectar, executar_query
from ollama_client import traduzir_para_sql
from queries import CONSULTAS


def carregar_env(caminho: Path):
    """Le um arquivo .env simples (KEY=VALUE por linha) e seta no os.environ.

    Linhas vazias ou comecando com # sao ignoradas. Valores ja definidos no
    ambiente tem precedencia.
    """
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        chave = chave.strip()
        valor = valor.strip().strip('"').strip("'")
        os.environ.setdefault(chave, valor)


def ler(prompt: str, padrao: str | None = None) -> str:
    sufixo = f" [{padrao}]" if padrao else ""
    val = input(f"{prompt}{sufixo}: ").strip()
    return val or (padrao or "")


def coletar_conexao() -> dict:
    print("\n=== Parametros de conexao com o PostgreSQL ===")
    host = ler("Host", os.getenv("POSTGRES_HOST", "localhost"))
    porta = ler("Porta", os.getenv("POSTGRES_PORT", "5432"))
    banco = ler("Banco", os.getenv("POSTGRES_DB", "copa_do_mundo"))
    user = ler("Usuario", os.getenv("POSTGRES_USER", "copa_admin"))
    senha = ler("Senha", os.getenv("POSTGRES_PASSWORD", ""))
    return {
        "host": host,
        "port": int(porta),
        "dbname": banco,
        "user": user,
        "password": senha,
    }


def coletar_params(specs):
    valores = {}
    for nome, prompt, conversor in specs:
        while True:
            raw = input(prompt).strip()
            try:
                valores[nome] = conversor(raw)
                break
            except (ValueError, TypeError):
                print(f"  -> valor invalido para '{nome}', tente novamente.")
    return valores


def imprimir_resultado(cols, rows):
    if not cols:
        print("(sem resultado)")
        return
    if not rows:
        print("(nenhuma linha)")
        return
    print(tabulate(rows, headers=cols, tablefmt="psql", showindex=False))
    print(f"\n{len(rows)} linha(s).")


def montar_menu():
    print("\n========== MENU ==========")
    for i, q in enumerate(CONSULTAS, start=1):
        print(f"  [{i:2d}] {q['titulo']}")
    print(f"  [11] Consulta em linguagem natural (via Ollama)")
    print(f"  [12] Executar SQL digitado")
    print(f"  [ 0] Sair")
    print("==========================")


def executar_predefinida(conn, indice: int):
    spec = CONSULTAS[indice - 1]
    print(f"\n>>> {spec['titulo']}")
    params = coletar_params(spec["params"]) if spec["params"] else None
    cols, rows = executar_query(conn, spec["sql"], params)
    imprimir_resultado(cols, rows)


def executar_via_ollama(conn):
    pergunta = input("Pergunta em portugues: ").strip()
    if not pergunta:
        print("Pergunta vazia.")
        return
    try:
        sql = traduzir_para_sql(pergunta)
    except requests.ConnectionError:
        print("Nao foi possivel conectar ao Ollama (esta rodando?).")
        return
    except requests.HTTPError as e:
        print(f"Ollama retornou erro HTTP: {e}")
        return
    print(f"\nSQL gerado:\n{sql}\n")
    if input("Executar? [S/n]: ").strip().lower() in ("", "s", "sim"):
        try:
            cols, rows = executar_query(conn, sql)
            imprimir_resultado(cols, rows)
        except psycopg2.Error as e:
            print(f"Erro ao executar: {e.pgerror or e}")
            conn.rollback()


def executar_sql_livre(conn):
    print("Digite o SQL (terminar com linha contendo apenas ';;'):")
    linhas = []
    while True:
        linha = input()
        if linha.strip() == ";;":
            break
        linhas.append(linha)
    sql = "\n".join(linhas).strip()
    if not sql:
        print("SQL vazio.")
        return
    try:
        cols, rows = executar_query(conn, sql)
        imprimir_resultado(cols, rows)
    except psycopg2.Error as e:
        print(f"Erro ao executar: {e.pgerror or e}")
        conn.rollback()


def main():
    carregar_env(Path(__file__).resolve().parent.parent / ".env")

    while True:
        try:
            params = coletar_conexao()
            conn = conectar(**params)
            print("Conectado.")
            break
        except psycopg2.Error as e:
            print(f"Falha na conexao: {e}")
            if input("Tentar novamente? [S/n]: ").strip().lower() in ("n", "nao"):
                sys.exit(1)

    try:
        while True:
            montar_menu()
            escolha = input("Opcao: ").strip()
            if escolha == "0":
                break
            try:
                if escolha in {str(i) for i in range(1, len(CONSULTAS) + 1)}:
                    executar_predefinida(conn, int(escolha))
                elif escolha == "11":
                    executar_via_ollama(conn)
                elif escolha == "12":
                    executar_sql_livre(conn)
                else:
                    print("Opcao invalida.")
            except psycopg2.Error as e:
                print(f"Erro de banco: {e.pgerror or e}")
                conn.rollback()
            except Exception:
                print("Erro inesperado:")
                traceback.print_exc()
    finally:
        conn.close()
        print("Conexao encerrada.")


if __name__ == "__main__":
    main()
