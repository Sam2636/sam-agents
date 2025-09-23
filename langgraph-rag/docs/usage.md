Install dependencies:

pip install -r requirements.txt


Start the agent:

python -m src.rag_agent.main


---

### 2️⃣ `docs/usage.md` — Usage Guide

```markdown
# Usage Guide

## Environment Setup

Create a `.env` file from `.env.example` and fill in your API keys:

```bash
cp .env.example .env

Running the Agent
python -m src.rag_agent.main


This starts the RAG agent locally.

The agent loads documents from the docs/ folder and answers queries based on your knowledge base.

Docker Usage

Build and run the Docker container:

docker build -t langgraph-rag .
docker run -it --env-file .env langgraph-rag

Local Documentation Server

Test your docs locally with MkDocs:

mkdocs serve


Open your browser at http://127.0.0.1:8000/

Live reload is enabled for easy editing


---

✅ These files are ready to go. Put them in your `docs/` folder, commit, and push — your GitHub Pages site will automatically update with this content.  

Do you want me to **also create a sample sidebar/navigation for `mkdocs.yml`** so these pages show nicely on the site?
