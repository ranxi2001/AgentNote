---
name: save_doc
description: Save markdown document to AgentNote knowledge base. Use when user wants to save, store, or archive formatted content, notes, or articles.
---

# Save Document Skill

Save Markdown documents to AgentNote knowledge base.

## When to Use

- User says "save this", "store this", "archive this"
- After formatting content with `format_to_markdown`
- When user provides structured markdown content

## Input Format

```json
{
  "title": "Document title",
  "content": "# Markdown Content\n\nFull markdown text...",
  "category": "Category name (optional)",
  "tags": ["tag1", "tag2"],
  "summary": "Brief summary (optional, auto-generated if empty)"
}
```

## Usage

```bash
cd /home/AgentNote
python skills/save_doc/save_doc.py '{"title":"My Note","content":"# Hello\n\nContent here","category":"Tech"}'
```

## Output

Returns document ID, slug, and confirmation:

```json
{
  "success": true,
  "id": 1,
  "slug": "my-note-20260115",
  "message": "Document saved: My Note"
}
```

## Workflow

1. Receive markdown content (usually from `format_to_markdown`)
2. Validate required fields (title, content)
3. Generate slug from title
4. Auto-generate summary if not provided
5. Store in database with tags
