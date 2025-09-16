# Pressure Decision Snapshot (T-002)

A rule-based web utility that turns a pasted high-pressure situation into a one-page decision snapshot. Paste the facts, hit **Create snapshot**, and the app lays out context, options, tradeoffs, decision, next step, and risks.

## Features

- Pure heuristics (no external APIs) with tight keyword matching for options, tradeoffs, and risks.
- Guards against oversized pastes (2,000 characters) and highlights when no structure was detected.
- Clean single-page UI that always renders the seven snapshot sections.

## Getting Started

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the Flask development server:

   ```bash
   flask --app t002_decision_snapshot.app run
   ```

3. Open the app at http://127.0.0.1:5000 and paste a situation similar to the golden-path example.

## Golden-Path Input

```
We need to decide whether to ship v1 without SSO for the pilot this Friday.
Users: 12 pilot accounts; low security risk; time pressure high.
Options: (1) Ship without SSO; (2) Delay 2 weeks for SSO; (3) Limit to 5 users and add SSO later.
Pros/Cons: (1) fast but some friction later; (2) safer but we miss momentum; (3) middle ground but adds support cost.
Risks: customer loses interest if we delay; rework if SSO changes routes.
Next: choose today; owner = Graham; deadline = 4pm.
```

The app should surface at least three options, two tradeoffs, and a single next step with owner and deadline.
