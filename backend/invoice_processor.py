import fitz
import zipfile
from fuzzywuzzy import fuzz
import json
from io import BytesIO
from pathlib import Path
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from .vector_store import save_to_vectorstore
import os
from dotenv import load_dotenv
load_dotenv()

def extract_text_from_pdf(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return ""

def extract_zip(file_bytes, extract_to="data/processed"):
    extract_path = Path(extract_to)
    extract_path.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(BytesIO(file_bytes)) as zip_ref:
        zip_ref.extractall(extract_to)
    
    # Recursively find all PDF files (case-insensitive)
    pdf_files = []
    for ext in ("*.pdf", "*.PDF"):
        pdf_files.extend(extract_path.rglob(ext))
    
    print(f"Extracted {len(pdf_files)} PDF files:")
    for i, f in enumerate(pdf_files, 1):
        print(f"{i}. {f.relative_to(extract_path)}")
    
    return pdf_files

async def process_policy_and_invoices(policy_file, invoice_zip, employee_name):
    # Read policy PDF
    policy_text = extract_text_from_pdf(await policy_file.read())
    if not policy_text.strip():
        print("Policy PDF is empty or invalid")
    
    # Process invoice ZIP
    invoice_bytes = await invoice_zip.read()
    invoice_files = extract_zip(invoice_bytes)
    
    if not invoice_files:
        return {
            "status": "error",
            "message": "No PDF files found in ZIP archive"
        }

    llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    prompt_template = PromptTemplate.from_file(
        "prompts/invoice_prompt.txt", 
        input_variables=["policy_text", "invoice_text"]
    )

    documents = []
    json_data = []  # For JSON output
    for invoice_file in invoice_files:
        # Skip directories (rare but possible)
        if not invoice_file.is_file():
            continue
            
        try:
            invoice_bytes = invoice_file.read_bytes()
            invoice_text = extract_text_from_pdf(invoice_bytes)
            
            if not invoice_text.strip():
                print(f"Skipped empty/corrupted invoice: {invoice_file.name}")
                continue
                
            # Process with LLM
            # print(f"this is policy text {policy_text}")
            prompt = prompt_template.format(
                policy_text=policy_text, 
                invoice_text=invoice_text
            )
            response = llm.invoke(prompt)
            
            # Parse response (add error handling)
            extracted_name = ""
            status = "Unknown"
            reason = "Response parsing failed"
            match_status = "Not Found"
            similarity = 0
            try:
                if "Employee Name:" in response:
                    extracted_name = response.split("Employee Name:")[1].split("\n")[0].strip()
                if "Reimbursement Status:" in response:
                    status = response.split("Reimbursement Status:")[1].split("\n")[0].strip()
                if "Reason:" in response:
                    reason = response.split("Reason:")[1].strip()
                if not extracted_name:
                    reason = "Employee name not found in invoice"
                else:
                    similarity = fuzz.ratio(employee_name.lower(), extracted_name.lower())
                    if similarity < 75:
                        match_status = "Mismatch"
                    else:
                        match_status = "Match"
            except Exception as e:
                print(f"Error parsing LLM response: {str(e)}")

            invoice_metadata = {
                    "employee_name": extracted_name,
                    "name_match_status": match_status,
                    "name_similarity": similarity,
                    "invoice_name": invoice_file.name,
                    "status": status,
                    "reason": reason
            }

            page_content = (
                f"Employee Name (Provided): {employee_name}\n"
                f"Employee Name (Extracted): {extracted_name}\n"
                f"Match Status: {match_status}\n"
                f"Status: {status}\n"
                f"Reason: {reason}\n\n"
                f"--- INVOICE CONTENT ---\n"
                f"{invoice_text}"
            )
            # Create document
            doc = Document(
                page_content=page_content,
                metadata=invoice_metadata
            )
            documents.append(doc)
            json_data.append({
            "content": invoice_text,  # Include text if needed
            "metadata": invoice_metadata
                })
            print(f"Processed: {invoice_file.name} → Status: {status}")
            with open("output.json", "w") as json_file:
                json.dump(json_data, json_file, indent=2)
            
        except Exception as e:
            print(f"Failed to process {invoice_file.name}: {str(e)}")
    
    # Handle empty documents
    if not documents:
        return {
            "status": "error",
            "message": "All invoices were empty or could not be processed"
        }
    matched_invoices = [
        {
            "employee_name": doc.metadata["employee_name"],
            "status": doc.metadata["status"],
            "reason": doc.metadata["reason"],
            "invoice_name": doc.metadata["invoice_name"]
        }
        for doc in documents if doc.metadata["name_match_status"] == "Match"
    ]
    save_to_vectorstore(documents)
    return {
        "status": "success",
        "matched_invoices": matched_invoices
    }