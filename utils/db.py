#!/usr/bin/env python3
"""
AgentNote Database Utility
数据库连接和初始化工具
"""

import sqlite3
import os
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
    conn.row_factory = sqlite3.Row  # 返回字典式结果
    conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """初始化数据库，创建表结构"""
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


# === CRUD 操作 ===

def add_idea(title: str, content: str, category: str = None, 
             keywords: list = None, source: str = "chat") -> int:
    """添加新想法"""
    keywords_json = json.dumps(keywords or [], ensure_ascii=False)
    
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO ideas (title, content, category, keywords, source)
               VALUES (?, ?, ?, ?, ?)""",
            (title, content, category, keywords_json, source)
        )
        return cursor.lastrowid


def get_idea(idea_id: int) -> dict:
    """获取单个想法"""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM ideas WHERE id = ?", (idea_id,)
        ).fetchone()
        result = row_to_dict(row)
        if result and result.get('keywords'):
            result['keywords'] = json.loads(result['keywords'])
        return result


def update_idea(idea_id: int, **kwargs) -> bool:
    """更新想法"""
    allowed_fields = {'title', 'content', 'category', 'keywords', 'source'}
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    if 'keywords' in updates and isinstance(updates['keywords'], list):
        updates['keywords'] = json.dumps(updates['keywords'], ensure_ascii=False)
    
    updates['updated_at'] = datetime.now().isoformat()
    
    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [idea_id]
    
    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE ideas SET {set_clause} WHERE id = ?", values
        )
        return cursor.rowcount > 0


def delete_idea(idea_id: int) -> bool:
    """删除想法"""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM ideas WHERE id = ?", (idea_id,))
        return cursor.rowcount > 0


def search_ideas(keyword: str = None, category: str = None, 
                 limit: int = 20, offset: int = 0) -> list:
    """搜索想法"""
    conditions = []
    params = []
    
    if keyword:
        conditions.append(
            "(title LIKE ? OR content LIKE ? OR keywords LIKE ?)"
        )
        like_pattern = f"%{keyword}%"
        params.extend([like_pattern, like_pattern, like_pattern])
    
    if category:
        conditions.append("category = ?")
        params.append(category)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    with get_connection() as conn:
        rows = conn.execute(
            f"""SELECT * FROM ideas 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?""",
            params + [limit, offset]
        ).fetchall()
        
        results = rows_to_list(rows)
        for r in results:
            if r.get('keywords'):
                r['keywords'] = json.loads(r['keywords'])
        return results


def get_recent_ideas(limit: int = 10) -> list:
    """获取最近的想法"""
    return search_ideas(limit=limit)


def add_relation(idea_id_1: int, idea_id_2: int, 
                 relation_type: str = "related", note: str = None) -> int:
    """添加想法关联"""
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO relations (idea_id_1, idea_id_2, relation_type, note)
               VALUES (?, ?, ?, ?)""",
            (idea_id_1, idea_id_2, relation_type, note)
        )
        return cursor.lastrowid


def get_relations(idea_id: int) -> list:
    """获取想法的所有关联"""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT r.*, 
                      i1.title as idea_1_title,
                      i2.title as idea_2_title
               FROM relations r
               JOIN ideas i1 ON r.idea_id_1 = i1.id
               JOIN ideas i2 ON r.idea_id_2 = i2.id
               WHERE r.idea_id_1 = ? OR r.idea_id_2 = ?""",
            (idea_id, idea_id)
        ).fetchall()
        return rows_to_list(rows)


def get_categories() -> list:
    """获取所有分类"""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT category, COUNT(*) as count 
               FROM ideas 
               WHERE category IS NOT NULL
               GROUP BY category
               ORDER BY count DESC"""
        ).fetchall()
        return rows_to_list(rows)


# === CLI 入口 ===

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_database()
    else:
        print("Usage: python db.py init")
        print(f"Database path: {DB_PATH}")
