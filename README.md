# HexLogic

<p align="center">
  <img src="api/static/hexlogic-logo.png" width="180" alt="HexLogic Logo"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License" />
  <img src="https://img.shields.io/badge/backend-Flask-black" alt="Flask Backend" />
  <img src="https://img.shields.io/badge/frontend-Netlify-00C7B7" alt="Netlify Frontend" />
  <img src="https://img.shields.io/badge/backend%20hosted-Render-46E3B7" alt="Render Backend Hosting" />
</p>

Professional AT89C51 / 8051 web-based simulator with assembler, full debugging workflow, live memory/register views, breakpoints, and an IDE-style interface.

---

## Live Deployment

Frontend (Netlify CDN):  
https://hexalogic-simulator.netlify.app

Backend API (Render Web Service):  
https://hexalogic-api.onrender.com

---

## Overview

HexLogic is a modern web-based 8051 simulator focused on AT89C51 behavior.

It provides:

- Assembly compilation
- Step-by-step execution
- Cycle-accurate simulation
- Internal RAM and Code ROM views
- Register + SFR inspection
- Breakpoints
- Memory editing
- Base conversion utilities
- Exportable debug snapshot

Designed for:

- Embedded systems students
- Microcontroller lab practice
- Teaching environments
- Browser-based debugging without hardware

---


## Architecture

```text
Browser (Netlify SPA)
      |
      | REST API (JSON)
      v
Flask Simulation Engine (Render)
```

### Frontend

- HTML/CSS/JavaScript
- IDE-style UI
- Editor with breakpoint gutter
- Debug controls

### Backend

- Flask REST API
- Python-based 8051 simulation core
- Instruction execution engine
- RAM/ROM/Flag/Register state management

---

## Features

- AT89C51 simulation flow
- Assemble / Run / Step / Pause / Stop / Run-to-Cursor
- Current instruction highlighting
- Live internal RAM viewer
- Code ROM view
- Register bank table
- SFR + flag watch panel
- Breakpoint support
- Memory edit
- Hex/Dec/Bin base converter
- Full simulation state export (JSON)
- In-app help panel

---

## Project Structure

```text
HEXALOGIC/
├── api/
│   ├── index.py            # Flask entry point
│   ├── templates/          # UI templates
│   └── static/             # CSS/JS/images/logo assets
├── core/                   # 8051 simulation engine
├── tests/                  # Pytest test suite
├── .github/workflows/      # CI workflows
├── requirements.txt
└── README.md
```

---

## Local Development

### 1. Clone

```bash
git clone https://github.com/AshwinderPalSingh/HEXALOGIC.git
cd HEXALOGIC
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install

```bash
pip install -e .
```

### 4. Run Backend

```bash
flask --app api/index.py run --debug
```

### 5. Open

```text
http://127.0.0.1:5000
```

---

## Testing

Run full test suite:

```bash
.venv/bin/python -m pytest -q
```

---

## Production Deployment

### Frontend - Netlify

- Connected to GitHub
- Auto-deploy on push
- Static SPA build
- API base URL points to Render backend

### Backend - Render

- Web Service (Flask)
- Gunicorn production server
- Environment variables configured
- CORS enabled for Netlify domain

---

## Environment Variables (Render)

Example:

```bash
FLASK_ENV=production
CORS_ALLOWED_ORIGINS=https://hexalogic-simulator.netlify.app
```

---

## Contact

Help / Support:  
ashwinder.p.prof@gmail.com

---

## License

MIT License. See [LICENSE](LICENSE).
