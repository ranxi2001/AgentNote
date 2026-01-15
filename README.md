# AgentNote 📚

> Agent-driven lightweight markdown knowledge base

A minimal **Claude Skills + SQLite** architecture for managing markdown documents. Just paste your messy notes, Claude formats them into clean markdown and stores them. The web UI provides a blog-style reading experience.

## Features

- **Markdown-first**: All content stored as markdown
- **Agent-powered**: Claude handles formatting and categorization
- **Zero friction**: Paste text → auto-format → stored
- **Blog viewer**: Clean web UI for reading documents
- **Local storage**: SQLite database, your data stays local

## Quick Start

### 1. Clone and Initialize

```bash
git clone https://github.com/yourusername/AgentNote.git
cd AgentNote
python utils/db.py init
```

### 2. Start Web UI

```bash
cd web
python app.py
# Open http://localhost:5000
```

### 3. Add Documents via Claude

In a Claude conversation with skills enabled:

```
You: Format and save this:
     python虚拟环境 用venv创建 python -m venv myenv
     激活linux是source myenv/bin/activate 退出用deactivate

Claude: [Uses format_to_markdown skill]
        [Uses save_doc skill]

        ✅ Saved: "Python Virtual Environment Guide"
        Category: Tech | Tags: python, venv
```

## Project Structure

```
AgentNote/
├── skills/
│   ├── save_doc/              # Save markdown documents
│   │   ├── SKILL.md
│   │   └── save_doc.py
│   └── format_to_markdown/    # Auto-format text to markdown
│       └── SKILL.md
├── utils/
│   └── db.py                  # Database operations
├── data/
│   └── .gitkeep               # DB created here (gitignored)
├── web/
│   ├── app.py                 # Flask API server
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
│       └── index.html
├── schema.sql
├── .gitignore
└── README.md
```

## Skills

### save_doc

Save markdown content to database:

```bash
python skills/save_doc/save_doc.py '{
  "title": "Document Title",
  "content": "# Markdown Content\n\nYour content here...",
  "category": "Tech",
  "tags": ["python", "tutorial"]
}'
```

### format_to_markdown

Claude-executed skill that transforms raw text into structured markdown with:
- Proper headings hierarchy
- Code blocks with language hints
- Lists and formatting
- Auto-generated title, category, tags

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/docs` | List documents (supports `?category=`, `?tag=`, `?keyword=`) |
| GET | `/api/docs/<id>` | Get document by ID |
| POST | `/api/docs` | Add new document |
| PUT | `/api/docs/<id>` | Update document |
| DELETE | `/api/docs/<id>` | Delete document |
| GET | `/api/categories` | List categories |
| GET | `/api/tags` | List tags |

## Database Schema

```sql
documents (id, slug, title, content, category, summary, source, timestamps)
tags (id, name)
document_tags (document_id, tag_id)
```

## Requirements

- Python 3.8+
- Flask

```bash
pip install flask
```

## License

MIT
