from flask import Flask, render_template, request, jsonify
from engine.query_parser import parse_query
from engine.retriever import retrieve_clauses
from engine.reasoner import decide
from engine.formatter import format_response
from engine.session_manager import get_session_context, update_session
from engine.db import log_user_query
from engine.alternate_policy_recommender import recommend_alternatives

# --- Optionally: Load data files if needed
from utils.load_data import load_plan_data  # You can implement this wrapper
plan_df, rate_df, benefits_df = load_plan_data()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_query = request.form.get("query", "")
        session_id = request.remote_addr  # fallback identifier

        # Step 1: Parse
        parsed = parse_query(user_query)

        # Step 2: Retrieve matching clauses
        matched_clauses = retrieve_clauses(parsed)

        # Step 3: Reasoning with rules / LLM
        decision = decide(parsed, matched_clauses)

        # Step 4: Format structured response
        response_json = format_response(user_query, parsed, matched_clauses, decision)

        # Step 5: Log to DB
        log_user_query(session_id, user_query, response_json)

        # Step 6: Update session context
        update_session(session_id, user_query, response_json)

        # Step 7: Suggest alternates if rejected
        alt_suggestions = []
        if decision.get("decision", "").lower() == "rejected":
            alt_suggestions = recommend_alternatives(
                user_age=parsed.get("age"),
                user_state=parsed.get("location"),
                plan_df=plan_df,
                rate_df=rate_df,
                benefits_df=benefits_df,
                base_coverage=parsed.get("coverage", 30000),
                original_plan_type=parsed.get("plan_type", None)
            )

        return render_template("index.html", response=response_json, suggestions=alt_suggestions)

    return render_template("index.html")

@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.json
    user_query = data.get("query", "")
    session_id = request.remote_addr

    parsed = parse_query(user_query)
    matched_clauses = retrieve_clauses(parsed)
    decision = decide(parsed, matched_clauses)
    response_json = format_response(user_query, parsed, matched_clauses, decision)
    log_user_query(session_id, user_query, response_json)
    update_session(session_id, user_query, response_json)

    alt_suggestions = []
    if decision.get("decision", "").lower() == "rejected":
        alt_suggestions = recommend_alternatives(
            user_age=parsed.get("age"),
            user_state=parsed.get("location"),
            plan_df=plan_df,
            rate_df=rate_df,
            benefits_df=benefits_df,
            base_coverage=parsed.get("coverage", 30000),
            original_plan_type=parsed.get("plan_type", None)
        )

    return jsonify({
        "response": response_json,
        "suggestions": alt_suggestions
    })

@app.route("/api/context", methods=["GET"])
def api_context():
    session_id = request.remote_addr
    return jsonify(get_session_context(session_id))

if __name__ == "__main__":
    app.run(debug=True)
