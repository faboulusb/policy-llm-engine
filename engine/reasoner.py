from engine.query_parser import parse_query
from engine.retriever import retrieve_clauses
from engine.llm_local_runner import LocalLLM

llm = LocalLLM()

def build_prompt(parsed: dict, matched_clauses: list) -> str:
    """
    Construct a prompt for the local LLM based on parsed user input and matched policy clauses.
    """
    user_info = (
        f"Age: {parsed.get('age', 'unknown')}, "
        f"Procedure: {parsed.get('procedure', 'unknown')}, "
        f"Location: {parsed.get('location', 'unknown')}, "
        f"Policy Age: {parsed.get('policy_age', 'unknown')} months."
    )

    clause_summary = "\n".join([f"- {c['text']}" for c in matched_clauses])

    prompt = (
        f"A user has the following details:\n"
        f"{user_info}\n\n"
        f"The following clauses were retrieved from the insurance policy documents:\n"
        f"{clause_summary}\n\n"
        f"Based on the clauses, answer:\n"
        f"1. Is the procedure covered? (approved/rejected)\n"
        f"2. What is the payout amount if applicable?\n"
        f"3. Justify the decision by referring to clause(s).\n"
        f"Respond in JSON format with keys: decision, amount, justification."
    )

    return prompt

def run_llm_reasoning(parsed: dict, matched_clauses: list) -> dict:
    """
    Generate a decision using the local LLM.
    """
    prompt = build_prompt(parsed, matched_clauses)
    raw_output = llm.generate(prompt)

    # Fallback parser if LLM returns non-strict JSON
    try:
        import json
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1
        json_block = raw_output[start:end]
        return json.loads(json_block)
    except Exception as e:
        return {
            "decision": "unknown",
            "amount": None,
            "justification": f"Failed to parse LLM response: {e}\nRaw Output: {raw_output}"
        }

def reason_over_query(raw_query: str) -> dict:
    """
    Full pipeline: Parse → Retrieve → Reason → Return Decision
    """
    parsed = parse_query(raw_query)
    matched_clauses = retrieve_clauses(parsed, top_k=5)

    if not matched_clauses:
        return {
            "decision": "unknown",
            "amount": None,
            "justification": "No relevant clauses found.",
            "matched_clauses": [],
            "parsed": parsed
        }

    result = run_llm_reasoning(parsed, matched_clauses)

    return {
        "decision": result.get("decision", "unknown"),
        "amount": result.get("amount"),
        "justification": result.get("justification"),
        "matched_clauses": matched_clauses,
        "parsed": parsed
    }

# 🧪 CLI Test
if __name__ == "__main__":
    query = "46M, knee surgery in Pune, 3-month policy"
    result = reason_over_query(query)
    from pprint import pprint
    pprint(result)

