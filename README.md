# 🧾 Invoice Reimbursement System

Automate and analyze invoice reimbursements against HR policy with GPT-3.5, FAISS, LangChain, FastAPI, and Streamlit.

## 🚀 Setup

```bash
git clone https://github.com/krishnavamshithumma/invoice-reimbursement-system.git
pip install -r requirements.txt
uvicorn backend.main:app --reload
streamlit run frontend/app.py
```
## env set up
1. Add a .env file and add your OPENAI_API_KEY there
## 📤 Analyze Invoices

1. Upload policy PDF and invoice ZIP.
2. Assign employee name.
3. See analysis stored in FAISS.

## 💬 Chatbot Usage

Ask:
- "Show all declined invoices by Ramesh"
- "Which invoices were partially reimbursed ?"

## 🧱 Stack

- LangChain + GPT-3.5
- FAISS (Vector Store)
- FastAPI (API)
- Streamlit (UI)

## Visualisation

![Architecture diagram](images/Screenshot%20from%202025-06-06%2012-01-44.png)
