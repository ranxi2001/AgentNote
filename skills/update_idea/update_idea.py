#!/usr/bin/env python3
"""
AgentNote Skill: update_idea
更新知识库中的想法
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
from db import update_idea, get_idea, init_database, DB_PATH


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
    
    idea_id = data.get("id")
    if not idea_id:
        print(json.dumps({
            "success": False,
            "error": "缺少 id 参数"
        }, ensure_ascii=False))
        return
    
    # 移除 id，剩余的就是要更新的字段
    update_data = {k: v for k, v in data.items() if k != "id"}
    
    if not update_data:
        print(json.dumps({
            "success": False,
            "error": "没有提供要更新的字段"
        }, ensure_ascii=False))
        return
    
    try:
        success = update_idea(idea_id, **update_data)
        
        if success:
            updated = get_idea(idea_id)
            print(json.dumps({
                "success": True,
                "message": f"✅ 想法 ID={idea_id} 已更新",
                "idea": updated
            }, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({
                "success": False,
                "error": f"未找到 ID={idea_id} 的想法"
            }, ensure_ascii=False))
            
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
