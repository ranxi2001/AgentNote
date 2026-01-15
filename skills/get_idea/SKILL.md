---
name: get_idea
description: 获取 AgentNote 知识库中的单条想法详情。
---

# Get Idea Skill

获取指定 ID 的想法详情。

## 输入格式

```json
{
  "id": 1
}
```

或直接传入 ID 数字。

## 使用方法

```bash
cd /home/AgentNote
python skills/get_idea/get_idea.py '{"id": 1}'
python skills/get_idea/get_idea.py 1
```
