import streamlit as st
import requests
from io import BytesIO

st.set_page_config(page_title="Invoice Reimbursement System", layout="centered")
st.title("🧾 Invoice Reimbursement System")

st.subheader("📤 Upload Invoices for Analysis")
policy = st.file_uploader("Upload HR Policy File (.pdf or .docx)", type=["pdf", "docx"])
invoice_zip = st.file_uploader("Upload Invoices ZIP", type=["zip"])
employee_name = st.text_input("Employee Name")

if st.button("Analyze Invoices"):
    if not (policy and invoice_zip and employee_name):
        st.error("Please provide all inputs.")
    else:
        mime_type = "application/pdf" if policy.name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        files = {
            "policy_file": (policy.name, BytesIO(policy.read()), mime_type),
            "invoice_zip": (invoice_zip.name, BytesIO(invoice_zip.read()), "application/zip"),
        }
        data = {"employee_name": employee_name}
        try:
            res = requests.post("http://localhost:8000/analyze", files=files, data=data)
            if res.ok:
                st.success("✅ Analysis Complete")
                result = res.json()

                if result["status"] == "success" and result.get("matched_invoices"):
                    st.markdown("### 🧾 Matched Invoice Results")
                    for idx, invoice in enumerate(result["matched_invoices"], 1):
                        st.markdown(f"#### 📄 Invoice {idx}: {invoice['invoice_name']}")
                        st.markdown(f"- **Employee Name:** {invoice['employee_name']}")
                        st.markdown(f"- **Status:** {invoice['status']}")
                        st.markdown(f"- **Reason:** {invoice['reason']}")
                        st.markdown("---")
                else:
                    st.warning("No matched invoices found.")
            else:
                st.error("❌ Something went wrong.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.subheader("💬 Query Reimbursement Bot")
query = st.text_input("Ask a question about invoices (e.g., Show all declined invoices)")

if st.button("Ask Bot"):
    if not query:
        st.warning("Enter a question before submitting.")
    else:
        try:
            res = requests.post("http://localhost:8000/chat", json={"query": query})
            if res.ok:
                st.markdown(res.json()["response"])
            else:
                st.error("❌ Failed to get response from bot.")
        except Exception as e:
            st.error(f"❌ Error: {e}")
