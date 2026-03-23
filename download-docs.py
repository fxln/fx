#!/usr/bin/env python3
"""
OpenClaw 文档下载脚本
从 https://docs.openclaw.ai/llms.txt 获取所有文档并保存到本地
"""

import os
import sys
import time
import urllib.request
from urllib.parse import urlparse

# 文档索引 URL
INDEX_URL = "https://docs.openclaw.ai/llms.txt"

# 保存目录
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openclaw-docs")

def get_index():
    """获取文档索引"""
    print(f"获取文档索引: {INDEX_URL}")
    try:
        with urllib.request.urlopen(INDEX_URL, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"获取索引失败: {e}")
        return None

def extract_urls(index_content):
    """从索引内容中提取所有文档 URL"""
    urls = []
    lines = index_content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('- [') and '](' in line:
            # 提取括号中的 URL
            start = line.find('](') + 2
            end = line.find(')', start)
            if start > 0 and end > start:
                url = line[start:end]
                if url.startswith('http'):
                    urls.append(url)
    return urls

def download_document(url, save_path):
    """下载单个文档"""
    print(f"下载: {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 保存文件
            with open(save_path, 'wb') as f:
                f.write(content)
            
            print(f"  已保存: {save_path}")
            return True
    except Exception as e:
        print(f"  下载失败: {e}")
        return False

def url_to_path(url):
    """将 URL 转换为本地文件路径"""
    parsed = urlparse(url)
    path = parsed.path
    
    # 移除开头的斜杠
    if path.startswith('/'):
        path = path[1:]
    
    # 如果是空路径，使用 index.md
    if not path:
        path = 'index.md'
    
    # 如果没有扩展名，添加 .md
    if '.' not in os.path.basename(path):
        path = path + '.md'
    
    return os.path.join(SAVE_DIR, path)

def main():
    """主函数"""
    print("=" * 60)
    print("OpenClaw 文档下载器")
    print("=" * 60)
    
    # 获取索引
    index_content = get_index()
    if not index_content:
        print("无法获取文档索引，退出")
        return 1
    
    # 提取 URL
    urls = extract_urls(index_content)
    print(f"\n找到 {len(urls)} 个文档")
    
    if not urls:
        print("没有找到文档 URL")
        return 1
    
    # 确保保存目录存在
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    # 下载每个文档
    success_count = 0
    fail_count = 0
    
    print(f"\n开始下载文档到: {SAVE_DIR}")
    print("-" * 60)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]", end=" ")
        
        save_path = url_to_path(url)
        
        if download_document(url, save_path):
            success_count += 1
        else:
            fail_count += 1
        
        # 避免请求太快
        time.sleep(0.5)
    
    # 总结
    print("\n" + "-" * 60)
    print(f"\n下载完成!")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print(f"  保存目录: {SAVE_DIR}")
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

