---
name: format_to_markdown
description: Convert raw text, notes, or unstructured content into well-formatted Markdown documents. Use when user pastes text and wants it organized, formatted, or cleaned up for storage.
---

# Format to Markdown Skill

**Core Skill**: Transform unstructured text into clean, well-organized Markdown documents.

## When to Use

- User pastes raw text, notes, or copied content
- User says "format this", "organize this", "clean this up"
- User wants to save messy notes as structured documents
- Content needs proper headings, lists, code blocks

## Formatting Rules

### 1. Structure Analysis

First, identify the content type:
- **Tutorial/Guide**: Use numbered steps, code blocks
- **Notes/Ideas**: Use bullet points, short paragraphs
- **Technical Doc**: Use headings hierarchy, code examples
- **Article/Blog**: Use paragraphs, blockquotes, emphasis

### 2. Markdown Elements to Use

```markdown
# Main Title (H1) - only one per document

## Section Heading (H2)

### Subsection (H3)

**Bold** for important terms
*Italic* for emphasis
`inline code` for commands, functions, file names

- Bullet lists for unordered items
1. Numbered lists for steps/sequences

> Blockquotes for citations or callouts

```language
code blocks for multi-line code
```

[Link text](url) for references
![Alt text](image-url) for images
```

### 3. Content Enhancement

- Add appropriate headings to organize sections
- Convert run-on text into bullet points where appropriate
- Wrap code/commands in code blocks with language hints
- Add blank lines between sections for readability
- Preserve original meaning while improving clarity

## Output Format

After formatting, provide JSON for `save_doc`:

```json
{
  "title": "Extracted or generated title",
  "content": "# Full Markdown Content\n\n...",
  "category": "Suggested category",
  "tags": ["relevant", "tags"],
  "summary": "Brief 1-2 sentence summary"
}
```

## Categories Reference

Common categories to use:
- **Tech**: Programming, tools, software
- **AI**: Machine learning, LLMs, agents
- **DevOps**: Deployment, infrastructure, CI/CD
- **Notes**: General notes, ideas, thoughts
- **Tutorial**: How-to guides, learning materials
- **Reference**: Documentation, API references

## Example

**Input** (raw text):
```
python虚拟环境管理 用venv创建 python -m venv myenv 激活的话windows是myenv\Scripts\activate linux是source myenv/bin/activate 退出用deactivate 删除直接删文件夹就行
```

**Output** (formatted):
```json
{
  "title": "Python Virtual Environment Management",
  "content": "# Python Virtual Environment Management\n\nManage isolated Python environments using `venv`.\n\n## Create Environment\n\n```bash\npython -m venv myenv\n```\n\n## Activate\n\n**Windows:**\n```cmd\nmyenv\\Scripts\\activate\n```\n\n**Linux/macOS:**\n```bash\nsource myenv/bin/activate\n```\n\n## Deactivate\n\n```bash\ndeactivate\n```\n\n## Delete\n\nSimply delete the environment folder:\n```bash\nrm -rf myenv\n```",
  "category": "Tech",
  "tags": ["python", "venv", "virtual-environment"],
  "summary": "Quick reference for creating, activating, and managing Python virtual environments using venv."
}
```

## Workflow

1. Receive raw text from user
2. Analyze content structure and type
3. Apply appropriate markdown formatting
4. Generate title, category, tags
5. Output JSON ready for `save_doc` skill
