policy-llm-engine/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── config.py
├── templates/
│   └── index.html
├── static/
│   └── css/
│       └── style.css
├── data/
│   ├── policies/
│   ├── contracts/
│   └── emails/
├── indexer/
│   └── chunk_and_embed.py
├── engine/
│   ├── query_parser.py
│   ├── retriever.py
│   ├── reasoner.py
│   ├── formatter.py
│   ├── session_manager.py
│   └── db.py
└── tests/
    ├── test_parser.py
    └── test_retriever.py
