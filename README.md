# AI Customer Support Agent

A portfolio-ready AI customer support MVP built with Python, FastAPI, SQLite, and a lightweight local knowledge base. It demonstrates a realistic customer-support workflow where the assistant can answer support questions, look up orders, check refund status, handle cancellations, and escalate to a human support agent when appropriate.

This project is intentionally simple and readable. It is designed for learning, portfolio use, and local demonstration rather than production deployment or real-world company operations.

## Project purpose

This project simulates a practical customer-support experience that combines:

- a browser-based chat UI
- a backend API
- intent detection and response routing
- local support tools
- a knowledge base for policy questions
- SQLite data storage for sessions and sample orders
- human escalation flow with ticket creation

## Key features

- Order status lookup with order ID validation
- Refund status checks based on stored data
- Cancellation rules with business-safe behavior
- Human escalation and generated ticket number
- FAQ and policy answers from a lightweight knowledge base
- Multi-turn conversation memory
- Graceful handling of missing or invalid input
- Local SQLite database with sample customer/support data
- Automated tests for core support workflows

## Architecture

The application follows a simple layered architecture:

- app/main.py: FastAPI routes and app startup
- app/agent.py: support orchestration and customer conversation logic
- app/tools.py: order, refund, cancellation, and escalation functions
- app/knowledge_base.py: policy and FAQ retrieval
- app/database.py: SQLite models, seed data, sessions, and ticket storage
- app/static/: browser frontend with HTML, CSS, and JavaScript
- app/config.py: local configuration and environment variables

## Technologies used

- Python 3.12
- FastAPI
- SQLite
- SQLAlchemy
- python-dotenv
- Google GenAI client
- Pytest
- HTML, CSS, and JavaScript

## Portfolio note

This is a working MVP for demonstration and learning. It is not a production customer support system, not a company deployment, and it does not include authentication, cloud infrastructure, or enterprise integrations.

## Local installation

1. Clone or open the project folder.
2. Create a virtual environment:

   python -m venv .venv

3. Activate the environment:

   .\.venv\Scripts\Activate.ps1

4. Install dependencies:

   python -m pip install -r requirements.txt

## Environment configuration

Create a local environment file from the example:

   copy .env.example .env

The example file includes the expected keys:

   GEMINI_API_KEY=
   MODEL_NAME=gemini-2.0-flash
   DATABASE_URL=sqlite:///customer_support.db

Important notes:

- Do not commit real API keys or secrets.
- The app works locally without a live Gemini key using the default fallback logic.
- The database is stored locally as SQLite and is ignored by git.

## Run the application locally

From the project root:

   .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

Then open:

   http://127.0.0.1:8000/

## Run the tests

From the project root:

   .\.venv\Scripts\python.exe -m pytest -q

## Example support workflows

- "Where is my order?"
- "I need to check the status of ORD1001"
- "What is your refund policy?"
- "I need a refund for ORD1002"
- "Can you cancel my order?"
- "I need to speak to a human agent"

## Known limitations

- The app uses a lightweight local knowledge base instead of a production vector search or enterprise retrieval system.
- Order, refund, and cancellation data are demo data stored in SQLite.
- There is no authentication or user account system.
- The human escalation flow creates a local ticket record rather than integrating with a live support platform.
- The frontend is intentionally minimal and clean for a portfolio demo.

## Future improvements

- Add a staff-facing ticket review view
- Improve retrieval with embeddings or vector search
- Add admin logging and analytics
- Add authentication for user sessions
- Move from SQLite to PostgreSQL for more production-like data handling

## GitHub / portfolio readiness

This project is ready to be placed on GitHub as a local portfolio project and demonstration app.

To initialize Git:

   git init
   git add .
   git commit -m "Initial AI support agent MVP"

Then connect to your remote repository and push:

   git branch -M main
   git remote add origin <your-repository-url>
   git push -u origin main

## Notes

This project is best understood as a working MVP that demonstrates realistic AI customer support patterns in a simple, maintainable architecture.
