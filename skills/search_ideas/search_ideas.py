#!/usr/bin/env python3
"""
AgentNote Skill: search_ideas
搜索知识库中的想法
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
from db import search_ideas, init_database, DB_PATH


def main():
    if not DB_PATH.exists():
        init_database()
    
    # 读取输入
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = sys.stdin.read().strip()
    
    # 默认参数
    keyword = None
    category = None
    limit = 20
    
    if input_data:
        try:
            data = json.loads(input_data)
            keyword = data.get("keyword")
            category = data.get("category")
            limit = data.get("limit", 20)
        except json.JSONDecodeError:
            # 如果不是 JSON，当作关键词处理
            keyword = input_data
    
    try:
        results = search_ideas(
            keyword=keyword,
            category=category,
            limit=limit
        )
        
        print(json.dumps({
            "success": True,
            "count": len(results),
            "results": results
        }, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
