#!/usr/bin/env python3
"""
启动文件合规检查脚本
检查AGENTS.md、SOUL.md、PROFILE.md、MEMORY.md的合规性
"""
import os
import re
import sys
import yaml
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Optional


# 文件长度限制（不含frontmatter）
LENGTH_LIMITS = {
    "AGENTS.md": 60,
    "SOUL.md": 80,
    "PROFILE.md": 50,
    "MEMORY.md": 150,
}

# 各文件必需的章节
REQUIRED_SECTIONS = {
    "AGENTS.md": ["安全", "记忆管理", "常用 Skill"],
    "SOUL.md": ["核心准则", "边界"],
    "PROFILE.md": ["用户资料"],
    "MEMORY.md": [],
}

# 禁止的格式元素
FORBIDDEN_PATTERNS = {
    "emoji": re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]'),
    "mermaid": re.compile(r'```mermaid\s', re.IGNORECASE),
    "long_code_block": re.compile(r'```[\s\S]{300,}?```'),
}


def parse_frontmatter(content: str) -> Tuple[Optional[dict], str]:
    """解析frontmatter元数据"""
    if not content.startswith("---"):
        return None, content
    
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return None, content
    
    yaml_str = content[3:end_idx].strip()
    try:
        metadata = yaml.safe_load(yaml_str)
        body = content[end_idx + 3:].strip()
        return metadata, body
    except yaml.YAMLError:
        return None, content


def count_lines(text: str) -> int:
    """计算行数（排除空行）"""
    return len([line for line in text.split('\n') if line.strip()])


def extract_sections(text: str) -> List[str]:
    """提取Markdown标题"""
    headers = []
    for line in text.split('\n'):
        if line.startswith('##'):
            header = line.lstrip('#').strip()
            headers.append(header)
    return headers


def find_emoji(text: str) -> List[str]:
    """查找emoji"""
    return FORBIDDEN_PATTERNS["emoji"].findall(text)


def find_mermaid(text: str) -> bool:
    """检查是否包含mermaid"""
    return bool(FORBIDDEN_PATTERNS["mermaid"].search(text))


def find_long_code_blocks(text: str) -> List[int]:
    """查找超过5行的代码块"""
    blocks = []
    in_block = False
    line_count = 0
    for line in text.split('\n'):
        if line.strip().startswith('```'):
            if in_block:
                if line_count > 5:
                    blocks.append(line_count)
                in_block = False
                line_count = 0
            else:
                in_block = True
                line_count = 0
        elif in_block:
            line_count += 1
    return blocks


def find_duplicate_sentences(text: str) -> List[str]:
    """查找重复的句子"""
    sentences = re.split(r'[。！？\n]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    counter = Counter(sentences)
    return [s for s, count in counter.items() if count > 1]


def audit_file(file_path: str) -> Dict:
    """审计单个文件"""
    result = {
        "file": os.path.basename(file_path),
        "path": file_path,
        "exists": os.path.exists(file_path),
        "errors": [],
        "warnings": [],
        "info": [],
    }
    
    if not result["exists"]:
        result["errors"].append("文件不存在")
        return result
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 解析frontmatter
    metadata, body = parse_frontmatter(content)
    
    if metadata is None:
        result["errors"].append("缺少frontmatter元数据")
    else:
        if "summary" not in metadata:
            result["errors"].append("缺少summary字段")
        if "read_when" not in metadata:
            result["errors"].append("缺少read_when字段")
    
    # 2. 检查文件长度
    line_count = count_lines(body)
    filename = os.path.basename(file_path)
    limit = LENGTH_LIMITS.get(filename, 150)
    result["info"].append(f"当前行数：{line_count}（上限{limit}）")
    
    if line_count > limit:
        result["warnings"].append(f"文件过长：{line_count}行，超过限制{limit}行")
    
    # 3. 检查必需章节
    sections = extract_sections(body)
    required = REQUIRED_SECTIONS.get(filename, [])
    for req in required:
        if not any(req in s for s in sections):
            result["warnings"].append(f"缺少必需章节：{req}")
    
    result["info"].append(f"章节：{', '.join(sections) if sections else '无'}")
    
    # 4. 检查禁止格式（AGENTS/SOUL/PROFILE检查，MEMORY跳过）
    if filename != "MEMORY.md":
        emojis = find_emoji(body)
        if emojis:
            result["warnings"].append(f"包含emoji：{len(emojis)}个")
        
        if find_mermaid(body):
            result["warnings"].append("包含mermaid图表（启动文件禁止）")
        
        long_blocks = find_long_code_blocks(body)
        if long_blocks:
            result["warnings"].append(f"包含超长代码块：{len(long_blocks)}个（超过5行）")
    
    # 5. 检查重复内容
    duplicates = find_duplicate_sentences(body)
    if duplicates:
        result["warnings"].append(f"可能存在重复内容：{len(duplicates)}处")
    
    return result


def format_report(results: List[Dict]) -> str:
    """格式化审计报告"""
    lines = []
    lines.append("=" * 50)
    lines.append("启动文件合规检查报告")
    lines.append("=" * 50)
    
    for r in results:
        lines.append("")
        lines.append(f"【{r['file']}】")
        
        if not r["exists"]:
            lines.append("  状态：不存在")
            continue
        
        # 统计
        errors = len(r["errors"])
        warnings = len(r["warnings"])
        
        if errors == 0 and warnings == 0:
            lines.append("  状态：合规")
        elif errors > 0:
            lines.append(f"  状态：不合规（{errors}个错误，{warnings}个警告）")
        else:
            lines.append(f"  状态：有警告（{warnings}个）")
        
        # 信息
        for info in r["info"]:
            lines.append(f"  信息：{info}")
        
        # 错误
        for err in r["errors"]:
            lines.append(f"  错误：{err}")
        
        # 警告
        for warn in r["warnings"]:
            lines.append(f"  警告：{warn}")
    
    lines.append("")
    lines.append("=" * 50)
    
    # 汇总
    total_errors = sum(len(r["errors"]) for r in results)
    total_warnings = sum(len(r["warnings"]) for r in results)
    
    if total_errors == 0 and total_warnings == 0:
        lines.append("结论：所有启动文件合规")
    else:
        lines.append(f"结论：共{total_errors}个错误，{total_warnings}个警告")
    
    return "\n".join(lines)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python audit_startup_files.py <workspace_dir>")
        print("示例: python audit_startup_files.py C:\\Users\\xxx\\.qwenpaw\\workspaces\\my_agent")
        sys.exit(1)
    
    workspace = sys.argv[1]
    
    files_to_check = [
        "AGENTS.md",
        "SOUL.md",
        "PROFILE.md",
        "MEMORY.md",
    ]
    
    results = []
    for filename in files_to_check:
        file_path = os.path.join(workspace, filename)
        result = audit_file(file_path)
        results.append(result)
    
    report = format_report(results)
    print(report)
    
    # 返回非零退出码如果有错误
    if any(r["errors"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
