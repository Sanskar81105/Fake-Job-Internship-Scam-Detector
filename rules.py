"""
rules.py - deterministic rule-based engine for scam detection.
"""
import re
from typing import List, Dict

RULES = [
    {
        "key": "registration_fee",
        "pattern": re.compile(r"\b(registration fee|registration fees|register fee)\b", re.I),
        "score": 30,
        "reason": "Mentions registration fee",
    },
    {
        "key": "training_fee",
        "pattern": re.compile(r"\b(training fee|training fees|pay for training|training cost)\b", re.I),
        "score": 30,
        "reason": "Mentions training fee",
    },
    {
        "key": "whatsapp_only",
        "pattern": re.compile(r"\b(whatsapp only|whatsapp-only|contact on whatsapp|only whatsapp)\b", re.I),
        "score": 20,
        "reason": "WhatsApp-only hiring or contact",
    },
    {
        "key": "free_email",
        "pattern": re.compile(r"\b[A-Z0-9._%+-]+@(gmail|yahoo)\.(com|in|co\.uk|net)\b", re.I),
        "score": 15,
        "reason": "Uses a free email provider (gmail/yahoo)",
    },
    {
        "key": "no_interview",
        "pattern": re.compile(r"\b(no interview|required no interview|no-interview|immediate hire|instant hire|start immediately)\b", re.I),
        "score": 20,
        "reason": "No interview or immediate hire promised",
    },
    {
        "key": "unreal_salary",
        "pattern": re.compile(
            r"\b(earn\s*\$?\d{3,}|\$\d{3,}\s*(per|/)\s*(week|day|month)|earn upto|earn up to|unrealistic pay|make \$\d+)\b",
            re.I,
        ),
        "score": 25,
        "reason": "Makes unrealistic earnings/salary claims",
    },
]


def risk_level_from_score(score: int) -> str:
    if score <= 30:
        return "LOW"
    if 31 <= score <= 60:
        return "MEDIUM"
    return "HIGH"


def analyze_text(text: str) -> Dict:
    if text is None:
        text = ""
    reasons: List[str] = []
    score = 0

    for rule in RULES:
        try:
            pattern = rule["pattern"]
            if pattern.search(text):
                reasons.append(rule["reason"])
                score += int(rule["score"])
        except Exception:
            continue

    score = max(0, min(100, int(score)))
    if score == 0 and not reasons:
        reasons = ["No scam indicators detected"]

    level = risk_level_from_score(score)
    return {"risk_score": score, "risk_level": level, "reasons": reasons}
