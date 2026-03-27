from typing import Dict, Any
import json
from pathlib import Path
from langchain.tools import tool
from langchain_community.vectorstores import FAISS
from rag import embed_instance
from model import llm


# ============================================================
# PATHS
# ============================================================

VECTOR_STORES_DIR = Path("vectorstores")

# Reference KBs
CGHS_KB_PATH = str(VECTOR_STORES_DIR / "cghs_rates")
NPPA_KB_PATH = str(VECTOR_STORES_DIR / "nppa_prices")

# Embeddings
embeddings = embed_instance.get_embeddings()


# ============================================================
# TOOL 1: Extract Bill Items
# ============================================================

@tool
def extract_bill_items(kb_name: str) -> str:
    """
    Extracts structured billing items from hospital bill KB.

    Args:
        kb_name: Name of the bill vectorstore.

    Returns:
        JSON containing:
        - procedures
        - medicines
        - room_charges
        - icu_charges
        - investigations
    """

    try:

        kb_path = str(VECTOR_STORES_DIR / kb_name)

        if not Path(kb_path).exists():
            return json.dumps({"error": f"Bill KB not found: {kb_path}"})

        bill_kb = FAISS.load_local(
            kb_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

        retriever = bill_kb.as_retriever(search_kwargs={"k": 5})

        query = """
Extract all billable items from this hospital bill.

Return structured JSON with:

procedures
investigations
medicines
room_charges
icu_charges

Each item must include:
name
quantity
charged_price
"""

        docs = retriever.invoke(query)

        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""
You are a medical billing auditor.

Extract billing items from the bill.

Context:
{context}

Return STRICT JSON format:

{{
"procedures": [],
"investigations": [],
"medicines": [],
"room_charges": {{}},
"icu_charges": {{}}
}}
"""

        response = llm.invoke(prompt)

        return response.content.strip()

    except Exception as e:
        return json.dumps({"error": str(e)})


# ============================================================
# TOOL 2: Validate Procedures & Investigations (CGHS)
# ============================================================

@tool
def validate_procedure_charges(
    procedures: str,
    investigations: str,
    room_charges: str,
    icu_charges: str
) -> str:
    """
    Validates hospital procedures and investigations against CGHS rate list.
    """

    try:

        if not Path(CGHS_KB_PATH).exists():
            return "ERROR: CGHS KB not found"

        cghs_kb = FAISS.load_local(
            CGHS_KB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

        retriever = cghs_kb.as_retriever(search_kwargs={"k": 5})

        query = f"""
Validate hospital charges against CGHS reference rates.

Procedures:
{procedures}

Investigations:
{investigations}

Room Charges:
{room_charges}

ICU Charges:
{icu_charges}
"""

        docs = retriever.invoke(query)

        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""
You are a hospital billing auditor.

Compare hospital charges against CGHS reference rates.

Context:
{context}

Hospital Charges:
{query}

Return JSON:

[
{{
"item": "",
"charged_price": "",
"allowed_price": "",
"status": "VALID / OVERPRICED / UNDERPRICED",
"excess_amount": ""
}}
]
"""

        response = llm.invoke(prompt)

        return response.content.strip()

    except Exception as e:
        return f"ERROR: {str(e)}"


# ============================================================
# TOOL 3: Validate Medicine Prices (NPPA)
# ============================================================

@tool
def validate_medicine_prices(medicines: str) -> str:
    """
    Validates medicine prices against NPPA ceiling prices.
    """

    try:

        if not Path(NPPA_KB_PATH).exists():
            return "ERROR: NPPA KB not found"

        nppa_kb = FAISS.load_local(
            NPPA_KB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

        retriever = nppa_kb.as_retriever(search_kwargs={"k": 5})

        query = f"""
Validate these medicines against NPPA ceiling prices.

Medicines:
{medicines}
"""

        docs = retriever.invoke(query)

        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""
You are a pharmaceutical pricing auditor.

Use ONLY NPPA ceiling prices.

Context:
{context}

Medicines:
{medicines}

Return JSON:

[
{{
"medicine": "",
"charged_price": "",
"allowed_price": "",
"status": "VALID / OVERPRICED",
"excess_amount": ""
}}
]
"""

        response = llm.invoke(prompt)

        return response.content.strip()

    except Exception as e:
        return f"ERROR: {str(e)}"


# ============================================================
# TOOL 4: Generate Final Audit Report
# ============================================================

@tool
def generate_bill_validation_report(
    procedure_validation: str,
    medicine_validation: str
) -> str:
    """
    Generates final bill audit report.
    """

    prompt = f"""
You are a hospital billing audit expert.

Procedure Validation:
{procedure_validation}

Medicine Validation:
{medicine_validation}

Generate final report including:

1. Summary
2. Overpriced Items
3. Valid Items
4. Estimated Excess Billing
5. Recommendation

Be concise and structured.
"""

    response = llm.invoke(prompt)

    return response.content.strip()


BILL_VALIDATOR_SYSTEM_PROMPT = """
You are the Hospital Bill Validation Agent.

Your job is to detect overpricing in hospital bills using
CGHS hospital rate rules and NPPA medicine ceiling prices.

STRICT WORKFLOW:

Step 1:
Call extract_bill_items with the bill KB name.

Step 2:
Parse the JSON output and call validate_procedure_charges using:
- procedures
- investigations
- room_charges
- icu_charges

Step 3:
Call validate_medicine_prices using:
- medicines

Step 4:
Call generate_bill_validation_report using outputs from previous tools.

Rules:
- Always rely on knowledge base evidence.
- Never invent prices.
- Compare hospital charges with CGHS and NPPA reference values.
- Clearly mark items as VALID or OVERPRICED.
- Calculate excess billing.
- Give the final report after all the tools execution which params you taken from kb and what is the comparision you done.
- The report must be provided even if the bill is underpriced or overpriced.
"""


# ============================================================
# TOOL LIST
# ============================================================

BILL_VALIDATOR_TOOLS = [
    extract_bill_items,
    validate_procedure_charges,
    validate_medicine_prices,
    generate_bill_validation_report
]