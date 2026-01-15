---
name: find_similar
description: 在 AgentNote 知识库中查找与指定想法相似的其他想法。
---

# Find Similar Skill

基于关键词查找相似想法。

## 输入格式

```json
{
  "idea_id": 1,
  "limit": 5
}
```

或者直接提供关键词：
```json
{
  "keywords": ["AI", "生产力"],
  "limit": 5
}
```

## 使用方法

```bash
cd /home/AgentNote
python skills/find_similar/find_similar.py '{"idea_id": 1}'
python skills/find_similar/find_similar.py '{"keywords": ["AI"]}'
```
