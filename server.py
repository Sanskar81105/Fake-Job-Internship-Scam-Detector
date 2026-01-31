#!/usr/bin/env python3
"""
server.py - Flask app factory and endpoints.

Endpoints:
- GET  /health
- POST /analyze-job
- GET  /analyses    # audit endpoint, paginated
"""
import os
import json
import logging
from datetime import datetime

from flask import Flask, request, jsonify, current_app

from rules import analyze_text
from db import init_db, get_session, engine, Base
from models import Analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def create_app(test_config: dict = None):
    app = Flask(__name__)

    # Load configuration from env or test_config (for tests)
    if test_config:
        app.config.update(test_config)
    else:
        # Example: mysql+pymysql://user:pass@host:3306/dbname
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI",
            os.environ.get("DATABASE_URL", "mysql+pymysql://root:@127.0.0.1:3306/scam_detector"),
        )
        app.config["JSON_SORT_KEYS"] = False

    # Initialize DB (create tables if needed)
    try:
        init_db(app.config.get("SQLALCHEMY_DATABASE_URI"))
        logger.info("Database initialized.")
    except Exception:
        logger.exception("Database initialization failed. App will still run but persistence may fail.")

    @app.route("/health", methods=["GET"])
    def health():
        """
        Basic health including DB connectivity.
        """
        db_ok = False
        try:
            session = get_session()
            # lightweight check
            session.execute("SELECT 1")
            session.close()
            db_ok = True
        except Exception:
            logger.exception("DB health check failed")
            db_ok = False

        status = {"status": "ok", "db": "ok" if db_ok else "unavailable"}
        return jsonify(status), 200 if db_ok else 503

    @app.route("/analyze-job", methods=["POST"])
    def analyze_job():
        """
        Accepts JSON { "job_description": "<text>" }
        Returns: { risk_score, risk_level, reasons[], persisted: bool }
        """
        try:
            payload = request.get_json(force=True)
        except Exception:
            return jsonify({"error": "Invalid JSON body"}), 400

        if not payload or "job_description" not in payload:
            return jsonify({"error": "Missing 'job_description' in request body"}), 400

        job_description = payload.get("job_description", "")
        if not isinstance(job_description, str) or not job_description.strip():
            return jsonify({"error": "'job_description' must be a non-empty string"}), 400

        # Analyze text deterministically
        result = analyze_text(job_description)

        # Persist (best-effort)
        persisted = False
        try:
            session = get_session()
            analysis = Analysis(
                job_description=job_description,
                risk_score=int(result["risk_score"]),
                risk_level=result["risk_level"],
                reasons=result["reasons"],
                created_at=datetime.utcnow(),
            )
            session.add(analysis)
            session.commit()
            persisted = True
            # Optionally attach database id
            result["id"] = analysis.id
            session.close()
        except Exception:
            logger.exception("Failed to persist analysis result")

        response = {
            "risk_score": int(result["risk_score"]),
            "risk_level": result["risk_level"].upper(),
            "reasons": result["reasons"],
            "persisted": persisted,
        }
        if "id" in result:
            response["id"] = result["id"]
        return jsonify(response), 200

    @app.route("/analyses", methods=["GET"])
    def list_analyses():
        """
        Audit endpoint: GET /analyses
        Query params:
          - page (default 1)
          - per_page (default 20, max 200)
          - risk_level (LOW|MEDIUM|HIGH) optional
          - start_date, end_date (ISO 8601) optional
          - q (search in job_description) optional
          - sort (created_at, -created_at) default -created_at
        Response:
        {
          "total": int,
          "page": int,
          "per_page": int,
          "total_pages": int,
          "items": [ {id, risk_score, risk_level, reasons, created_at, job_description_truncated}, ... ]
        }
        """
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 20))
            per_page = max(1, min(per_page, 200))
        except ValueError:
            return jsonify({"error": "Invalid pagination parameters"}), 400

        risk_level = request.args.get("risk_level")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        q = request.args.get("q")
        sort = request.args.get("sort", "-created_at")

        session = get_session()
        try:
            query = session.query(Analysis)

            if risk_level:
                query = query.filter(Analysis.risk_level == risk_level.upper())

            if start_date:
                try:
                    dt = datetime.fromisoformat(start_date)
                    query = query.filter(Analysis.created_at >= dt)
                except ValueError:
                    return jsonify({"error": "start_date must be ISO 8601"}), 400

            if end_date:
                try:
                    dt = datetime.fromisoformat(end_date)
                    query = query.filter(Analysis.created_at <= dt)
                except ValueError:
                    return jsonify({"error": "end_date must be ISO 8601"}), 400

            if q:
                query = query.filter(Analysis.job_description.ilike(f"%{q}%"))

            # sort
            if sort == "created_at":
                query = query.order_by(Analysis.created_at.asc())
            else:
                # default -created_at
                query = query.order_by(Analysis.created_at.desc())

            total = query.count()
            total_pages = (total + per_page - 1) // per_page if per_page else 1
            items = query.offset((page - 1) * per_page).limit(per_page).all()

            def to_dict(a: Analysis):
                return {
                    "id": a.id,
                    "risk_score": a.risk_score,
                    "risk_level": a.risk_level,
                    "reasons": a.reasons,
                    "created_at": a.created_at.isoformat() + "Z" if a.created_at else None,
                    # truncate job_description for listings
                    "job_description_snippet": (a.job_description[:500] + "...") if a.job_description and len(a.job_description) > 500 else a.job_description,
                }

            payload = {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "items": [to_dict(i) for i in items],
            }
            return jsonify(payload), 200
        except Exception:
            logger.exception("Failed to query analyses")
            return jsonify({"error": "Internal server error"}), 500
        finally:
            session.close()

    return app


if __name__ == "__main__":
    # Non-test run
    app = create_app()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug_env = os.environ.get("FLASK_DEBUG", "0")
    debug = debug_env == "1"
    logger.info("Starting Flask server at %s:%s (debug=%s)", host, port, debug)
    app.run(host=host, port=port, debug=debug)
