# Fake Job / Internship Scam Detector — Backend (Flask + MySQL)

This backend implements a deterministic, explainable rule-based analyzer for job/internship descriptions.

Features
- GET /health — service + DB availability
- POST /analyze-job — analyze job text and return:
  - risk_score (0-100)
  - risk_level (LOW | MEDIUM | HIGH)
  - reasons (array of matched human-readable reasons)
  - persisted (boolean): whether the result was saved to DB

Design principles
- Deterministic rule engine (rules/rules.py). Same input → same output.
- Explainable reasons for every matched rule.
- Persistence to MySQL for auditability and future training.

Quick start (local)
1. Create a MySQL database and user:
   - Example:
     CREATE DATABASE scam_detector CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
     CREATE USER 'scam_user'@'%' IDENTIFIED BY 'your_password';
     GRANT ALL PRIVILEGES ON scam_detector.* TO 'scam_user'@'%';
     FLUSH PRIVILEGES;

2. Copy `.env.example` -> `.env` and set DB_* env vars.

3. Install dependencies:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

4. Start the Flask app:
   python server.py

   For production, run behind Gunicorn:
   gunicorn -w 3 -b 127.0.0.1:8000 server:app

API examples

Health:
curl -i http://localhost:5000/health

Analyze (example):
curl -i -X POST http://localhost:5000/analyze-job \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Immediate hire! No interview. Pay a registration fee of $50. Contact via WhatsApp only."}'

Sample response:
{
  "risk_score": 80,
  "risk_level": "HIGH",
  "reasons": [
    "Mentions registration fee",
    "WhatsApp-only hiring or contact",
    "No interview or immediate hire promised"
  ],
  "persisted": true
}

Notes & operational considerations
- The backend expects the MySQL database/schema to exist. The app will create the analyses table automatically (if it can connect).
- Rules are located in `rules.py`. They are intentionally simple regex-based and ordered deterministically.
- The DB `reasons` column is JSON; ensure your MySQL version supports JSON (5.7+). If you need compatibility with older MySQL versions, change the column to TEXT and store JSON strings.
- The service is intentionally authentication-free (per constraints). Add network-level protections in production.
- For high availability and performance, run this Flask app behind a WSGI server (Gunicorn/Uvicorn) and use an external connection pooler if needed.

Extending the system
- Add more rules to `RULES` in rules.py. Keep scores deterministic and document changes.
- Add an admin endpoint to query persisted analyses for auditing (not included here).
- Replace or augment the rule engine with ML later; keep the rules for explainability fallback.

If you want, I can:
- Provide a SQL migration script for your specific MySQL setup.
- Add an auditing / query endpoint to list past analyses (paginated).
- Convert persistence to use SQLAlchemy for easier migrations.
