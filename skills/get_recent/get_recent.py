#!/usr/bin/env python3
"""
AgentNote Skill: get_recent
获取最近添加的想法
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
from db import get_recent_ideas, init_database, DB_PATH


def main():
    if not DB_PATH.exists():
        init_database()
    
    limit = 10  # 默认
    
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = sys.stdin.read().strip()
    
    if input_data:
        try:
            if input_data.isdigit():
                limit = int(input_data)
            else:
                data = json.loads(input_data)
                limit = data.get("limit", 10)
        except (json.JSONDecodeError, ValueError):
            pass
    
    try:
        results = get_recent_ideas(limit=limit)
        
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
