Personal Expense Tracker — AI Agent

An AI-powered personal expense tracker built as a college project for Agentic AI and Automation. It combines a Flask web interface, SQLite database, and an OpenAI-powered agent that understands natural-language expense queries and can use tools to read or add expense data.

Problem Statement

AI Agent for Personal Expense Tracking

Develop an AI agent that helps users record and analyze personal expenses through natural-language interaction while maintaining a structured expense database.

Objectives

Record and manage personal expenses.

Store transaction data in SQLite.

Support natural-language expense queries.

Allow the AI agent to add expenses through tool calling.

Provide spending summaries and category-wise analysis.

Provide an interactive dashboard for viewing transactions.

Key Features

AI Expense Assistant

Examples:

How much did I spend?

How much did I spend this month?

How much did I spend on food this month?

How much did I spend today?

Add ₹300 for dinner today

Expense Management

Add expenses manually.

Delete transactions.

Search transactions.

Filter transactions by category.

View recent transactions.

Spending Dashboard

Displays:

Total spending

Current-month spending

Transaction count

Category-wise spending breakdown

Quick prompts for common AI queries

Agentic AI Architecture

                    User
                     |
          +----------+----------+
          |                     |
     Manual Entry        Natural Language
          |                     |
          v                     v
      Flask App          AI Expense Agent
                                |
                         Tool Selection
                       +--------+--------+
                       |                 |
                       v                 v
              Spending Summary      Add Expense
                       |                 |
                       +--------+--------+
                                |
                                v
                         SQLite Database
                                |
                                v
                         Dashboard / Response

How the Agent Works

The user sends a natural-language request.

Flask receives the request through the /chat route.

The OpenAI model interprets the user's intent.

The model selects an available tool when actual expense data or a database operation is required.

The tool reads from or writes to SQLite.

The tool result is returned to the agent.

The agent generates a natural-language response.

The dashboard reflects newly added expense data when applicable.

Available Agent Tools

get_spending_summary

Retrieves spending information from the database.

Supported periods:

all

this_month

today

It can also filter by category.

add_expense

Adds an expense to SQLite using:

amount

category

description

expense date

Technology Stack

Layer

Technology

Frontend

HTML, CSS, JavaScript

Backend

Python, Flask

Database

SQLite

AI

OpenAI API

Environment

python-dotenv

Production Server

Gunicorn

Deployment

Render

Version Control

Git / GitHub

Project Structure

personal-expense-agent/
│
├── app.py
├── agent.py
├── database.py
├── requirements.txt
├── .python-version
├── .env
├── .gitignore
│
├── data/
│   └── expenses.db
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js

Local Setup

1. Clone the repository

git clone https://github.com/Rutvasawarkar/Personal-Expense-Tracker.git
cd Personal-Expense-Tracker

2. Create and activate a virtual environment

python -m venv .venv

Windows:

.venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure the OpenAI API key

Create .env in the project root:

OPENAI_API_KEY=your_api_key_here

Do not commit .env to GitHub.

5. Run the application

python app.py

Open:

http://127.0.0.1:5000

Deployment

The application is deployed using Render.

Production start command:

gunicorn app:app

Live application:

https://personal-expense-tracker-i6as.onrender.com

Screenshots

Add screenshots of the deployed application here. Suggested files:

docs/
├── dashboard.png
├── ai-assistant.png
├── spending-breakdown.png
└── transactions.png

Then reference them, for example:

![Dashboard](docs/dashboard.png)

Example Agent Interactions

User Input

Agent Action

How much did I spend?

Reads spending summary

How much did I spend this month?

Reads current-month spending

How much did I spend on food this month?

Reads category + period summary

How much did I spend today?

Reads today's spending

Add ₹90 for coffee today

Calls the expense insertion tool

Security Notes

The OpenAI API key is stored in an environment variable.

.env is excluded from version control.

The API key is not included in frontend code.

Current Limitations

SQLite is suitable for this academic project but is not ideal for multi-user production workloads.

The Render free instance can sleep after inactivity, increasing first-request response time.

Persistent cloud database storage is not configured.

The application focuses on a single-user expense workflow.

AI functionality depends on availability of the configured OpenAI API.

Future Scope

PostgreSQL or another persistent cloud database

User authentication

Monthly and yearly financial reports

Advanced charts and trend analysis

Budget limits and alerts

Recurring expense detection

CSV/PDF export

Voice-based expense entry

Additional agent tools for financial analysis

Academic Context

Course: Agentic AI and Automation

Project: AI Agent for Personal Expense Tracking

The project demonstrates:

AI agents

Tool calling

Natural-language interaction

Database operations

Web application development

Dashboard analytics

Cloud deployment

License

This project was developed as an academic/educational project.