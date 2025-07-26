policy-llm-engine/
├── app.py
├── requirements.txt
├── README.md
├── config.py
├── .env.example
│
├── templates/
│   └── index.html
│
├── static/
│   └── css/
│       └── style.css
│
├── data/
│   ├── policies/
│   ├── contracts/
│   ├── emails/
│   └── embeddings/
│
├── indexer/
│   └── chunk_and_embed.py
│
├── engine/
│   ├── query_parser.py
│   ├── retriever.py
│   ├── reasoner.py
│   ├── formatter.py
│   ├── session_manager.py
│   ├── db.py
│   ├── alternate_policy_recommender.py
│   └── lru_cache.py
│
├── models/
│   └── llm_local_runner.py
