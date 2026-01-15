#!/usr/bin/env python3
"""
AgentNote Skill: relate_ideas
在知识库中创建想法关联
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
from db import add_relation, get_idea, init_database, DB_PATH


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
    
    idea_id_1 = data.get("idea_id_1")
    idea_id_2 = data.get("idea_id_2")
    
    if not idea_id_1 or not idea_id_2:
        print(json.dumps({
            "success": False,
            "error": "需要 idea_id_1 和 idea_id_2"
        }, ensure_ascii=False))
        return
    
    # 验证两个想法存在
    idea1 = get_idea(idea_id_1)
    idea2 = get_idea(idea_id_2)
    
    if not idea1:
        print(json.dumps({
            "success": False,
            "error": f"未找到 ID={idea_id_1} 的想法"
        }, ensure_ascii=False))
        return
    
    if not idea2:
        print(json.dumps({
            "success": False,
            "error": f"未找到 ID={idea_id_2} 的想法"
        }, ensure_ascii=False))
        return
    
    try:
        relation_id = add_relation(
            idea_id_1=idea_id_1,
            idea_id_2=idea_id_2,
            relation_type=data.get("relation_type", "related"),
            note=data.get("note")
        )
        
        print(json.dumps({
            "success": True,
            "relation_id": relation_id,
            "message": f"✅ 已创建关联: [{idea1['title']}] <-> [{idea2['title']}]"
        }, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
