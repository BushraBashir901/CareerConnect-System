# CareerConnect — AI-Powered Recruitment Platform

CareerConnect is an AI-powered recruitment platform built using FastAPI, PostgreSQL, Redis, Celery, and LLM integrations.

It streamlines hiring workflows through resume parsing, AI-powered candidate matching, chatbot orchestration, and async background processing.

## Features

* JWT + Google OAuth Authentication
* Resume Parsing & AI Analysis
* AI-based Candidate Matching
* Chatbot & Conversation Memory Handling
* Redis Caching & Session Management
* Celery Background Workers
* Scalable FastAPI Backend Architecture

## Tech Stack

* FastAPI
* PostgreSQL
* Redis
* Celery
* SQLAlchemy
* LLM Integrations

## Run Project

```bash

cd CareerConnect
uv sync
uvicorn main:app --reload
```

## Celery Worker

```bash
celery -A app.tasks.worker worker --loglevel=info
```

