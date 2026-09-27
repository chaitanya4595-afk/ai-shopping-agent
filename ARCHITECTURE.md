# Architecture

## Overview

AI Shopping Agent is a tool-using conversational application. The language
model orchestrates the workflow, while deterministic tools own product search,
rating retrieval, and order persistence.

```text
User
  │
  ├── text request ───────────────────────────┐
  │                                           │
  └── product image ─► vision model ──────────┤
                                              ▼
                                      LangChain agent
                                      Qwen on Groq
                                              │
                    ┌─────────────────────────┼─────────────────────┐
                    ▼                         ▼                     ▼
             search_products             get_rating            checkout
                    │                         │                     │
                    └─────────────────────────┴──────────► SQLite store
                                              │
                                              ▼
                                  ranked products / order
```

## Components

### Streamlit application

`app.py` owns chat state, image upload, and rendering. It passes conversation
history to the agent and displays either candidate products or an order
confirmation.

### Agent orchestration

`src/ai_shopping_agent/agent.py` defines the Groq chat model, vision model,
tools, and system policy. The policy separates browsing from ordering and
requires explicit user confirmation before checkout.

### Product catalog

The SQLite database in `data/store.db` contains products, customer reviews, and
demo orders. Product search supports keyword, price, and organic filters.

### Ratings

`src/ai_shopping_agent/reviews.py` contains deterministic rating aggregation.
Keeping this logic outside the model makes it independently testable.

### Vision path

Uploaded images are encoded and sent to Llama 4 Scout. The model returns a
compact product description and search intent, which then enters the same
catalog-search path as a normal text request.

## Safety boundary

Browsing cannot call checkout. The agent must first display product IDs and
receive an explicit confirmation. Order selection is resolved from IDs that
were already shown to the user rather than guessed by the model.

## Testing boundary

Tests exercise the SQLite catalog and deterministic rating functions without
calling external language-model APIs.
