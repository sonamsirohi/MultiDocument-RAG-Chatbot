import os
import uuid
import shutil
import re

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash
)

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

import pytesseract

# -----------------------------
# Tesseract Setup
# -----------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["PATH"] += r";C:\Program Files\Tesseract-OCR"

print(shutil.which("tesseract"))

# -----------------------------
# LangChain Imports
# -----------------------------
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

# -----------------------------
# Load ENV
# -----------------------------
load_dotenv()

# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__)
app.secret_key = "your_secret_key_123"

# -----------------------------
# Folders
# -----------------------------
UPLOAD_FOLDER = "uploads"
DB_FOLDER = "chroma_db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DB_FOLDER, exist_ok=True)

# -----------------------------
# TEMP USERS (replace with DB later)
# -----------------------------
users = {}

# =====================================================
# PDF PROCESSING
# =====================================================
def process_pdf(path, filename):
    elements = partition_pdf(
        filename=path,
        strategy="auto",
        infer_table_structure=True
    )

    chunks = chunk_by_title(
        elements,
        max_characters=3000,
        new_after_n_chars=2400,
        combine_text_under_n_chars=500
    )

    return [
        Document(page_content=c.text, metadata={"source": filename})
        for c in chunks
    ]


# =====================================================
# VECTOR DB
# =====================================================
def create_db(documents):
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    return Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory=DB_FOLDER
    )


def load_db():
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    return Chroma(
        persist_directory=DB_FOLDER,
        embedding_function=embedding
    )


# =====================================================
# ROUTES
# =====================================================
@app.route("/")
def home():
    return render_template("home.html")


# -----------------------------
# SIGNUP
# -----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, username):
            flash("Invalid email")
            return redirect("/signup")

        if username in users:
            flash("User exists")
            return redirect("/signup")

        users[username] = generate_password_hash(password)

        flash("Signup success")
        return redirect("/login")

    return render_template("signup.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if username not in users:
            flash("User not found")
            return redirect("/login")

        if not check_password_hash(users[username], password):
            flash("Wrong password")
            return redirect("/login")

        session["user"] = username
        session["uploaded"] = False

        # ⭐ INIT CHAT HISTORY HERE
        session["chat_history"] = []

        return redirect("/dashboard")

    return render_template("login.html")


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template(
        "index.html",
        user=session["user"],
        uploaded=session.get("uploaded", False),
        chat_history=session.get("chat_history", [])
    )


# -----------------------------
# UPLOAD PDFs
# -----------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    files = request.files.getlist("files")
    all_docs = []

    uploaded_files = session.get("uploaded_files", [])

    for file in files:
        if file.filename.endswith(".pdf"):

            name = str(uuid.uuid4()) + "_" + file.filename
            path = os.path.join(UPLOAD_FOLDER, name)
            file.save(path)

            uploaded_files.append(file.filename)  

            all_docs.extend(process_pdf(path, file.filename))

    if all_docs:
        create_db(all_docs)
        session["uploaded"] = True
        session["uploaded_files"] = uploaded_files

    return redirect("/dashboard")


# -----------------------------
# ASK (WITH HISTORY)
# -----------------------------
@app.route("/ask", methods=["POST"])
def ask():
    if "user" not in session:
        return redirect("/login")

    query = request.form["query"]

    db = load_db()
    docs = db.similarity_search(query, k=4)

    context = "\n\n".join([d.page_content for d in docs])
    sources = list(set([d.metadata["source"] for d in docs]))

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""
Answer only from context.

Context:
{context}

Question:
{query}
"""

    answer = llm.invoke(prompt).content

    # ⭐ STORE HISTORY
    if "chat_history" not in session:
        session["chat_history"] = []

    session["chat_history"].append({
        "user": query,
        "bot": answer
    })

    session.modified = True  # IMPORTANT for Flask session update

    return render_template(
        "index.html",
        user=session["user"],
        uploaded=True,
        answer=answer,
        sources=sources,
        chat_history=session["chat_history"]
    )


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)