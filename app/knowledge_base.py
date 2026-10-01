from typing import List

KNOWLEDGE_BASE = [
    {
        "title": "Shipping Policy",
        "category": "shipping",
        "keywords": ["shipping", "delivery", "late", "arrive", "track", "shipment", "order"],
        "answer": "Standard shipping usually takes 3-5 business days. Express shipping takes 1-2 business days. If an order is delayed, we recommend checking the tracking link or contacting support with the order ID.",
    },
    {
        "title": "Return Policy",
        "category": "returns",
        "keywords": ["return", "refund", "exchange", "damaged", "broken", "wrong item"],
        "answer": "Most items can be returned within 30 days of delivery if they are unused and in original packaging. Damaged or incorrect items can be returned faster and may qualify for a refund or replacement.",
    },
    {
        "title": "Refund Policy",
        "category": "refund",
        "keywords": ["refund", "money back", "reimbursement", "paid but not placed"],
        "answer": "Refunds are processed after review and usually appear within 5-7 business days to the original payment method. Duplicate payments or payment failures are reviewed manually.",
    },
    {
        "title": "Cancellation Policy",
        "category": "cancellation",
        "keywords": ["cancel", "cancellation", "cancelled", "stop order"],
        "answer": "Orders can be cancelled before they are shipped. Once dispatched, the order may no longer be cancelable and may need to be returned instead.",
    },
    {
        "title": "Payment Policy",
        "category": "payments",
        "keywords": ["payment", "charged", "billing", "deducted", "card"],
        "answer": "A payment may appear as pending or processing before the order is confirmed. If you were charged but the order was not created, we can review the transaction and open a support case.",
    },
    {
        "title": "Warranty Information",
        "category": "warranty",
        "keywords": ["warranty", "defect", "repair", "replacement", "guarantee"],
        "answer": "Eligible products come with a 12-month limited warranty against manufacturing defects. Please share the order ID and issue details to check warranty eligibility.",
    },
]


def retrieve_knowledge(query: str) -> List[dict]:
    if not query:
        return []

    text = query.lower()
    scored = []
    for item in KNOWLEDGE_BASE:
        keywords = [item["title"].lower()] + item["keywords"]
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        if score > 0:
            scored.append({
                "title": item["title"],
                "category": item["category"],
                "answer": item["answer"],
                "score": score,
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:3]
