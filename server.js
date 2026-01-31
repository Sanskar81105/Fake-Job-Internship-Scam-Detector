/**
 * Minimal Express backend to support the frontend.
 * Endpoint: POST /analyze-job
 *
 * This is a simple heuristic-based implementation intended for local testing/demos.
 * It returns JSON: { risk_score: number (0-100), risk_level: "low"|"medium"|"high", reasons: [string] }
 */

const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('.')); // serve frontend static files for simple testing

const PORT = process.env.PORT || 3000;

// Basic heuristics: keywords and patterns to flag
const INDICATORS = [
  { keyword: 'wire transfer', reason: 'Requests payment or wire transfer' },
  { keyword: 'transfer money', reason: 'Requests payment or money transfer' },
  { keyword: 'pay to', reason: 'Mentions paying to start work' },
  { keyword: 'upfront', reason: 'Mentions upfront payment' },
  { keyword: 'western union', reason: 'Mentions Western Union' },
  { keyword: 'western-union', reason: 'Mentions Western Union' },
  { keyword: 'bank account', reason: 'Asks for bank account details' },
  { keyword: 'personal information', reason: 'Requests excessive personal information' },
  { keyword: 'no interview', reason: 'No interview or immediate hire' },
  { keyword: 'guaranteed', reason: 'Promises guaranteed money or position' },
  { keyword: 'work from home and pay', reason: 'Work from home with payment requirement' },
  { keyword: 'pay to apply', reason: 'Charges a fee to apply or be considered' },
  { keyword: 'job placement fee', reason: 'Charges for placement or training' },
  { keyword: 'earn $', reason: 'Offers unrealistic earnings' },
  { keyword: 'earn upto', reason: 'Offers unrealistic earnings' },
  { keyword: 'confidential', reason: 'Requests confidential details before interview' },
];

function analyzeText(text) {
  const lowered = text.toLowerCase();
  const reasons = new Set();
  let score = 0;

  INDICATORS.forEach((ind, idx) => {
    if (lowered.includes(ind.keyword)) {
      reasons.add(ind.reason);
      score += 8 + (idx % 4); // simple varied scoring
    }
  });

  // Additional heuristics
  const contactMatches = (lowered.match(/\b(contact|call|whatsapp|telegram|sms)\b/g) || []).length;
  if (contactMatches > 0) {
    reasons.add('Direct contact instructions provided (call/WhatsApp/Telegram)');
    score += Math.min(10, contactMatches * 3);
  }

  // Look for unrealistic promises or vague recruiter info
  if (/(no experience required|start immediately|instant hire)/i.test(text)) {
    reasons.add('Promises instant hire or no-experience requirement');
    score += 10;
  }

  // Look for vague company info
  if (/(work from home).*?(no company|not disclosed|undisclosed|confidential)/i.test(lowered)) {
    reasons.add('Vague or undisclosed company information');
    score += 8;
  }

  // Cap score
  score = Math.min(100, score);

  // Map to levels
  let risk_level = 'low';
  if (score >= 65 || reasons.size >= 4) risk_level = 'high';
  else if (score >= 30 || reasons.size >= 2) risk_level = 'medium';

  return {
    risk_score: score,
    risk_level,
    reasons: Array.from(reasons),
  };
}

app.post('/analyze-job', (req, res) => {
  const { job_description } = req.body || {};
  if (!job_description || typeof job_description !== 'string') {
    return res.status(400).json({ error: 'job_description is required' });
  }

  try {
    const result = analyzeText(job_description);
    return res.json(result);
  } catch (err) {
    console.error('Analysis error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`Fake Job Scam Detector backend listening on http://localhost:${PORT}`);
});
