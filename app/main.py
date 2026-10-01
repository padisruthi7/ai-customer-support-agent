from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent import CustomerSupportAgent
from app.database import clear_session, init_db

app = FastAPI(title="AI Customer Support Agent")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": "Invalid request payload."})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Something went wrong while handling the request."})


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    customer_id: Optional[str] = None


class ResetRequest(BaseModel):
    session_id: str


@app.get("/")
def read_index():
    return FileResponse("app/static/index.html")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "AI Customer Support Agent"}


@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    agent = CustomerSupportAgent()
    reply = agent.process_message(payload.session_id or "default-session", payload.message, customer_id=payload.customer_id)
    return reply


@app.post("/api/reset")
def reset_session(payload: ResetRequest):
    clear_session(payload.session_id)
    return {"status": "ok", "session_id": payload.session_id}
