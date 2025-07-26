from flask import Flask, render_template, request, jsonify
from engine.query_parser import parse_query
from engine.retriever import retrieve_clauses
from engine.reasoner import decide
from engine.formatter import format_response
from engine.session_manager import get_session_context, update_session
from engine.db import log_query_and_response
from engine.alternate_policy_recommender import suggest_alternatives

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_query = request.form.get("query", "")
        session_id = request.remote_addr  # basic fallback; replace with real session/token

        # Step 1: Parse query
        parsed = parse_query(user_query)

        # Step 2: Retrieve relevant clauses from SQL or FAISS
        clauses = retrieve_clauses(parsed)

        # Step 3: Apply LLM / logic to reason on clauses
        decision = decide(parsed, clauses)

        # Step 4: Generate formatted structured JSON
        response_json = format_response(user_query, parsed, clauses, decision)

        # Step 5: Log into PostgreSQL for audit
        log_query_and_response(session_id, user_query, parsed, clauses, decision)

        # Step 6: Update session cache
        update_session(session_id, user_query, response_json)

        # Step 7: Get context-aware suggestions
        suggestions = suggest_alternatives(parsed, decision)

        return render_template("index.html", response=response_json, suggestions=suggestions)

    return render_template("index.html")

@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.json
    user_query = data.get("query", "")
    session_id = request.remote_addr

    parsed = parse_query(user_query)
    clauses = retrieve_clauses(parsed)
    decision = decide(parsed, clauses)
    response_json = format_response(user_query, parsed, clauses, decision)
    log_query_and_response(session_id, user_query, parsed, clauses, decision)
    update_session(session_id, user_query, response_json)
    suggestions = suggest_alternatives(parsed, decision)

    return jsonify({
        "response": response_json,
        "suggestions": suggestions
    })

@app.route("/api/context", methods=["GET"])
def get_context():
    session_id = request.remote_addr
    return jsonify(get_session_context(session_id))

if __name__ == "__main__":
    app.run(debug=True)
