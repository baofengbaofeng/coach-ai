#!/usr/bin/env python3
"""
修复pydantic模型文件，移除Field使用
"""

import re
import os

def fix_model_file(filepath):
    """修复模型文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复各种Field模式
    patterns = [
        # : type = Field(..., description="...")
        (r':\s*([a-zA-Z_][a-zA-Z0-9_\[\], ]*)\s*=\s*Field\(\.\.\.[^)]*\)', r': \1'),
        
        # : Optional[type] = Field(None, description="...")
        (r':\s*Optional\[([a-zA-Z_][a-zA-Z0-9_\[\], ]*)\]\s*=\s*Field\(None[^)]*\)', r': Optional[\1] = None'),
        
        # : type = Field(default_factory=..., description="...")
        (r':\s*([a-zA-Z_][a-zA-Z0-9_\[\], ]*)\s*=\s*Field\(default_factory=[^)]*\)', r': \1'),
        
        # : List[type] = Field(default_factory=list, description="...")
        (r':\s*List\[([a-zA-Z_][a-zA-Z0-9_\[\], ]*)\]\s*=\s*Field\(default_factory=list[^)]*\)', r': List[\1] = []'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed: {filepath}")

def main():
    """主函数"""
    # 修复所有模块的models.py文件
    modules_dir = "coding/tornado/modules"
    
    for root, dirs, files in os.walk(modules_dir):
        for file in files:
            if file == "models.py":
                filepath = os.path.join(root, file)
                fix_model_file(filepath)

if __name__ == "__main__":
    main()