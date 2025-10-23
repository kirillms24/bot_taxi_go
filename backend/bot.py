import json
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Для простоты используем предобученную модель
tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")

def get_bot_response(message: str):
    inputs = tokenizer([message], return_tensors="pt")
    reply_ids = model.generate(**inputs)
    response = tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
    return response

def save_ticket(customer_name, message, response):
    # Сохраняем запрос в JSON (или в БД)
    with open("tickets_history.json", "a", encoding="utf-8") as f:
        json.dump({"customer_name": customer_name, "message": message, "response": response}, f, ensure_ascii=False)
        f.write("\n")
