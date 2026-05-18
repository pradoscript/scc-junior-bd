# Prototipo Copa do Mundo

CLI em Python que conecta ao PostgreSQL, executa as 10 consultas predefinidas
do projeto, aceita SQL livre e traduz perguntas em portugues para SQL via
Ollama (modelo local).

## Pre-requisitos

- Python 3.10+
- PostgreSQL rodando (recomendado: `docker compose up -d` na raiz do repo)
- Ollama instalado e com um modelo baixado (ex: `ollama pull llama3.2`)

## Instalacao

```bash
pip install -r requirements.txt
```

## Configuracao

Os parametros de conexao podem vir de variaveis de ambiente (ou do arquivo
`.env` na raiz do repo). Exemplo em `.env.example`:

```
POSTGRES_USER=copa_admin
POSTGRES_PASSWORD=...
POSTGRES_DB=copa_do_mundo
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2
```

Copie `.env.example` para `.env` e ajuste a senha.

## Uso

```bash
python prototipo/main.py
```

O programa pede os parametros de conexao (com defaults vindos do `.env`),
abre conexao com o banco e exibe um menu:

- `[1]..[10]` consultas predefinidas (perguntam parametros conforme necessario)
- `[11]` consulta em linguagem natural (via Ollama)
- `[12]` SQL livre (terminar com linha `;;`)
- `[0]` sair

## Arquivos

- `db.py` — abre conexao e executa SQL
- `queries.py` — as 10 consultas parametrizadas
- `ollama_client.py` — chamada HTTP ao Ollama
- `main.py` — menu interativo
