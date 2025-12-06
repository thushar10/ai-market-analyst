#!/bin/sh

# Import workflows ONLY if none exist yet
WORKFLOW_COUNT=$(n8n list:workflow | wc -l)

if [ "$WORKFLOW_COUNT" -le 1 ]; then
  echo "No workflows found — importing default workflows..."
  n8n import:workflow --input=/workflows/agent-market-analyst.json
  n8n import:workflow --input=/workflows/rag-search.json
  n8n import:workflow --input=/workflows/ingest-10k.json
else
  echo "✔ Workflows already exist — skipping import."
fi

echo "🚀 Starting n8n..."
exec n8n start
