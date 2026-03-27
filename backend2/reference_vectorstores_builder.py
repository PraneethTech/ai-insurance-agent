from pathlib import Path
import pandas as pd

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from rag import embed_instance


VECTOR_STORES_DIR = Path("vectorstores")

DATA_DIR = Path("shared") / "bill_docs"

CGHS_FILE = DATA_DIR / "Cghs_Rate_List1500.00.xlsx"
NPPA_FILE = DATA_DIR / "NPPA-UPDATED-PRICE-LIST-AS-ON-01-04-2025_compressed-1_compressed.pdf"

embeddings = embed_instance.get_embeddings()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200
)


# ============================================================
# CGHS EXCEL LOADER (WITHOUT UNSTRUCTURED)
# ============================================================

def load_cghs_excel():

    df = pd.read_excel(CGHS_FILE)

    documents = []

    for _, row in df.iterrows():

        row_text = "\n".join(
            [f"{col}: {row[col]}" for col in df.columns]
        )

        documents.append(
            Document(
                page_content=row_text,
                metadata={"source": "CGHS_RATE_LIST"}
            )
        )

    return documents


# ============================================================
# BUILD CGHS VECTORSTORE
# ============================================================

def build_cghs_vectorstore():

    docs = load_cghs_excel()

    split_docs = splitter.split_documents(docs)

    vectorstore = FAISS.from_documents(split_docs, embeddings)

    path = VECTOR_STORES_DIR / "cghs_rates"
    vectorstore.save_local(str(path))

    print("CGHS vectorstore created")


# ============================================================
# BUILD NPPA VECTORSTORE
# ============================================================

def build_nppa_vectorstore():

    loader = PyPDFLoader(str(NPPA_FILE))
    docs = loader.load()

    split_docs = splitter.split_documents(docs)

    vectorstore = FAISS.from_documents(split_docs, embeddings)

    path = VECTOR_STORES_DIR / "nppa_prices"
    vectorstore.save_local(str(path))

    print("NPPA vectorstore created")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    VECTOR_STORES_DIR.mkdir(exist_ok=True)

    build_cghs_vectorstore()
    build_nppa_vectorstore()

    print("All reference KBs built successfully")