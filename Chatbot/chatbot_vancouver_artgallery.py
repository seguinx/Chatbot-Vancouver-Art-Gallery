import csv
import difflib
from pathlib import Path

faq = []

base_path = Path(__file__).parent
csv_path = base_path / "question_Vancouver.csv"
log_path = base_path / "unanswered_questions.txt"

with open(csv_path, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        faq.append(row)

print("Hello! I am the Vancouver Art Gallery FAQ chatbot.")
print("Ask me a question about membership or visiting the gallery.")
print("Type 'quit' to stop.")

while True:
    user_question = input("You: ").lower().strip()

    if user_question == "quit":
        print("Bot: Goodbye!")
        break

    best_row = None
    best_score = 0

    for row in faq:
        model_question = row["question_model"]
        score = difflib.SequenceMatcher(None, user_question, model_question).ratio()

        if score > best_score:
            best_score = score
            best_row = row

    if best_row and best_score >= 0.60:
        print("Bot:", best_row["short_answer"])
        print("Source:", best_row["source_link"])
        print("Match score:", round(best_score, 2))
    else:
        print("Bot: Sorry, I am not sure about that yet. Try asking in a different way.")
        print("Bot: I am not confident on this one. Here are a few similar questions you can try.")

        all_questions = [row["question_model"] for row in faq]
        suggestions = difflib.get_close_matches(user_question, all_questions, n=3, cutoff=0.3)

        if suggestions:
            for suggestion in suggestions:
                print("-", suggestion)
        else:
            print("- Please check the official website: https://www.vanartgallery.bc.ca/")

        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(user_question + "\n")