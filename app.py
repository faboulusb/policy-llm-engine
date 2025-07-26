from flask import Flask, render_template, request, jsonify
from engine.query_parser import parse_query
from engine.retriever import retrieve_relevant_clauses
from engine.reasoner import evaluate_decision
from engine.formatter import format_response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        user_input = request.form.get("query", "")

        # 1. Parse Query
        parsed = parse_query(user_input)

        # 2. Retrieve Relevant Clauses
        chunks = retrieve_relevant_clauses(parsed)

        # 3. Evaluate Logic
        decision = evaluate_decision(parsed, chunks)

        # 4. Format Result
        result = format_response(decision)

    return render_template("index.html", result=result)

@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.json
    parsed = parse_query(data.get("query", ""))
    chunks = retrieve_relevant_clauses(parsed)
    decision = evaluate_decision(parsed, chunks)
    result = format_response(decision)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
