---
name: get_recent
description: 获取 AgentNote 知识库中最近添加的想法列表。
---

# Get Recent Skill

快速查看最近记录的想法。

## 输入格式

```json
{
  "limit": 10
}
```

或直接传入数字表示数量。

## 使用方法

```bash
cd /home/AgentNote
python skills/get_recent/get_recent.py 5
python skills/get_recent/get_recent.py '{"limit": 10}'
```
