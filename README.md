
# FastAPI Audio Service (JWT + Webhook)

Incluye `bcrypt_sha256` para evitar el límite de 72 bytes de bcrypt.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
