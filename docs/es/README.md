# Yum Bot — Español

<p align="center">
  <a href="../en/README.md">EN</a> ·
  <a href="../pt-br/README.md">PT-BR</a> ·
  <strong>ES</strong>
  &nbsp;·&nbsp;
  <a href="../../README.MD">Idiomas</a>
</p>

> **En desarrollo** (*em desenvolvimento*). Esta documentación todavía está empezando. El repositorio también: es el **principio del principio**.

---

**Yum** es un bot de Discord para comunidades que aprenden juntas.

En el día a día del servidor cubre lo que la mayoría de las guilds espera de un bot “completo”: **XP por hablar en el chat**, participar en actividades y **quedarse en las llamadas**. Quien se involucra en la comunidad sube en el ranking.

Lo que marca el proyecto es el **enfoque en estudios**. Yum va a **generar ejercicios de programación todos los días**. Cada ronda puede ser **casual** (practicar sin presión) o **competición** (competir con el servidor). Al resolver, la persona recibe una **nota** por la calidad de la solución — y esa nota define el XP: **cuanto mejor sea la resolución, más XP**.

Como el eje es el aprendizaje, **no hay techo de alcance**. El bot puede crecer hacia lo que tenga sentido para estudiar — nuevos tipos de ejercicio, nuevas formas de evaluar, nuevas dinámicas en Discord. Vamos a **ampliar el horizonte sobre todo en LM (Language Models)**: generar contenido, corregir respuestas y adaptar el ritmo de quien está aprendiendo.

### Open source

El proyecto es **open source**. Si quieres participar, **eres bienvenido**.

También puedes usar esta base en tu propio proyecto, **siempre que des los créditos**.

### Arquitectura

Capas simples, estilo **bot + cogs + servicios + persistencia**:

| Capa | Dónde | Rol |
| --- | --- | --- |
| Entrada | `main.py` | Token, intents, carga cogs, arranca el bot |
| Extensiones | `App/cogs/` | Comandos y listeners de Discord (ej.: welcome/goodbye) |
| Servicios | `App/services/` | Reglas de negocio (ranking de XP, config del servidor) |
| Datos | `App/database/` | SQLAlchemy (modelos, sesión, engine) |
| Migraciones | `alembic/` | Evolución del schema en PostgreSQL |

Flujo típico: evento o comando en el cog → servicio (`RankingManager`, `ServersConfigManager`) → sesión SQLAlchemy → PostgreSQL.

Stack actual: **Python**, **discord.py**, **SQLAlchemy**, **Alembic**, **PostgreSQL** (vía Docker), **Ruff**.

### Ruff

[Ruff](https://docs.astral.sh/ruff/) es el linter y formateador del proyecto: señala errores, imports desordenados y estilo inconsistente, y puede corregir gran parte de eso solo. La configuración está en `pyproject.toml`. Conviene ejecutarlo **antes de abrir un PR** (y después de tocar Python).

```bash
# qué está fuera del estándar
ruff check .

# aplica correcciones automáticas (imports, algunas reglas)
ruff check . --fix

# formatea el código
ruff format .
```

Un check limpio (sin findings) significa que el árbol actual pasó el Ruff.

### Cómo ejecutarlo

**Requisitos:** Python 3.12+, Docker (para Postgres), token de un bot en el [Discord Developer Portal](https://discord.com/developers/applications).

```bash
git clone <url-del-repositorio>
cd yum-bot

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edita .env: YUM_BOT_TOKEN y DATABASE_URL si hace falta

docker compose up -d

alembic upgrade head

python main.py
```

Postgres queda en el puerto **15432**. La URL por defecto está en `.env.example`.
