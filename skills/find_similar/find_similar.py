#!/usr/bin/env python3
"""
AgentNote Skill: find_similar
查找相似想法
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
from db import get_idea, search_ideas, init_database, DB_PATH


def find_by_keywords(keywords: list, exclude_id: int = None, limit: int = 5) -> list:
    """基于关键词查找相似想法"""
    all_results = []
    seen_ids = set()
    
    if exclude_id:
        seen_ids.add(exclude_id)
    
    for kw in keywords:
        results = search_ideas(keyword=kw, limit=limit * 2)
        for r in results:
            if r['id'] not in seen_ids:
                seen_ids.add(r['id'])
                all_results.append(r)
    
    return all_results[:limit]


def main():
    if not DB_PATH.exists():
        init_database()
    
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = sys.stdin.read().strip()
    
    if not input_data:
        print(json.dumps({
            "success": False,
            "error": "缺少输入参数"
        }, ensure_ascii=False))
        return
    
    try:
        data = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"JSON 解析失败: {str(e)}"
        }, ensure_ascii=False))
        return
    
    limit = data.get("limit", 5)
    keywords = data.get("keywords", [])
    idea_id = data.get("idea_id")
    
    # 如果提供了 idea_id，从该想法提取关键词
    if idea_id:
        idea = get_idea(idea_id)
        if not idea:
            print(json.dumps({
                "success": False,
                "error": f"未找到 ID={idea_id} 的想法"
            }, ensure_ascii=False))
            return
        
        # 合并关键词
        idea_keywords = idea.get("keywords", [])
        if isinstance(idea_keywords, str):
            idea_keywords = json.loads(idea_keywords)
        keywords = list(set(keywords + idea_keywords))
        
        if idea.get("category"):
            keywords.append(idea["category"])
    
    if not keywords:
        print(json.dumps({
            "success": False,
            "error": "没有可用的关键词进行搜索"
        }, ensure_ascii=False))
        return
    
    try:
        results = find_by_keywords(keywords, exclude_id=idea_id, limit=limit)
        
        print(json.dumps({
            "success": True,
            "search_keywords": keywords,
            "count": len(results),
            "similar_ideas": results
        }, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
