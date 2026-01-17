#!/usr/bin/env python3
"""
X Bookmarks Export Tool
导出推特书签为 Markdown 格式

支持多种输出格式和筛选条件
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class BookmarkExporter:
    """书签导出器"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def query_bookmarks(
        self,
        limit: int = None,
        since: str = None,
        until: str = None,
        user: str = None,
        lang: str = None,
        search: str = None,
        order: str = 'desc'
    ) -> list:
        """
        查询书签

        Args:
            limit: 最大数量
            since: 开始日期 (YYYY-MM-DD)
            until: 结束日期 (YYYY-MM-DD)
            user: 筛选用户 (screen_name)
            lang: 筛选语言
            search: 全文搜索
            order: 排序方式 (asc/desc)
        """
        conn = self._get_connection()
        try:
            conditions = []
            params = []

            if since:
                conditions.append("date(created_at) >= ?")
                params.append(since)
            if until:
                conditions.append("date(created_at) <= ?")
                params.append(until)
            if user:
                conditions.append("user_screen_name = ?")
                params.append(user)
            if lang:
                conditions.append("lang = ?")
                params.append(lang)
            if search:
                conditions.append("full_text LIKE ?")
                params.append(f"%{search}%")

            where_clause = " AND ".join(conditions) if conditions else "1=1"
            order_dir = "DESC" if order == 'desc' else "ASC"
            limit_clause = f"LIMIT {limit}" if limit else ""

            query = f"""
                SELECT
                    tweet_id, tweet_url, full_text, lang,
                    created_at, user_name, user_screen_name,
                    bookmark_count, favorite_count, retweet_count,
                    reply_count, quote_count, view_count,
                    urls, media, hashtags
                FROM x_bookmarks
                WHERE {where_clause}
                ORDER BY created_at {order_dir}
                {limit_clause}
            """

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def format_markdown_list(self, bookmarks: list, include_stats: bool = False) -> str:
        """
        格式化为简洁的 Markdown 列表
        适合后续 AI 总结
        """
        lines = []
        lines.append(f"# X Bookmarks Export")
        lines.append(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"总计: {len(bookmarks)} 条\n")
        lines.append("---\n")

        for i, bm in enumerate(bookmarks, 1):
            # 基本信息
            user = f"@{bm['user_screen_name']}" if bm['user_screen_name'] else "Unknown"
            date = bm['created_at'][:10] if bm['created_at'] else "Unknown"
            text = bm['full_text'].replace('\n', ' ').strip()

            lines.append(f"## {i}. {user} ({date})")
            lines.append(f"{text}\n")

            # 链接
            if bm['tweet_url']:
                lines.append(f"[原文链接]({bm['tweet_url']})")

            # URLs
            if bm['urls']:
                try:
                    urls = json.loads(bm['urls'])
                    if urls:
                        for url in urls:
                            expanded = url.get('expanded_url', '')
                            if expanded and 'twitter.com' not in expanded and 'x.com' not in expanded:
                                lines.append(f"- [{url.get('display_url', expanded)}]({expanded})")
                except json.JSONDecodeError:
                    pass

            # 统计数据
            if include_stats:
                stats = []
                if bm['view_count']:
                    stats.append(f"👁 {bm['view_count']}")
                if bm['favorite_count']:
                    stats.append(f"❤️ {bm['favorite_count']}")
                if bm['retweet_count']:
                    stats.append(f"🔁 {bm['retweet_count']}")
                if bm['bookmark_count']:
                    stats.append(f"🔖 {bm['bookmark_count']}")
                if stats:
                    lines.append(f"\n{' | '.join(stats)}")

            lines.append("\n---\n")

        return "\n".join(lines)

    def format_compact_list(self, bookmarks: list) -> str:
        """
        格式化为紧凑列表
        每条一行，适合快速浏览
        """
        lines = []
        lines.append(f"# X Bookmarks ({len(bookmarks)} 条)\n")

        for i, bm in enumerate(bookmarks, 1):
            user = f"@{bm['user_screen_name']}" if bm['user_screen_name'] else ""
            date = bm['created_at'][:10] if bm['created_at'] else ""
            text = bm['full_text'].replace('\n', ' ')[:100]
            if len(bm['full_text']) > 100:
                text += "..."
            url = bm['tweet_url'] or ""

            lines.append(f"{i}. [{user}]({url}) {date}")
            lines.append(f"   {text}\n")

        return "\n".join(lines)

    def format_json(self, bookmarks: list) -> str:
        """导出为 JSON 格式"""
        return json.dumps(bookmarks, ensure_ascii=False, indent=2)

    def format_for_summary(self, bookmarks: list) -> str:
        """
        格式化为适合 AI 总结的格式
        只保留核心内容，去除干扰
        """
        lines = []
        lines.append("以下是需要总结的推文列表：\n")

        for i, bm in enumerate(bookmarks, 1):
            user = bm['user_name'] or bm['user_screen_name'] or "Unknown"
            text = bm['full_text'].strip()
            url = bm['tweet_url'] or ""

            lines.append(f"【{i}】{user}")
            lines.append(f"{text}")

            # 提取外部链接
            if bm['urls']:
                try:
                    urls = json.loads(bm['urls'])
                    external_urls = [u['expanded_url'] for u in urls
                                     if u.get('expanded_url') and
                                     'twitter.com' not in u['expanded_url'] and
                                     'x.com' not in u['expanded_url']]
                    if external_urls:
                        lines.append(f"相关链接: {', '.join(external_urls)}")
                except json.JSONDecodeError:
                    pass

            lines.append(f"原文: {url}")
            lines.append("")

        return "\n".join(lines)

    def export(
        self,
        format: str = 'markdown',
        output: str = None,
        **query_args
    ) -> str:
        """
        导出书签

        Args:
            format: 输出格式 (markdown/compact/json/summary)
            output: 输出文件路径，None 则输出到 stdout
            **query_args: 查询参数
        """
        bookmarks = self.query_bookmarks(**query_args)

        if not bookmarks:
            return "没有找到符合条件的书签"

        # 格式化
        if format == 'markdown':
            content = self.format_markdown_list(bookmarks, include_stats=True)
        elif format == 'compact':
            content = self.format_compact_list(bookmarks)
        elif format == 'json':
            content = self.format_json(bookmarks)
        elif format == 'summary':
            content = self.format_for_summary(bookmarks)
        else:
            content = self.format_markdown_list(bookmarks)

        # 输出
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"已导出 {len(bookmarks)} 条书签到 {output}"
        else:
            return content


