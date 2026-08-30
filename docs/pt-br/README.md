# Yum Bot — Português (Brasil)

<p align="center">
  <a href="../en/README.md">EN</a> ·
  <strong>PT-BR</strong> ·
  <a href="../es/README.md">ES</a>
  &nbsp;·&nbsp;
  <a href="../../README.MD">Idiomas</a>
</p>

> **Em desenvolvimento.** Esta documentação ainda está no começo. O repositório também: é o **início do início**.

---

O **Yum** é um bot de Discord para comunidades que aprendem juntas.

No dia a dia do servidor, ele cobre o que a maioria das guilds espera de um bot “completo”: **XP por conversar no chat**, participar de atividades e **ficar nas calls**. Quem se envolve na comunidade sobe no ranking.

O que diferencia o projeto é o **foco em estudos**. O Yum vai **gerar exercícios de programação todos os dias** para os membros. Cada round pode ser **casual** (treinar sem pressão) ou **competição** (disputar com o servidor). Ao resolver, a pessoa recebe uma **nota** pela qualidade da solução — e essa nota define o XP: **quanto melhor a resolução, mais XP**.

Como o eixo é estudo, **não há limitações de escopo**. O bot pode crescer para o que fizer sentido na aprendizagem — novos tipos de exercício, novas formas de avaliar, novas dinâmicas no Discord. Vamos **expandir os horizontes principalmente em LM (Language Models)**: gerar conteúdo, corrigir respostas e personalizar o ritmo de quem está aprendendo.

### Open source

O projeto é **open source**. Quem quiser participar, **fique à vontade**.

Você também pode pegar esta base para o seu próprio projeto, **desde que dê os créditos**.

### Arquitetura

Camadas simples, no estilo **bot + cogs + serviços + persistência**:

| Camada | Onde | Papel |
| --- | --- | --- |
| Entrada | `main.py` | Token, intents, carrega cogs, sobe o bot |
| Extensões | `App/cogs/` | Comandos e listeners do Discord (ex.: welcome/goodbye) |
| Serviços | `App/services/` | Regras de negócio (ranking de XP, config do servidor) |
| Dados | `App/database/` | SQLAlchemy (modelos, sessão, engine) |
| Migrações | `alembic/` | Evolução do schema no PostgreSQL |

Fluxo típico: evento ou comando no cog → serviço (`RankingManager`, `ServersConfigManager`) → sessão SQLAlchemy → PostgreSQL.

Stack atual: **Python**, **discord.py**, **SQLAlchemy**, **Alembic**, **PostgreSQL** (via Docker), **Ruff**.

### Ruff

O [Ruff](https://docs.astral.sh/ruff/) é o linter e formatador do projeto: aponta erros, imports bagunçados e estilo inconsistente, e pode corrigir boa parte disso sozinho. A configuração fica em `pyproject.toml`. Vale rodar **antes de abrir um PR** (e depois de mexer no Python).

```bash
# o que está fora do padrão
ruff check .

# aplica correções automáticas (imports, alguns fixes)
ruff check . --fix

# formata o código
ruff format .
```

Um check limpo (sem findings) é o sinal de que o momento atual do código passou no Ruff.

### Como rodar

**Requisitos:** Python 3.12+, Docker (para o Postgres), token de um bot no [Discord Developer Portal](https://discord.com/developers/applications).

```bash
git clone <url-do-repositorio>
cd yum-bot

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edite .env: YUM_BOT_TOKEN e, se precisar, DATABASE_URL

docker compose up -d

alembic upgrade head

python main.py
```

O Postgres sobe na porta **15432**. A URL padrão está em `.env.example`.
