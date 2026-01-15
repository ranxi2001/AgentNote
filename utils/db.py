#!/usr/bin/env python3
"""
AgentNote Database Utility
Markdown 文档知识库数据库工具
"""

import sqlite3
import re
import json
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# 数据库路径
DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "agentnote.db"
SCHEMA_PATH = Path(__file__).parent.parent / "schema.sql"


def ensure_db_dir():
    """确保数据目录存在"""
    DB_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection():
    """获取数据库连接的上下文管理器"""
    ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """初始化数据库"""
    ensure_db_dir()

    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()

    with get_connection() as conn:
        conn.executescript(schema_sql)

    print(f"✅ 数据库初始化完成: {DB_PATH}")
    return True


def row_to_dict(row):
    """将 sqlite3.Row 转换为字典"""
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows):
    """将多行结果转换为字典列表"""
    return [row_to_dict(row) for row in rows]


def generate_slug(title: str) -> str:
    """从标题生成 URL 友好的 slug"""
    # 移除特殊字符，保留中文、字母、数字
    slug = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', title.lower())
    # 空格替换为短横线
    slug = re.sub(r'[\s_]+', '-', slug)
    # 移除首尾短横线
    slug = slug.strip('-')
    # 添加时间戳确保唯一
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{slug}-{timestamp}" if slug else timestamp


# === 文档 CRUD ===

def add_document(title: str, content: str, category: str = None,
                 tags: list = None, summary: str = None,
                 source: str = "chat", slug: str = None) -> dict:
    """添加新文档"""
    if not slug:
        slug = generate_slug(title)

    # 如果没有摘要，从内容提取前100字
    if not summary:
        # 去除 markdown 标记提取纯文本摘要
        plain = re.sub(r'[#*`\[\]()>-]', '', content)
        summary = plain[:100].strip() + ('...' if len(plain) > 100 else '')

    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO documents (slug, title, content, category, summary, source)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (slug, title, content, category, summary, source)
        )
        doc_id = cursor.lastrowid

        # 添加标签
        if tags:
            for tag_name in tags:
                tag_name = tag_name.strip()
                if not tag_name:
                    continue
                # 获取或创建标签
                conn.execute(
                    "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                    (tag_name,)
                )
                tag_row = conn.execute(
                    "SELECT id FROM tags WHERE name = ?", (tag_name,)
                ).fetchone()
                if tag_row:
                    conn.execute(
                        "INSERT OR IGNORE INTO document_tags (document_id, tag_id) VALUES (?, ?)",
                        (doc_id, tag_row['id'])
                    )

        return {
            'id': doc_id,
            'slug': slug,
            'title': title
        }


def get_document(doc_id: int = None, slug: str = None) -> dict:
    """获取单个文档"""
    with get_connection() as conn:
        if doc_id:
            row = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (doc_id,)
            ).fetchone()
        elif slug:
            row = conn.execute(
                "SELECT * FROM documents WHERE slug = ?", (slug,)
            ).fetchone()
        else:
            return None

        result = row_to_dict(row)
        if result:
            # 获取标签
            tags = conn.execute(
                """SELECT t.name FROM tags t
                   JOIN document_tags dt ON t.id = dt.tag_id
                   WHERE dt.document_id = ?""",
                (result['id'],)
            ).fetchall()
            result['tags'] = [t['name'] for t in tags]

        return result


def update_document(doc_id: int, **kwargs) -> bool:
    """更新文档"""
    allowed_fields = {'title', 'content', 'category', 'summary', 'source'}
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return False

    updates['updated_at'] = datetime.now().isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [doc_id]

    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE documents SET {set_clause} WHERE id = ?", values
        )

        # 更新标签
        if 'tags' in kwargs:
            # 清除旧标签
            conn.execute(
                "DELETE FROM document_tags WHERE document_id = ?", (doc_id,)
            )
            # 添加新标签
            for tag_name in kwargs['tags']:
                tag_name = tag_name.strip()
                if not tag_name:
                    continue
                conn.execute(
                    "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                    (tag_name,)
                )
                tag_row = conn.execute(
                    "SELECT id FROM tags WHERE name = ?", (tag_name,)
                ).fetchone()
                if tag_row:
                    conn.execute(
                        "INSERT OR IGNORE INTO document_tags (document_id, tag_id) VALUES (?, ?)",
                        (doc_id, tag_row['id'])
                    )

        return cursor.rowcount > 0


def delete_document(doc_id: int) -> bool:
    """删除文档"""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        return cursor.rowcount > 0


def search_documents(keyword: str = None, category: str = None,
                     tag: str = None, limit: int = 20, offset: int = 0) -> list:
    """搜索文档"""
    conditions = []
    params = []

    if keyword:
        conditions.append(
            "(d.title LIKE ? OR d.content LIKE ? OR d.summary LIKE ?)"
        )
        like_pattern = f"%{keyword}%"
        params.extend([like_pattern, like_pattern, like_pattern])

    if category:
        conditions.append("d.category = ?")
        params.append(category)

    if tag:
        conditions.append("""
            d.id IN (
                SELECT dt.document_id FROM document_tags dt
                JOIN tags t ON dt.tag_id = t.id
                WHERE t.name = ?
            )
        """)
        params.append(tag)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    with get_connection() as conn:
        rows = conn.execute(
            f"""SELECT d.*, GROUP_CONCAT(t.name) as tags_str
                FROM documents d
                LEFT JOIN document_tags dt ON d.id = dt.document_id
                LEFT JOIN tags t ON dt.tag_id = t.id
                WHERE {where_clause}
                GROUP BY d.id
                ORDER BY d.created_at DESC
                LIMIT ? OFFSET ?""",
            params + [limit, offset]
        ).fetchall()

        results = []
        for row in rows:
            doc = row_to_dict(row)
            doc['tags'] = doc['tags_str'].split(',') if doc.get('tags_str') else []
            del doc['tags_str']
            results.append(doc)

        return results


def get_recent_documents(limit: int = 10) -> list:
    """获取最近文档"""
    return search_documents(limit=limit)


def get_categories() -> list:
    """获取所有分类及计数"""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT category, COUNT(*) as count
               FROM documents
               WHERE category IS NOT NULL AND category != ''
               GROUP BY category
               ORDER BY count DESC"""
        ).fetchall()
        return rows_to_list(rows)


def get_all_tags() -> list:
    """获取所有标签及计数"""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT t.name, COUNT(dt.document_id) as count
               FROM tags t
               LEFT JOIN document_tags dt ON t.id = dt.tag_id
               GROUP BY t.id
               ORDER BY count DESC"""
        ).fetchall()
        return rows_to_list(rows)


def get_documents_count() -> int:
    """获取文档总数"""
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) as count FROM documents").fetchone()
        return row['count'] if row else 0


# === CLI 入口 ===

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_database()
    else:
        print("Usage: python db.py init")
        print(f"Database path: {DB_PATH}")
