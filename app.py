import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
with open("schemes.json", encoding="utf-8") as f:
    DATA = json.load(f)
SCHEMES, DOCS = DATA["schemes"], DATA["docs"]

BRACKETS = {"u2": (0, 2), "2-5": (2, 5), "5-8": (5, 8), "8+": (8, 999)}  # lakhs per year
LABELS = {"student": "a student", "woman": "a woman entrepreneur/homemaker", "senior": "a senior citizen",
          "farmer": "a farmer", "daily_wage": "a daily wage worker"}


def match(u):
    lo, hi = BRACKETS[u["income"]]
    results = []
    for s in SCHEMES:
        generic = "any" in s["categories"]
        if not generic and u["category"] not in s["categories"]:
            continue
        if s["states"] != ["all"] and u["state"] not in s["states"]:
            continue
        if lo >= s["max_income"]:                       # income too high
            continue
        if s.get("status") and u["status"] not in s["status"]:
            continue
        if s.get("level") and u.get("level") not in s["level"]:
            continue
        if s.get("caste") and u.get("caste") not in s["caste"]:
            continue
        score, why = 70, []
        if not generic:
            score += 10
            why.append(f"You are {LABELS[u['category']]}")
        if hi <= s["max_income"]:
            score += 10
            why.append("your income is within the limit")
        elif s["max_income"] < 999:
            why.append("your income may be within the limit")
        if s["states"] != ["all"]:
            score += 5
            why.append(f"you live in {u['state']}")
        if s.get("status"):
            score += 3
        if s.get("caste"):
            score += 5
            why.append(f"you belong to the {u['caste']} category")
        results.append({**s, "match": min(score, 98),
                        "why": (", ".join(why) or "Open to everyone") + "."})
    return sorted(results, key=lambda x: -x["match"])


@app.route("/")
def index():
    return render_template("index.html", count=len(SCHEMES))


@app.route("/api/match", methods=["POST"])
def api_match():
    u = request.get_json(force=True)
    if u.get("income") not in BRACKETS or not u.get("category"):
        return jsonify(error="Please answer all questions."), 400
    return jsonify(schemes=match(u), docs=DOCS)


if __name__ == "__main__":
    app.run(debug=True)
