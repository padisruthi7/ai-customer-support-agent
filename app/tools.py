import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.database import Order, Refund, SupportTicket, SessionLocal


def _normalize_order_id(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    match = re.search(r"ORD\d+", value.upper())
    return match.group(0) if match else None


def get_order_status(order_id: str) -> Dict[str, object]:
    normalized = _normalize_order_id(order_id)
    if not normalized:
        return {"found": False, "message": "Please provide a valid order ID such as ORD1001."}

    with SessionLocal() as session:
        order = session.query(Order).filter(Order.order_id == normalized).first()
        if not order:
            return {"found": False, "order_id": normalized, "message": f"Order ID {normalized} was not found."}

        return {
            "found": True,
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "status": order.status,
            "shipping_eta": order.shipping_eta,
            "item": order.item,
            "message": f"Your order {order.order_id} is currently {order.status}. Expected delivery: {order.shipping_eta}.",
        }


def get_customer_order_history(customer_id: str) -> List[Dict[str, object]]:
    if not customer_id:
        return []

    with SessionLocal() as session:
        orders = session.query(Order).filter(Order.customer_id == customer_id).all()
        return [
            {
                "order_id": order.order_id,
                "item": order.item,
                "status": order.status,
                "total": order.total,
                "shipping_eta": order.shipping_eta,
            }
            for order in orders
        ]


def check_refund_status(order_id: str) -> Dict[str, object]:
    normalized = _normalize_order_id(order_id)
    if not normalized:
        return {"found": False, "message": "Please provide a valid order ID to check the refund status."}

    with SessionLocal() as session:
        refund = session.query(Refund).filter(Refund.order_id == normalized).first()
        if not refund:
            return {"found": False, "message": f"I could not find a refund record for {normalized}."}

        return {
            "found": True,
            "order_id": refund.order_id,
            "status": refund.status,
            "amount": refund.amount,
            "reason": refund.reason,
            "message": f"Refund for {refund.order_id} is {refund.status}. Amount: {refund.amount}.",
        }


def cancel_order(order_id: str) -> Dict[str, object]:
    normalized = _normalize_order_id(order_id)
    if not normalized:
        return {"success": False, "message": "Please provide a valid order ID to cancel."}

    with SessionLocal() as session:
        order = session.query(Order).filter(Order.order_id == normalized).first()
        if not order:
            return {"success": False, "message": f"Order {normalized} was not found."}
        if order.status in {"cancelled", "delivered"}:
            return {"success": False, "message": f"Order {normalized} cannot be cancelled because it is already {order.status}.", "status": order.status}

        order.status = "cancelled"
        session.commit()

        return {
            "success": True,
            "order_id": order.order_id,
            "status": "cancelled",
            "message": f"Order {order.order_id} has been cancelled successfully.",
        }


def create_support_ticket(customer_id: str, order_id: str, issue: str, priority: str = "normal") -> Dict[str, object]:
    if not customer_id:
        return {"success": False, "message": "Customer ID is required."}

    ticket_id = f"TKT{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    with SessionLocal() as session:
        ticket = SupportTicket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            order_id=order_id,
            subject=f"{priority.title()} support request",
            summary=issue,
            status="open",
        )
        session.add(ticket)
        session.commit()

        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": "open",
            "message": f"A human support ticket has been created: {ticket_id}.",
        }


def escalate_to_human(customer_id: str, order_id: Optional[str], reason: str) -> Dict[str, object]:
    issue = reason or "Customer requested human assistance."
    ticket = create_support_ticket(customer_id, order_id or "", issue, priority="high")
    if not ticket["success"]:
        return ticket

    return {
        "success": True,
        "ticket_id": ticket["ticket_id"],
        "status": "escalated",
        "message": f"Your issue has been escalated to a human agent. Ticket number: {ticket['ticket_id']}.",
    }
