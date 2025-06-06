from langchain_openai import ChatOpenAI  # Changed to ChatOpenAI for gpt-3.5-turbo
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from .vector_store import load_vectorstore
import os
from dotenv import load_dotenv

load_dotenv()

def query_chatbot(query):
    # Load vector store
    vectorstore = load_vectorstore()
    if not vectorstore:
        return {"response": "Vector store not found. Please upload invoices first."}

    # Load custom prompt template
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "chatbot_prompt.txt")
    
    try:
        with open(prompt_path, "r") as f:
            template = f.read().strip()  # Read prompt template
    except FileNotFoundError:
        template = """You are an Invoice Analysis Specialist. Your task is to perform detailed analysis of invoices using the retrieved context.
                Follow these guidelines:
                1. Conduct comprehensive analysis of invoice details
                2. Extract and interpret numerical data (amounts, quantities, taxes)
                3. Identify key entities (vendor names, dates, payment terms)
                4. Compare and correlate information across multiple invoices when relevant
                5. If no results match the query, respond with "No relevant invoices found"

                Context: {context}

                Question: {question}

                Detailed Analysis:"""

    # Create PromptTemplate with required variables
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    # Initialize ChatOpenAI (gpt-3.5-turbo)
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Configure RetrievalQA with custom prompt
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )

    result = qa.run(query)
    return {"response": result}