---
name: relate_ideas
description: 在 AgentNote 知识库中创建想法之间的关联关系。
---

# Relate Ideas Skill

建立两个想法之间的关联。

## 输入格式

```json
{
  "idea_id_1": 1,
  "idea_id_2": 2,
  "relation_type": "related",
  "note": "关联说明（可选）"
}
```

**relation_type 可选值**:
- `related` - 相关
- `parent` - 父子关系
- `inspired_by` - 启发来源
- `contradict` - 矛盾/对立

## 使用方法

```bash
cd /home/AgentNote
python skills/relate_ideas/relate_ideas.py '{"idea_id_1":1,"idea_id_2":2}'
```
