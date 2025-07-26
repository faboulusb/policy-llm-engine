import json
from typing import Dict, Any

def format_decision_response(reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the reasoning result into a structured response for UI or API.
    """
    return {
        "query_details": reasoning_result.get("parsed", {}),
        "decision": reasoning_result.get("decision", "unknown"),
        "payout_amount": reasoning_result.get("amount"),
        "justification": reasoning_result.get("justification", "No explanation provided."),
        "matched_clauses": [
            {
                "source": clause["source"],
                "doc_type": clause.get("doc_type", "unknown"),
                "text_snippet": clause["text"][:300] + "..." if len(clause["text"]) > 300 else clause["text"]
            }
            for clause in reasoning_result.get("matched_clauses", [])
        ]
    }

def format_pretty_print(response_dict: Dict[str, Any]) -> str:
    """
    Returns a readable, indented JSON string version of the response (for logs/UI).
    """
    return json.dumps(response_dict, indent=2, ensure_ascii=False)

# 🧪 Example usage
if __name__ == "__main__":
    from reasoner import reason_over_query

    raw_query = "46M, knee surgery in Pune, 3-month policy"
    raw_result = reason_over_query(raw_query)

    formatted = format_decision_response(raw_result)
    print("✅ Final Output:\n")
    print(format_pretty_print(formatted))
