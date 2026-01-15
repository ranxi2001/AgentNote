#!/usr/bin/env python3
"""
AgentNote Skill: delete_idea
删除知识库中的想法
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
from db import delete_idea, get_idea, init_database, DB_PATH


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
            "error": "缺少 ID 参数"
        }, ensure_ascii=False))
        return
    
    try:
        if input_data.isdigit():
            idea_id = int(input_data)
        else:
            data = json.loads(input_data)
            idea_id = data.get("id")
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({
            "success": False,
            "error": "无效的 ID 格式"
        }, ensure_ascii=False))
        return
    
    # 先获取想法信息用于确认
    idea = get_idea(idea_id)
    if not idea:
        print(json.dumps({
            "success": False,
            "error": f"未找到 ID={idea_id} 的想法"
        }, ensure_ascii=False))
        return
    
    try:
        success = delete_idea(idea_id)
        
        print(json.dumps({
            "success": True,
            "message": f"✅ 已删除想法: {idea['title']}",
            "deleted_idea": idea
        }, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
