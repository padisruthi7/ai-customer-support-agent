import os
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String(50), nullable=False)
    item = Column(String(150), nullable=False)
    total = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    shipping_eta = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), nullable=False)
    customer_id = Column(String(50), nullable=False)
    amount = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String(50), nullable=False)
    order_id = Column(String(50), nullable=True)
    subject = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    status = Column(String(50), default="open")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False)
    customer_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    create_sample_data()


def get_db_session():
    return SessionLocal()


def create_sample_data() -> None:
    with SessionLocal() as session:
        session.query(ConversationMessage).delete()
        session.query(ConversationSession).delete()
        session.query(SupportTicket).delete()
        session.query(Refund).delete()
        session.query(Order).delete()
        session.query(Customer).delete()

        session.add_all(
            [
                Customer(customer_id="CUST1001", name="Aisha Khan", email="aisha@example.com"),
                Customer(customer_id="CUST1002", name="Daniel Smith", email="daniel@example.com"),
                Customer(customer_id="CUST1003", name="Maya Patel", email="maya@example.com"),
            ]
        )

        session.add_all(
            [
                Order(order_id="ORD1001", customer_id="CUST1001", item="Wireless Headphones", total="$89.99", status="in_transit", shipping_eta="2 days"),
                Order(order_id="ORD1002", customer_id="CUST1002", item="Smart Watch", total="$149.99", status="processing", shipping_eta="4 days"),
                Order(order_id="ORD1003", customer_id="CUST1003", item="Portable Speaker", total="$59.99", status="delivered", shipping_eta="Delivered on 2026-09-10"),
            ]
        )

        session.add_all(
            [
                Refund(order_id="ORD1002", customer_id="CUST1002", amount="$149.99", status="approved", reason="Duplicate payment"),
                Refund(order_id="ORD1003", customer_id="CUST1003", amount="$59.99", status="completed", reason="Damaged item"),
            ]
        )

        session.commit()


def get_conversation_session(session_id: str):
    with SessionLocal() as session:
        record = session.query(ConversationSession).filter(ConversationSession.session_id == session_id).first()
        return record


def create_conversation_session(session_id: str, customer_id: Optional[str] = None):
    with SessionLocal() as session:
        record = session.query(ConversationSession).filter(ConversationSession.session_id == session_id).first()
        if record is None:
            record = ConversationSession(session_id=session_id, customer_id=customer_id)
            session.add(record)
            session.commit()
        return record


def save_conversation_message(session_id: str, role: str, content: str):
    with SessionLocal() as session:
        session.add(ConversationMessage(session_id=session_id, role=role, content=content))
        session.commit()


def get_session_history(session_id: str) -> List[str]:
    with SessionLocal() as session:
        messages = session.query(ConversationMessage).filter(ConversationMessage.session_id == session_id).order_by(ConversationMessage.created_at.asc()).all()
        return [{"role": item.role, "content": item.content} for item in messages]


def clear_session(session_id: str):
    with SessionLocal() as session:
        session.query(ConversationMessage).filter(ConversationMessage.session_id == session_id).delete()
        session.query(ConversationSession).filter(ConversationSession.session_id == session_id).delete()
        session.commit()


init_db()


if __name__ == "__main__":
    init_db()
