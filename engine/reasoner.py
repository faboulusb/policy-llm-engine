from engine.query_parser import parse_query
from engine.retriever import retrieve_clauses
from engine.llm_local_runner import run_llm_reasoning  # swap with Gemini/OpenAI if needed

def reason_over_query(raw_query: str) -> dict:
    """
    Parses, retrieves, reasons, and returns a decision with justification.
    """
    # Step 1: Parse natural query
    parsed = parse_query(raw_query)

    # Step 2: Retrieve matched chunks from index
    matched_clauses = retrieve_clauses(parsed, top_k=5)

    if not matched_clauses:
        return {
            "decision": "unknown",
            "amount": None,
            "justification": "No relevant clauses found in the documents.",
            "matched_clauses": [],
            "parsed": parsed
        }

    # Step 3: Generate structured decision (LLM or Rule-Based)
    result = run_llm_reasoning(parsed, matched_clauses)

    return {
        "decision": result.get("decision", "unknown"),
        "amount": result.get("amount"),
        "justification": result.get("justification"),
        "matched_clauses": matched_clauses,
        "parsed": parsed
    }

# 🧪 Example usage
if __name__ == "__main__":
    query = "46M, knee surgery in Pune, 3-month policy"
    result = reason_over_query(query)
    from pprint import pprint
    pprint(result)
