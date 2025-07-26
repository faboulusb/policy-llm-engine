from flask import Flask, render_template, request, jsonify
from engine.query_parser import parse_query
from engine.retriever import retrieve_clauses
from engine.reasoner import decide
from engine.formatter import format_response
from engine.session_manager import get_session_context, update_session
from engine.db import log_user_query
import requests

# Optional: Load in-memory plan data if needed for UI fallback
from utils.load_data import load_plan_data
plan_df, rate_df, benefits_df = load_plan_data()

app = Flask(__name__)

# External alternate policy API URL
ALT_API_URL = "https://bajaj-alianz-health-insurance-lznkjuhdddi3v9weyxgshc.streamlit.app/api/alternatives"

def fetch_alternates_from_external(parsed):
    try:
        payload = {
            "age": parsed.get("age"),
            "state": parsed.get("location"),
            "coverage": parsed.get("coverage", 30000),
            "plan_type": parsed.get("plan_type", "Any")
        }
        res = requests.post(ALT_API_URL, json=payload, timeout=10)
        if res.status_code == 200:
            return res.json().get("plans", [])
        else:
            print(f"⚠️ Failed to fetch alternates from external recommender. Status: {res.status_code}")
            return []
    except Exception as e:
        print("❌ Error fetching external alternatives:", e)
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_query = request.form.get("query", "")
        session_id = request.remote_addr

        parsed = parse_query(user_query)
        matched_clauses = retrieve_clauses(parsed)
        decision = decide(parsed, matched_clauses)
        response_json = format_response(user_query, parsed, matched_clauses, decision)
        log_user_query(session_id, user_query, response_json)
        update_session(session_id, user_query, response_json)

        alt_suggestions = []
        if decision.get("decision", "").lower() == "rejected":
            alt_suggestions = fetch_alternates_from_external(parsed)

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
        alt_suggestions = fetch_alternates_from_external(parsed)

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
