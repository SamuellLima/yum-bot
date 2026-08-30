# Yum Bot — English

<p align="center">
  <strong>EN</strong> ·
  <a href="../pt-br/README.md">PT-BR</a> ·
  <a href="../es/README.md">ES</a>
  &nbsp;·&nbsp;
  <a href="../../README.MD">Languages</a>
</p>

> **Under development** (*em desenvolvimento*). This documentation is still early. So is the repo: it is the **very beginning**.

---

**Yum** is a Discord bot for communities that learn together.

Day to day, it covers what most servers expect from a “full” bot: **XP for chatting**, joining activities, and **staying in voice**. People who show up in the community climb the ranking.

What sets the project apart is the **study focus**. Yum will **generate programming exercises every day**. Each round can be **casual** (practice with no pressure) or **competition** (play against the server). When you submit a solution, you get a **score** for how good it is — and that score drives XP: **a better solution means more XP**.

Because the axis is learning, **there is no scope ceiling**. The bot can grow into whatever helps people study — new exercise types, new ways to grade, new Discord flows. We will **push the horizon especially around LM (Language Models)**: generating content, grading answers, and adapting the pace to each learner.

### Open source

This project is **open source**. Want to help? **You are welcome.**

You may also use this codebase as a starting point for your own project, **as long as you give credit**.

### Architecture

A simple **bot + cogs + services + persistence** layout:

| Layer | Where | Role |
| --- | --- | --- |
| Entry | `main.py` | Token, intents, load cogs, run the bot |
| Extensions | `App/cogs/` | Discord commands and listeners (e.g. welcome/goodbye) |
| Services | `App/services/` | Business rules (XP ranking, guild config) |
| Data | `App/database/` | SQLAlchemy (models, session, engine) |
| Migrations | `alembic/` | PostgreSQL schema changes |

Typical flow: cog event/command → service (`RankingManager`, `ServersConfigManager`) → SQLAlchemy session → PostgreSQL.

Current stack: **Python**, **discord.py**, **SQLAlchemy**, **Alembic**, **PostgreSQL** (via Docker), **Ruff**.

### Ruff

[Ruff](https://docs.astral.sh/ruff/) is the project’s linter and formatter: it flags errors, messy imports, and inconsistent style, and can fix a lot of that on its own. Config lives in `pyproject.toml`. Run it **before opening a PR** (and after you change Python files).

```bash
# what is out of standard
ruff check .

# apply automatic fixes (imports, some rules)
ruff check . --fix

# format the code
ruff format .
```

A clean check (no findings) means the current tree passed Ruff.

### How to run

**Requirements:** Python 3.12+, Docker (for Postgres), a bot token from the [Discord Developer Portal](https://discord.com/developers/applications).

```bash
git clone <repository-url>
cd yum-bot

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env: YUM_BOT_TOKEN and DATABASE_URL if needed

docker compose up -d

alembic upgrade head

python main.py
```

Postgres is exposed on port **15432**. The default URL is in `.env.example`.
