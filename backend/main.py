from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Ticket
from bot import get_bot_response, save_ticket

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates = Jinja2Templates(directory="../frontend")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

@app.post("/support")
async def send_message(customer_name: str = Form(...), message: str = Form(...), db: Session = next(get_db())):
    response = get_bot_response(message)
    save_ticket(customer_name, message, response)
    
    ticket = Ticket(customer_name=customer_name, message=message, response=response)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    return {"response": response}

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = next(get_db())):
    tickets = db.query(Ticket).all()
    return templates.TemplateResponse("admin.html", {"request": request, "tickets": tickets})
