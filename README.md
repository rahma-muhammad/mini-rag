# MiniRAG Learning project

I will use this repo to learn the best practices to create production-ready RAG application.

# Learning Objectives

- [ ] Practice clean code 
- [ ] Using docker
- [ ] Using MongoDB 
- [ ] Using Qdrant as vector database

# How to run it

- create new environment

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd.exe)
.venv\Scripts\activate.bat
```

- install dependencies

```bash 
pip install -r requirements.txt
```

- run docker 

```bash
cd docker
# start in background (detached). On Linux you may need sudo; on macOS/Windows you usually don't.
docker compose up -d
```
- run app

```bash
cd ../src
# bind to 0.0.0.0 so the server is reachable from other containers/hosts; use --reload in dev
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```