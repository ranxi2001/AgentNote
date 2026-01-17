#!/usr/bin/env python3
"""
Save Document to Knowledge Base
保存文档到知识库
"""

import argparse
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    """生成 URL 友好的 slug"""
    # 转小写，替换空格和特殊字符
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    # 添加时间戳确保唯一
    timestamp = datetime.now().strftime('%Y%m%d')
    return f"{text[:50]}-{timestamp}" if text else f"doc-{timestamp}"


def save_document(
    db_path: str,
    title: str,
    content: str,
    category: str = None,
    summary: str = None,
    source: str = 'chat',
    tags: list = None,
    slug: str = None
) -> dict:
    """
    保存文档到知识库

    Returns:
        包含保存结果的字典
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        # 生成 slug
        if not slug:
            slug = slugify(title)

        # 检查 slug 是否已存在
        cursor = conn.execute("SELECT id FROM documents WHERE slug = ?", (slug,))
        existing = cursor.fetchone()

        if existing:
            # 更新现有文档
            conn.execute("""
                UPDATE documents
                SET title = ?, content = ?, category = ?, summary = ?,
                    source = ?, updated_at = CURRENT_TIMESTAMP
                WHERE slug = ?
            """, (title, content, category, summary, source, slug))
            doc_id = existing['id']
            action = 'updated'
        else:
            # 插入新文档
            cursor = conn.execute("""
                INSERT INTO documents (slug, title, content, category, summary, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (slug, title, content, category, summary, source))
            doc_id = cursor.lastrowid
            action = 'created'

        # 处理标签
        if tags:
            # 删除现有标签关联
            conn.execute("DELETE FROM document_tags WHERE document_id = ?", (doc_id,))

            for tag_name in tags:
                tag_name = tag_name.strip().lower()
                if not tag_name:
                    continue

                # 获取或创建标签
                cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                tag_row = cursor.fetchone()

                if tag_row:
                    tag_id = tag_row['id']
                else:
                    cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                    tag_id = cursor.lastrowid

                # 创建关联
                conn.execute(
                    "INSERT OR IGNORE INTO document_tags (document_id, tag_id) VALUES (?, ?)",
                    (doc_id, tag_id)
                )

        conn.commit()

        return {
            'success': True,
            'action': action,
            'doc_id': doc_id,
            'slug': slug,
            'title': title
        }

    except Exception as e:
        conn.rollback()
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='保存文档到知识库',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --title "AI 总结" --content "内容..." --category twitter
  %(prog)s --title "笔记" --content-file notes.md --tags "ai,学习"
  echo "内容" | %(prog)s --title "标题" --stdin
        """
    )

    parser.add_argument('--title', '-t', required=True, help='文档标题')
    parser.add_argument('--content', '-c', help='文档内容 (Markdown)')
    parser.add_argument('--content-file', '-f', help='从文件读取内容')
    parser.add_argument('--stdin', action='store_true', help='从 stdin 读取内容')
    parser.add_argument('--category', help='分类')
    parser.add_argument('--summary', help='摘要')
    parser.add_argument('--source', default='chat', help='来源 (默认: chat)')
    parser.add_argument('--tags', help='标签，逗号分隔')
    parser.add_argument('--slug', help='自定义 slug')
    parser.add_argument('--db', help='数据库路径')

    args = parser.parse_args()

    # 确定内容来源
    content = None
    if args.stdin:
        content = sys.stdin.read()
    elif args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        print("错误: 必须提供内容 (--content, --content-file 或 --stdin)")
        sys.exit(1)

    # 确定数据库路径
    if args.db:
        db_path = args.db
    else:
        script_dir = Path(__file__).parent
        db_path = str(script_dir / '../data/agentnote.db')

    if not os.path.exists(db_path):
        print(f"错误: 数据库不存在: {db_path}")
        sys.exit(1)

    # 解析标签
    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(',')]

    # 保存文档
    result = save_document(
        db_path=db_path,
        title=args.title,
        content=content,
        category=args.category,
        summary=args.summary,
        source=args.source,
        tags=tags,
        slug=args.slug
    )

    if result['success']:
        print(f"✓ 文档已{result['action']}: {result['title']}")
        print(f"  ID: {result['doc_id']}")
        print(f"  Slug: {result['slug']}")
    else:
        print(f"✗ 保存失败: {result['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
