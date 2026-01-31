import pytest
from rules import analyze_text

def test_no_indicators():
    res = analyze_text("This is a normal job posting with detailed company info.")
    assert res["risk_score"] == 0
    assert "No scam indicators detected" in res["reasons"]
    assert res["risk_level"] == "LOW"

def test_registration_fee_and_whatsapp():
    txt = "Immediate hire. Please pay a registration fee of $25. Contact on WhatsApp only."
    res = analyze_text(txt)
    # registration_fee 30 + whatsapp 20 = 50
    assert res["risk_score"] == 50
    assert res["risk_level"] == "MEDIUM"
    assert "Mentions registration fee" in res["reasons"]
    assert any("WhatsApp" in r for r in res["reasons"])

def test_unreal_salary():
    txt = "Earn $5000 per week, no experience needed."
    res = analyze_text(txt)
    # unreal_salary 25 + no_interview 20 -> 45
    assert res["risk_score"] >= 45
    assert res["risk_level"] in ("MEDIUM", "HIGH")
