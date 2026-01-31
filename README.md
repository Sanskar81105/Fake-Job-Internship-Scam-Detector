# Fake Job / Internship Scam Detector

A small demo web app to analyze job descriptions for common scam indicators.

Features:
- Paste a job description in the UI and click "Analyze Job".
- Frontend calls a backend endpoint `/analyze-job`.
- Backend returns a risk score (0-100), a risk level (low/medium/high), and a list of reasons/indicators.

Local usage (development):
1. Install dependencies:
   - `npm install`
2. Start the server:
   - `npm start`
3. Open your browser:
   - `http://localhost:3000` (the server serves the static frontend files)

Notes:
- The backend included is a minimal heuristic stub intended for demos and local testing only.
- For production, replace the heuristic logic with a robust service (e.g., an ML model, third-party API, or stricter rules).
- Always encourage users to independently verify job offers.

License: MIT
