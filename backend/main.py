from fastapi import FastAPI, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from .invoice_processor import process_policy_and_invoices
from .chatbot import query_chatbot

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/analyze")
async def analyze(policy_file: UploadFile, invoice_zip: UploadFile, employee_name: str = Form(...)):
    return await process_policy_and_invoices(policy_file, invoice_zip, employee_name)

@app.post("/chat")
async def chat(query: str = Body(..., embed=True)):
    return query_chatbot(query)
