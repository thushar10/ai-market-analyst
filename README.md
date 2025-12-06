## Getting Started (Dev)

### 1. Clone and set up env


```bash
git clone https://github.com/your-user/ai-market-analyst.git
cd ai-market-analyst

cp .env.example .env
# edit .env and add your API keys
```



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



## Prerequisites

To run this project, you will need:

1. **OpenAI account**
   - Used for embeddings (OpenAI Embeddings node)
   - Get your API key from the OpenAI dashboard
   - Put it into `.env` as `OPENAI_API_KEY=...`

2. **Pinecone account**
   - Create a Pinecone index named `finance-agent`
     - Metric: cosine or dot product
     - Dimension: must match your embedding model (e.g. 1536 for `text-embedding-3-small`)
   - Get your API key and environment
   - Put them in `.env`:
     - `PINECONE_API_KEY=...`
     - `PINECONE_ENVIRONMENT=...`

3. **Gemini (Google AI Studio) API key**
   - Used by the Gemini Chat Model nodes in n8n
   - Configure the **Google PaLM / Gemini credential** inside n8n with your key

4. **NewsAPI account (optional but recommended)**
   - Used by the MCP server to fetch recent market news
   - Get an API key from NewsAPI
   - Put it in `.env` as `NEWS_API_KEY=...`

5. **Google account (for Gmail + Sheets)**
   - Create a Google Cloud project
   - Enable:
     - Gmail API
     - Google Sheets API
   - Configure OAuth consent screen (Testing is fine)
   - Create OAuth client credentials
   - In n8n:
     - Create **Gmail OAuth2** credential (for sending approval emails)
     - Create **Google Sheets OAuth2** credential (for appending rows to the ledger)
   - Connect them once via the UI so tokens are stored in `n8n_data`

6. **10-K PDF**
   - Download the latest 10-K for a ticker (e.g. Apple AAPL)
   - Save it to `data/files/aapl-10k.pdf`
   - The `Ingest 10-K` workflow expects it at `/files/aapl-10k.pdf` inside the container.

