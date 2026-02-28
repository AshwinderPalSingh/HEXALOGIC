========
HexLogic
========

.. image:: api/static/hexlogic-logo.png
   :alt: HexLogic Logo

|license|

Professional AT89C51/8051 web simulator with assembler, memory/register views,
step-by-step debugging, breakpoints, and IDE-style workflow.

Project Origin and Attribution
==============================

This project started by cloning the original open-source repository:

`devanshshukla99/8051-Simulator <https://github.com/devanshshukla99/8051-Simulator>`_

HexLogic is a heavily customized and extended version with:

- modernized UI/UX
- expanded instruction behavior fixes
- improved label and jump handling
- better debugger visibility and runtime feedback
- export/help tooling for practical usage

Features
========

- AT89C51-focused simulation flow
- Assemble, Run, Step, Pause, Stop, Run-to-Cursor controls
- Runtime line tracking and current-instruction highlighting
- Internal RAM and Code ROM live views
- Register, flag, register-bank and SFR watch tables
- Breakpoint support via editor gutter
- Memory edit support
- Base converter (Hex/Dec/Bin)
- Download full simulation snapshot (JSON report)
- Help/contact panel inside UI

Current UI Contact
==================

- Help email: ``ashwinder.p.prof@gmail.com``

Tech Stack
==========

- Backend: Flask + Python core simulation engine
- Frontend: HTML/CSS/JavaScript (single-page simulator interface)
- Tests: pytest

Local Development
=================

1. Clone repository and enter project:

   .. code-block:: bash

      git clone <your-repo-url>
      cd 8051-Simulator

2. Create and activate virtual environment:

   .. code-block:: bash

      python3 -m venv .venv
      source .venv/bin/activate

3. Install dependencies:

   .. code-block:: bash

      pip install -e .

4. Run server:

   .. code-block:: bash

      flask --app api/index.py run --debug

5. Open:

   - ``http://127.0.0.1:5000``

Testing
=======

Run full test suite:

.. code-block:: bash

   .venv/bin/python -m pytest -q

Deployment Direction
====================

Recommended production split deployment:

- Frontend: Netlify (GitHub auto-deploy)
- Backend API: Render Web Service (Flask)

This gives CDN-fast frontend delivery and stable Python backend hosting.
Repository can be published to GitHub first, then connected to Netlify/Render.

License
=======

MIT License.

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :alt: License
