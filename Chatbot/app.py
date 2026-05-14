from flask import Flask, render_template, request, jsonify
import csv
import difflib
from pathlib import Path

app = Flask(__name__)

faq = []
base_path = Path(__file__).parent
csv_path = base_path / "question_Vancouver.csv"

with open(csv_path, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        faq.append(row)


def get_bot_response(user_question):
    user_question = user_question.lower().strip()

    best_row = None
    best_score = 0

    for row in faq:
        model_question = row["question_model"]
        score = difflib.SequenceMatcher(None, user_question, model_question).ratio()

        if score > best_score:
            best_score = score
            best_row = row

    if best_row and best_score >= 0.60:
        return {
            "answer": best_row["short_answer"],
            "source": best_row["source_link"],
            "score": round(best_score, 2),
            "suggestions": []
        }
    else:
        all_questions = [row["question_model"] for row in faq]
        suggestions = difflib.get_close_matches(user_question, all_questions, n=3, cutoff=0.3)

        return {
            "answer": "Sorry, I am not sure about that yet. Try asking in a different way.",
            "source": "https://www.vanartgallery.bc.ca/",
            "score": round(best_score, 2),
            "suggestions": suggestions
        }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({
                "answer": "Hmm I did not receive anything on my side",
                "source": "https://www.vanartgallery.bc.ca/",
                "score": 0,
                "suggestions": []
            }), 400

        user_message = data["message"]
        response = get_bot_response(user_message)
        return jsonify(response)

    except Exception as e:
        print("ERROR IN /chat:", e)
        return jsonify({
            "answer": f"Server error: {str(e)}",
            "source": "https://www.vanartgallery.bc.ca/",
            "score": 0,
            "suggestions": []
        }), 500


if __name__ == "__main__":
    app.run(debug=True, load_dotenv=False)