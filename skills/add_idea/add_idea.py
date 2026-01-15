#!/usr/bin/env python3
"""
AgentNote Skill: add_idea
添加新想法到知识库
"""

import sys
import json
from pathlib import Path

# 添加 utils 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
from db import add_idea, init_database, DB_PATH


def main():
    # 确保数据库存在
    if not DB_PATH.exists():
        init_database()
    
    # 读取输入
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = sys.stdin.read().strip()
    
    if not input_data:
        print(json.dumps({
            "success": False,
            "error": "缺少输入数据"
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
    
    # 验证必填字段
    if not data.get("title") or not data.get("content"):
        print(json.dumps({
            "success": False,
            "error": "title 和 content 是必填字段"
        }, ensure_ascii=False))
        return
    
    # 添加到数据库
    try:
        idea_id = add_idea(
            title=data["title"],
            content=data["content"],
            category=data.get("category"),
            keywords=data.get("keywords", []),
            source=data.get("source", "chat")
        )
        
        print(json.dumps({
            "success": True,
            "id": idea_id,
            "message": f"✅ 想法已保存，ID: {idea_id}"
        }, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
