#!/usr/bin/env python3
"""
AgentNote Skill: save_doc
Save Markdown documents to knowledge base
"""

import sys
import json
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
from db import add_document, init_database, DB_PATH


def main():
    # Ensure database exists
    if not DB_PATH.exists():
        init_database()

    # Read input
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = sys.stdin.read().strip()

    if not input_data:
        print(json.dumps({
            "success": False,
            "error": "No input data provided"
        }, ensure_ascii=False))
        return

    try:
        data = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"JSON parse error: {str(e)}"
        }, ensure_ascii=False))
        return

    # Validate required fields
    if not data.get("title") or not data.get("content"):
        print(json.dumps({
            "success": False,
            "error": "title and content are required"
        }, ensure_ascii=False))
        return

    # Save to database
    try:
        result = add_document(
            title=data["title"],
            content=data["content"],
            category=data.get("category"),
            tags=data.get("tags", []),
            summary=data.get("summary"),
            source=data.get("source", "chat")
        )

        print(json.dumps({
            "success": True,
            "id": result["id"],
            "slug": result["slug"],
            "message": f"Document saved: {result['title']}"
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