def main():
    parser = argparse.ArgumentParser(
        description='X 书签导出工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                           # 导出最近20条到默认目录
  %(prog)s -n 10                     # 导出最近 10 条
  %(prog)s --since 2026-01-01        # 导出指定日期后的书签
  %(prog)s --user elonmusk           # 导出指定用户的书签
  %(prog)s --format summary          # 导出为 AI 总结格式
  %(prog)s --stdout                  # 输出到终端而非文件
        """
    )

    # 筛选参数
    parser.add_argument('-n', '--limit', type=int, help='最大导出数量')
    parser.add_argument('--since', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--until', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--user', help='筛选用户 (screen_name)')
    parser.add_argument('--lang', help='筛选语言 (zh/en/ja 等)')
    parser.add_argument('--search', help='全文搜索关键词')
    parser.add_argument('--order', choices=['asc', 'desc'], default='desc',
                        help='排序方式 (默认: desc 最新优先)')

    # 输出参数
    parser.add_argument('-f', '--format',
                        choices=['markdown', 'compact', 'json', 'summary'],
                        default='summary',
                        help='输出格式 (默认: summary)')
    parser.add_argument('-o', '--output', help='输出文件路径 (默认: data/exports/bookmarks-日期.md)')
    parser.add_argument('--stdout', action='store_true', help='输出到终端而非文件')

    # 数据库路径
    parser.add_argument('--db', help='数据库路径')

    args = parser.parse_args()

    # 确定数据库路径
    if args.db:
        db_path = args.db
    else:
        script_dir = Path(__file__).parent
        db_path = str(script_dir / '../data/agentnote.db')

    if not os.path.exists(db_path):
        print(f"错误: 数据库不存在: {db_path}")
        sys.exit(1)

    # 确定输出路径
    output_path = args.output
    if not args.stdout and not output_path:
        # 默认输出到 data/exports/ 目录
        exports_dir = script_dir / '../data/exports'
        exports_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')
        output_path = str(exports_dir / f'bookmarks-{timestamp}.md')

    # 创建导出器
    exporter = BookmarkExporter(db_path)

    # 设置默认 limit
    limit = args.limit if args.limit else 20

    # 执行导出
    result = exporter.export(
        format=args.format,
        output=None if args.stdout else output_path,
        limit=limit,
        since=args.since,
        until=args.until,
        user=args.user,
        lang=args.lang,
        search=args.search,
        order=args.order
    )

    print(result)


if __name__ == '__main__':
    main()
