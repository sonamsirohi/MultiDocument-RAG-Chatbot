# 📚 Multi-Document RAG Chatbot (Flask + LangChain + OpenAI)

An AI-powered **Retrieval-Augmented Generation (RAG) chatbot** that allows users to upload multiple PDF documents and ask intelligent questions based on their content. The system uses **semantic search + LLM reasoning** to generate accurate, context-aware responses.

---


## 📌 Features

- 📄 Upload multiple PDF documents
- 🤖 ChatGPT-style conversational Q&A
- 🔍 Semantic search using embeddings (OpenAI)
- 🧠 Retrieval-Augmented Generation (RAG pipeline)
- 💬 Conversation history stored per session
- 🔐 Simple authentication system (Flask sessions)
- ⚡ Context-based answers only from documents
- 🖥 Clean UI with chat + document panel layout

---

## 🧠 How It Works (RAG Pipeline)

1. **User uploads PDFs**
2. PDFs are parsed using `unstructured`
3. Text is split into chunks
4. Embeddings are generated using OpenAI
5. Stored in **ChromaDB vector database**
6. User asks a question
7. Query is converted into embeddings
8. Similar chunks are retrieved (semantic search)
9. LLM generates answer using retrieved context

---

## 🏗 Architecture
User Query
↓
Flask Backend
↓
Embedding (OpenAI)
↓
ChromaDB Vector Search
↓
Relevant PDF Chunks
↓
LLM (GPT-4o-mini)
↓
Final Answer


---

## 🛠 Tech Stack

- Python
- Flask
- LangChain
- OpenAI API
- ChromaDB (Vector Database)
- HTML, CSS (Frontend)
- PyTesseract (OCR)
- Unstructured (PDF parsing)

---

## 📁 Project Structure

```

MultiDocument-RAG-Chatbot/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── uploads/ (ignored)
├── chroma\_db/ (ignored)
├── myenv/ (ignored)

⚙️ **Installation & Setup
1. Clone repository**
git clone https://github.com/your-username/MultiDocument-RAG-Chatbot.git
cd MultiDocument-RAG-Chatbot

**2. Create virtual environment**
python -m venv myenv
myenv\Scripts\activate   # Windows

**3. Install dependencies**
pip install -r requirements.txt

**4. Add API key**
Create .env file:
OPENAI_API_KEY=your_api_key_here

**5. Run application**
python app.py
