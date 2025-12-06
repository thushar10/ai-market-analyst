## Getting Started (Dev)

### 1. Clone and set up env

```bash
git clone https://github.com/your-user/ai-market-analyst.git
cd ai-market-analyst

cp .env.example .env
# edit .env and add your API keys




# AI Market Analyst Agent

This project is an end-to-end AI “paper trading” assistant built with:

- **n8n** as the workflow orchestrator
- **Pinecone + OpenAI embeddings** for RAG over 10-K filings
- **Google Gemini** as the main LLM
- **Custom MCP server** for live market data (Yahoo Finance) & news (NewsAPI)
- **Gmail + Google Sheets** for human-in-the-loop approvals and logging

### What it does

1. **Document Ingestion (Ingest 10-K workflow)**
   - Reads a 10-K PDF (e.g. Apple’s annual report) from a mounted folder
   - Splits it into chunks, embeds them with OpenAI embeddings
   - Stores vectors in a Pinecone index (`finance-agent`)

2. **RAG Tool (Tool - RAG Search workflow)**
   - When called with a question, retrieves the most relevant chunks from Pinecone
   - Uses Gemini to answer strictly based on the retrieved context
   - Designed as a reusable “tool” workflow that other workflows can call

3. **Market Analyst Agent (Agent - Market Analyst workflow)**
   - Exposes an HTTP **webhook** (`/webhook/market-analyst`)
   - Extracts the stock ticker from the user’s question using Gemini
   - Calls a custom **MCP server** to:
     - Get current stock price & 50-day average (via Yahoo Finance)
     - Get recent news headlines (via NewsAPI)
   - Calls the **RAG Search** workflow to pull risk factors from the latest 10-K
   - Feeds everything into Gemini to produce a **BUY / HOLD / SELL** recommendation with reasoning
   - If BUY or SELL:
     - Sends you an **approval email** (Gmail) with the analysis & an approval link
     - Waits at a **Wait** node until you click the link
     - On approval, appends a row to **Google Sheets** (`AI Trade Ledger`) with:
       - Date, Ticker, Action, Reasoning, Status=Approved

This creates a complete **human-in-the-loop AI trading assistant** with real data, RAG, agents, and an auditable trade ledger.
