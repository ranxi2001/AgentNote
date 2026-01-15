#!/usr/bin/env python3
"""
AgentNote Skill: summarize_category
获取分类下的想法用于总结
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
from db import search_ideas, get_categories, init_database, DB_PATH


def main():
    if not DB_PATH.exists():
        init_database()
    
    category = None
    
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = sys.stdin.read().strip()
    
    if input_data:
        try:
            data = json.loads(input_data)
            category = data.get("category")
        except json.JSONDecodeError:
            category = input_data
    
    try:
        if category:
            # 获取指定分类的想法
            results = search_ideas(category=category, limit=100)
            
            print(json.dumps({
                "success": True,
                "category": category,
                "count": len(results),
                "ideas": results,
                "summary_prompt": f"请根据以下 {len(results)} 条关于「{category}」的想法，生成一份总结报告。"
            }, ensure_ascii=False, indent=2))
        else:
            # 返回所有分类统计
            categories = get_categories()
            
            print(json.dumps({
                "success": True,
                "categories": categories,
                "total_categories": len(categories)
            }, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
