#!/usr/bin/env python3
"""
AgentNote Skill: format_thought
格式化零碎想法为结构化 JSON

注意：此脚本主要用于演示和验证。
实际使用时，格式化工作由 Claude 在对话中完成，
然后调用 add_idea 入库。
"""

import sys
import json
import re


def extract_basic_info(text: str) -> dict:
    """
    基础的本地格式化（无 LLM）
    实际场景下这部分由 Claude 完成
    """
    # 清理文本
    text = text.strip()
    
    # 简单提取标题（取前20字符或第一句）
    first_line = text.split('\n')[0][:50]
    title = first_line[:20] + "..." if len(first_line) > 20 else first_line
    
    # 简单关键词提取（基于常见词过滤）
    words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', text)
    stopwords = {'的', '是', '了', '在', '有', '和', '与', '这', '那', '我', '你', 'the', 'a', 'an', 'is', 'are'}
    keywords = list(set(w for w in words if len(w) > 1 and w.lower() not in stopwords))[:5]
    
    return {
        "title": title,
        "category": "未分类",
        "keywords": keywords,
        "content": text,
        "suggested_relations": [],
        "_note": "此为基础本地格式化，建议让 Claude 重新分析以获得更好的结构化结果"
    }


def main():
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
    else:
        input_text = sys.stdin.read().strip()
    
    if not input_text:
        print(json.dumps({
            "success": False,
            "error": "缺少输入文本"
        }, ensure_ascii=False))
        return
    
    try:
        result = extract_basic_info(input_text)
        
        print(json.dumps({
            "success": True,
            "formatted": result,
            "prompt_template": """请将以下想法格式化为 JSON:

用户输入: {input}

输出格式:
{{
  "title": "简短标题（10字以内）",
  "category": "分类",
  "keywords": ["关键词"],
  "content": "整理后的描述"
}}""".format(input=input_text)
        }, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
