from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Ticket
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# --- Database ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./taxi_support.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Bot setup ---
tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")

def get_bot_response(message: str):
    inputs = tokenizer([message], return_tensors="pt")
    reply_ids = model.generate(**inputs)
    response = tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
    return response

def save_ticket_history(customer_name, message, response):
    with open("tickets_history.json", "a", encoding="utf-8") as f:
        json.dump({"customer_name": customer_name, "message": message, "response": response}, f, ensure_ascii=False)
        f.write("\n")

# --- FastAPI app ---
app = FastAPI()

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Такси Поддержка</title>
        <style>
            body { font-family: Arial; margin:20px; background:#f4f4f4; }
            header nav a { margin-right:15px; text-decoration:none; color:#333; font-weight:bold; }
            header { margin-bottom:20px; }
            h1,h2 { color:#222; }
        </style>
    </head>
    <body>
        <header>
            <h1>Такси Поддержка</h1>
            <nav>
                <a href="/support">Чат с ботом</a>
                <a href="/admin">Админка</a>
            </nav>
        </header>
        <main>
            <h2>Добро пожаловать в службу поддержки Такси</h2>
            <p>Используйте чат для связи с ботом или откройте админку для сотрудников.</p>
        </main>
    </body>
    </html>
    """

@app.get("/support", response_class=HTMLResponse)
async def support_page():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Чат с ботом</title>
        <style>
            body { font-family: Arial; margin:20px; background:#f4f4f4; }
            input, button { padding:8px; margin:5px 0; }
            #chat-box p { background:#fff; padding:5px; border-radius:4px; margin:5px 0; }
            #chat-box { max-height:400px; overflow-y:auto; border:1px solid #ccc; padding:10px; background:#eaeaea; }
        </style>
    </head>
    <body>
        <h2>Чат с ботом поддержки</h2>
        <form id="chat-form">
            <input type="text" id="name" placeholder="Ваше имя" required>
            <input type="text" id="message" placeholder="Введите сообщение" required>
            <button type="submit">Отправить</button>
        </form>
        <div id="chat-box"></div>
        <script>
            document.getElementById("chat-form").addEventListener("submit", async (e) => {
                e.preventDefault();
                const name = document.getElementById("name").value;
                const message = document.getElementById("message").value;
                const response = await fetch("/support", {
                    method: "POST",
                    body: new URLSearchParams({ customer_name:name, message:message })
                });
                const data = await response.json();
                const chatBox = document.getElementById("chat-box");
                chatBox.innerHTML += `<p><b>Вы:</b> ${message}</p><p><b>Бот:</b> ${data.response}</p>`;
                document.getElementById("message").value="";
                chatBox.scrollTop = chatBox.scrollHeight;
            });
        </script>
    </body>
    </html>
    """

@app.post("/support")
async def send_message(customer_name: str = Form(...), message: str = Form(...), db: Session = next(get_db())):
    response = get_bot_response(message)
    save_ticket_history(customer_name, message, response)
    ticket = Ticket(customer_name=customer_name, message=message, response=response)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {"response": response}

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(db: Session = next(get_db())):
    tickets = db.query(Ticket).all()
    rows = ""
    for t in tickets:
        rows += f"<tr><td>{t.id}</td><td>{t.customer_name}</td><td>{t.message}</td><td>{t.response}</td><td>{t.status}</td><td>{t.created_at}</td></tr>"
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Админка</title>
        <style>
            body{{font-family:Arial;margin:20px;background:#f4f4f4;}}
            table, th, td{{border:1px solid black;border-collapse:collapse;padding:5px;}}
            th{{background:#ddd;}}
            td{{max-width:300px; word-wrap:break-word;}}
        </style>
    </head>
    <body>
        <h2>Админка поддержки</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Имя клиента</th>
                <th>Сообщение</th>
                <th>Ответ</th>
                <th>Статус</th>
                <th>Дата</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """
