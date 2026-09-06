DeepResearch AI

Multi-Agent AI Research & Intelligence Platform

DeepResearch AI is a multi-agent research assistant that takes a user's research question and passes it through a coordinated AI pipeline.

Instead of asking a single AI model to produce one response, the platform uses specialized agents for research, critical analysis, insight generation, and final report building.

Features

Multi-agent AI research pipeline

Research Agent for initial topic exploration

Critical Analysis Agent for identifying weaknesses, risks, contradictions, and missing perspectives

Insight Generation Agent for patterns, trends, hypotheses, and practical implications

Report Builder Agent for producing a structured final research report

FastAPI backend

Next.js frontend

Gemini-powered AI generation

Backend health monitoring

Graceful Gemini free-tier quota handling

Automated backend and frontend tests

Multi-Agent Architecture

User Research Question
        |
        v
   Next.js Frontend
        |
        v
   FastAPI Backend
        |
        v
     Orchestrator
        |
        v
  Research Agent
        |
        v
Critical Analysis Agent
        |
        v
 Insight Generation Agent
        |
        v
 Report Builder Agent
        |
        v
Structured Research Report
        |
        v
   Next.js Frontend

Agents

1. Research Agent

Creates the initial research brief for the user's question.

It identifies:

Topic overview

Important concepts

Key research questions

Claims requiring verification

Directions for deeper research

2. Critical Analysis Agent

Critically evaluates the research brief.

It identifies:

Strong points

Weak or unsupported claims

Missing perspectives

Contradictions

Verification requirements

Potential bias

Areas for improvement

3. Insight Generation Agent

Combines the research brief and critical analysis to generate higher-level insights.

It focuses on:

Patterns

Trends

New insights

Hypotheses

Practical implications

Unanswered questions

4. Report Builder Agent

Combines all previous agent outputs into a professional final report containing:

Executive Summary

Research Overview

Key Findings

Critical Analysis

Key Insights and Trends

Practical Implications

Open Questions

Conclusion

Tech Stack

Backend

Python

FastAPI

Pydantic

Google Gemini API

Google GenAI Python SDK

Pytest

Frontend

Next.js 16

React

TypeScript

Vitest

Testing Library

Development

Git

GitHub

VS Code

Project Structure

deepresearch-ai/
|
+-- backend/
|   |
|   +-- agents/
|   |   +-- research_agent.py
|   |   +-- analysis_agent.py
|   |   +-- insight_agent.py
|   |   +-- report_builder_agent.py
|   |
|   +-- services/
|   |   +-- gemini_service.py
|   |
|   +-- tests/
|   |
|   +-- main.py
|   +-- orchestrator.py
|
+-- frontend/
|   |
|   +-- src/
|       +-- app/
|       |   +-- page.tsx
|       |   +-- page.test.tsx
|       |
|       +-- lib/
|           +-- api.ts
|
+-- docs/
+-- examples/
+-- reports/
+-- .env.example
+-- .gitignore
+-- README.md

API Endpoints

Health Check

GET /health

Checks whether the FastAPI backend is running.

Basic AI Generation

POST /ai/generate

Example request:

{
  "prompt": "Explain Retrieval-Augmented Generation."
}

Multi-Agent Deep Research

POST /research

Example request:

{
  "question": "What are the main benefits and risks of using AI agents in healthcare?"
}

The endpoint runs the complete multi-agent pipeline and returns:

{
  "question": "...",
  "research_brief": "...",
  "critical_analysis": "...",
  "insights": "...",
  "final_report": "..."
}

Local Setup

1. Clone the repository

git clone https://github.com/shantanu-c25/deepresearch-ai.git
cd deepresearch-ai

Backend Setup

Create a Python virtual environment:

python -m venv backend/.venv

Windows PowerShell

Activate it using:

.\backend\.venv\Scripts\Activate.ps1

Install backend dependencies:

pip install -r backend/requirements.txt

Environment Variables

Create:

backend/.env

Add your Gemini API key:

GEMINI_API_KEY=your_gemini_api_key_here

Do not commit .env files or API keys to GitHub.

Start the Backend

From the project root:

python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

Backend URL:

http://127.0.0.1:8000

Frontend Setup

Open another terminal:

cd frontend
npm install
npm run dev

Frontend URL:

http://localhost:3000

Run Backend Tests

From the project root with the backend virtual environment activated:

python -m pytest -q

Current backend test status:

5 passed

Run Frontend Tests

From the frontend directory:

npx vitest run src/app/page.test.tsx --reporter=verbose

Current frontend test status:

3 passed

Error Handling

DeepResearch AI handles Gemini API quota exhaustion gracefully.

If the Gemini free-tier request quota is reached, the backend returns:

429 Too Many Requests

and the frontend displays:

Gemini free-tier quota has been reached. Please try again later.

This prevents quota errors from appearing as generic server failures.

Example Research Question

What are the main benefits and risks of using AI agents in healthcare?

The platform processes the question through:

Research
   ↓
Critical Analysis
   ↓
Insight Generation
   ↓
Final Report

Current Status

FastAPI backend

Gemini integration

Health endpoint

AI generation endpoint

Research Agent

Critical Analysis Agent

Insight Generation Agent

Report Builder Agent

Multi-agent orchestrator

/research API

Next.js frontend integration

Multi-agent research results displayed in UI

Gemini quota-aware error handling

Backend tests

Frontend tests

GitHub repository

Production deployment

Demo video

GitHub

Repository:

https://github.com/shantanu-c25/deepresearch-ai

Author

Shantanu Chattopadhyay

Built as part of an AI Engineering hackathon project.