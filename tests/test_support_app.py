from app.database import SupportTicket, create_sample_data, get_db_session
from app.knowledge_base import retrieve_knowledge
from app.tools import cancel_order, check_refund_status, get_order_status
from app.agent import CustomerSupportAgent


def test_knowledge_base_question():
    result = retrieve_knowledge("How long does shipping take?")
    assert result is not None
    assert any(item["title"] == "Shipping Policy" for item in result)


def test_order_lookup_success():
    create_sample_data()
    order = get_order_status("ORD1001")
    assert order["found"] is True
    assert order["order_id"] == "ORD1001"


def test_invalid_order_id():
    order = get_order_status("ORD9999")
    assert order["found"] is False
    assert "not found" in order["message"].lower()


def test_refund_status():
    status = check_refund_status("ORD1002")
    assert status["found"] is True
    assert status["status"] in {"approved", "processing", "completed"}


def test_cancel_order_request():
    result = cancel_order("ORD1001")
    assert result["success"] is True
    assert result["status"] == "cancelled"


def test_human_escalation_request():
    agent = CustomerSupportAgent()
    response = agent.process_message("session-esc", "I want to speak to a human agent.")
    assert "human" in response["response"].lower()
    assert response["escalated"] is True


def test_multi_turn_conversation_context():
    agent = CustomerSupportAgent()
    first = agent.process_message("session-ctx", "My order is late.")
    second = agent.process_message("session-ctx", "ORD1002.")
    assert first["response"]
    assert second["response"]
    assert "ORD1002" in second["response"] or "order" in second["response"].lower()


def test_empty_message_handling():
    agent = CustomerSupportAgent()
    result = agent.process_message("session-empty", "   ")
    assert "please provide" in result["response"].lower()


def test_missing_order_id_asks_for_information():
    agent = CustomerSupportAgent()
    result = agent.process_message("session-missing-order", "Where is my order?")
    assert "order id" in result["response"].lower()
    assert result["tool_used"] is None


def test_multi_turn_follow_up_after_missing_order_id():
    agent = CustomerSupportAgent()
    first = agent.process_message("session-followup", "Where is my order?")
    second = agent.process_message("session-followup", "ORD1001")
    assert "order id" in first["response"].lower()
    assert second["response"]
    assert "ORD1001" in second["response"]


def test_refund_policy_question_uses_knowledge_base():
    result = retrieve_knowledge("What is your refund policy?")
    assert result
    assert any(item["title"] == "Refund Policy" for item in result)


def test_agent_returns_policy_answer_without_order_id():
    agent = CustomerSupportAgent()
    result = agent.process_message("session-policy-refund", "What is your refund policy?")
    assert "refund" in result["response"].lower()
    assert "order id" not in result["response"].lower()
    assert result["tool_used"] is None


def test_cancellation_is_blocked_for_delivered_orders():
    create_sample_data()
    result = cancel_order("ORD1003")
    assert result["success"] is False
    assert "already delivered" in result["message"].lower()


def test_cancel_order_updates_database_state():
    create_sample_data()
    result = cancel_order("ORD1002")
    assert result["success"] is True
    updated = get_order_status("ORD1002")
    assert updated["found"] is True
    assert updated["status"] == "cancelled"


def test_human_escalation_creates_support_ticket():
    create_sample_data()
    agent = CustomerSupportAgent()
    response = agent.process_message("session-ticket", "I need to speak to a human agent about my order ORD1001.")
    assert response["escalated"] is True
    assert "ticket" in response["response"].lower()
    ticket_id = response["ticket_id"]
    with get_db_session() as session:
        ticket = session.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
        assert ticket is not None
        assert ticket.customer_id == "CUST1001"


def test_unsupported_request_returns_safe_help_message():
    agent = CustomerSupportAgent()
    result = agent.process_message("session-unsupported", "Can you give me today's crypto price?")
    assert "order support" in result["response"].lower()
    assert result["tool_used"] is None


def test_default_database_url_is_serverless_safe_on_vercel(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    import importlib
    import app.config as config

    importlib.reload(config)
    assert "/tmp/" in config.DATABASE_URL or "tmp" in config.DATABASE_URL.lower()

    monkeypatch.delenv("VERCEL", raising=False)
    importlib.reload(config)
    assert "customer_support.db" in config.DATABASE_URL
