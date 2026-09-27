# AI Shopping Agent

> A multimodal, tool-using shopping assistant that searches a product catalog,
> checks customer ratings, understands product images, and only places an order
> after explicit user confirmation.

This project demonstrates an agentic workflow where the LLM does not own the
business data or transaction logic. LangChain orchestrates the conversation;
SQLite-backed tools perform product lookup, rating aggregation, and checkout;
and a separate vision model converts uploaded images into structured search
intent.

## Key features

- Natural-language product search
- Maximum-price and organic-product filtering
- Customer-rating lookup before recommendations
- Image-based product search with a multimodal model
- Multi-turn selection such as `order #2`
- Explicit confirmation boundary before checkout
- SQLite product, review, and order persistence
- Streamlit conversational interface
- Tests for catalog integrity and deterministic rating logic

## Example workflow

```text
User: I want organic honey under $20 with a 4.5+ rating
                           │
                           ▼
                    LangChain Agent
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       search_products              get_rating
              │                         │
              └──────────► SQLite ◄─────┘
                           │
                           ▼
                 qualifying products
                           │
                           ▼
                  user selects #2
                           │
                           ▼
                       checkout
                           │
                           ▼
                   order confirmation
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for component responsibilities,
tool boundaries, and the image-search path.

## Technology stack

| Technology | Role |
| --- | --- |
| Python 3.12 | Application language |
| LangChain | Agent and tool orchestration |
| Groq / Qwen | Agent reasoning model |
| Llama 4 Scout | Product-image understanding |
| SQLite | Product, review, and order data |
| Streamlit | Conversational UI |
| pytest | Deterministic component tests |
| uv | Dependency and environment management |

## Project structure

```text
.
├── app.py
├── src/ai_shopping_agent/
│   ├── __init__.py
│   ├── agent.py
│   └── reviews.py
├── data/
│   └── store.db
├── scripts/
│   └── setup_db.py
├── docs/sample_images/
├── tests/
│   ├── test_database.py
│   └── test_reviews.py
├── .env.example
├── ARCHITECTURE.md
├── pyproject.toml
└── requirements.txt
```

## Local setup

```bash
git clone https://github.com/chaitanya4595-afk/ai-shopping-agent.git
cd ai-shopping-agent
uv sync --extra dev
cp .env.example .env
```

Add your Groq API key to `.env`, then run:

```bash
uv run streamlit run app.py
```

Run tests with:

```bash
uv run pytest
```

## Limitations

- The catalog is a small demo dataset rather than a live retailer inventory.
- Checkout records a demo order locally; it does not process payment.
- SQLite is appropriate for this prototype, not high-concurrency commerce.
- Model output may vary and image interpretation may be imperfect.
- Public deployments consume the configured Groq quota.

## Future improvements

- Replace SQLite with a hosted transactional database
- Add structured tool outputs and stronger schema validation
- Add inventory quantities and transactional stock checks
- Add agent evaluation traces and regression tests
- Add authentication and user-specific carts
