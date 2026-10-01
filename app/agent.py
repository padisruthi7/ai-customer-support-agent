import re
import uuid
from typing import Optional

from app.config import GEMINI_API_KEY, MODEL_NAME
from app.database import create_conversation_session, get_session_history, save_conversation_message
from app.knowledge_base import retrieve_knowledge
from app.tools import cancel_order, check_refund_status, create_support_ticket, escalate_to_human, get_customer_order_history, get_order_status

try:
    from google import genai
except Exception:  # pragma: no cover
    genai = None


def _extract_order_id(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"ORD\d+", text.upper())
    return match.group(0) if match else None


class CustomerSupportAgent:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model_name = MODEL_NAME

    def _call_llm(self, prompt: str) -> str:
        if not self.api_key or genai is None:
            return ""

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(model=self.model_name, contents=prompt)
            return getattr(response, "text", str(response)) or ""
        except Exception:
            return ""

    def _get_last_order_reference(self, session_id: str) -> Optional[str]:
        history = get_session_history(session_id)
        for message in reversed(history):
            order_id = _extract_order_id(message["content"])
            if order_id:
                return order_id
        return None

    def _get_pending_action(self, session_id: str) -> Optional[str]:
        history = get_session_history(session_id)
        for message in reversed(history):
            if message.get("role") != "assistant":
                continue
            content = (message.get("content") or "").lower()
            if "cancel" in content and "order" in content and "order id" in content:
                return "cancel_order"
            if "refund" in content and "order id" in content:
                return "check_refund_status"
            if "current status" in content or ("order" in content and "status" in content and "order id" in content):
                return "get_order_status"
            if "human" in content and "ticket" in content:
                return "escalate_to_human"
        return None

    def _handle_tool_request(self, session_id: str, message: str, order_id: Optional[str], customer_id: Optional[str]):
        lower = message.lower()
        pending_action = self._get_pending_action(session_id)

        if pending_action and order_id:
            if pending_action == "cancel_order":
                result = cancel_order(order_id)
                response = result["message"]
                return response, "cancel_order", False, [], None
            if pending_action == "check_refund_status":
                result = check_refund_status(order_id)
                response = result["message"]
                return response, "check_refund_status", False, [], None
            if pending_action == "get_order_status":
                result = get_order_status(order_id)
                response = result["message"]
                return response, "get_order_status", False, [], None
            if pending_action == "escalate_to_human":
                ticket = escalate_to_human(customer_id or "CUST1001", order_id, "Customer requested follow-up help after a missing information prompt.")
                response = ticket["message"]
                return response, "escalate_to_human", True, [], ticket.get("ticket_id")

        if "human" in lower or "agent" in lower or "speak to a human" in lower or "speak to someone" in lower:
            ticket = escalate_to_human(customer_id or "CUST1001", order_id, "Customer explicitly requested a human support agent.")
            response = ticket["message"]
            return response, "escalate_to_human", True, [], ticket.get("ticket_id")

        policy_keywords = [
            "policy",
            "refund policy",
            "return policy",
            "shipping policy",
            "cancellation policy",
            "cancel policy",
            "payment policy",
            "warranty",
        ]
        is_policy_question = "policy" in lower or "faq" in lower
        if is_policy_question and any(keyword in lower for keyword in ["refund", "return", "shipping", "cancel", "payment", "warranty"]):
            return None, None, False, [], None

        if "cancel" in lower and "order" in lower and "policy" not in lower:
            if not order_id:
                response = "Please provide your order ID so I can check whether it can be cancelled."
                return response, None, False, [], None
            result = cancel_order(order_id)
            response = result["message"]
            return response, "cancel_order", False, [], None

        if ("refund" in lower or "money back" in lower) and "policy" not in lower and "status" not in lower:
            if not order_id:
                response = "Please share your order ID so I can check the refund status."
                return response, None, False, [], None
            result = check_refund_status(order_id)
            response = result["message"]
            return response, "check_refund_status", False, [], None

        if ("refund" in lower or "money back" in lower) and ("policy" in lower or "faq" in lower):
            return None, None, False, [], None

        if "order" in lower and ("status" in lower or "where" in lower or "late" in lower or "track" in lower):
            if not order_id:
                response = "I can help with that. Please provide your order ID so I can check the current status."
                return response, None, False, [], None
            result = get_order_status(order_id)
            response = result["message"]
            return response, "get_order_status", False, [], None

        if "history" in lower or "past orders" in lower:
            if not customer_id:
                response = "I can look up your order history. Please provide your customer ID or use your account profile."
                return response, None, False, [], None
            history = get_customer_order_history(customer_id)
            if not history:
                response = "I could not find any orders for that customer profile."
            else:
                response = "Your recent orders: " + "; ".join(f"{item['order_id']} ({item['status']})" for item in history)
            return response, "get_customer_order_history", False, [], None

        return None, None, False, [], None

    def process_message(self, session_id: str, user_message: str, customer_id: Optional[str] = None):
        session_id = session_id or uuid.uuid4().hex
        message = (user_message or "").strip()
        create_conversation_session(session_id, customer_id)
        save_conversation_message(session_id, "user", message)

        if not message:
            reply = "Please provide a message and I will help with your support request."
            save_conversation_message(session_id, "assistant", reply)
            return {
                "session_id": session_id,
                "response": reply,
                "tool_used": None,
                "knowledge_used": [],
                "escalated": False,
            }

        order_id = _extract_order_id(message) or self._get_last_order_reference(session_id)
        pending_action = self._get_pending_action(session_id)

        if pending_action and not order_id:
            if pending_action == "get_order_status":
                response = "I can help with that. Please provide your order ID so I can check the current status."
                save_conversation_message(session_id, "assistant", response)
                return {
                    "session_id": session_id,
                    "response": response,
                    "tool_used": None,
                    "knowledge_used": [],
                    "escalated": False,
                }

        tool_response = self._handle_tool_request(session_id, message, order_id, customer_id)
        response, tool_used, escalated, knowledge_used, ticket_id = tool_response
        if response is not None:
            result = {
                "session_id": session_id,
                "response": response,
                "tool_used": tool_used,
                "knowledge_used": knowledge_used,
                "escalated": escalated,
            }
            if ticket_id:
                result["ticket_id"] = ticket_id
            save_conversation_message(session_id, "assistant", response)
            return result

        knowledge = retrieve_knowledge(message)
        if knowledge:
            answer = knowledge[0]["answer"]
            if self.api_key:
                prompt = (
                    "You are a helpful customer support assistant. "
                    f"Use this inquiry: {message}\n"
                    f"Use this support knowledge: {knowledge[0]['answer']}\n"
                    "Give a concise but empathetic answer without inventing facts."
                )
                llm_answer = self._call_llm(prompt)
                if llm_answer:
                    answer = llm_answer
            response = answer
        else:
            response = (
                "I can help with order support, refunds, shipping, cancellations, and returns. "
                "Please share your order ID or the issue you are facing."
            )

        save_conversation_message(session_id, "assistant", response)
        return {
            "session_id": session_id,
            "response": response,
            "tool_used": None,
            "knowledge_used": knowledge,
            "escalated": False,
        }
