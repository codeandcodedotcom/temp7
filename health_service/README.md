## Endpoints
- `GET /health/ping` — Liveness
- `GET /health/hello` — Metadata
- `POST /health/post` — POST echo
- `GET /health/postgres` — DB connectivity (DSN or Managed Identity)
- `GET /health/openai` — OpenAI auth check

## Running Locally
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py


gunicorn -w 4 -b 0.0.0.0:$PORT app:create_app()
