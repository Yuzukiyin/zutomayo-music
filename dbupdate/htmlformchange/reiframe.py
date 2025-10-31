"""
批量提取多平台 iframe 嵌入链接（YouTube、网易云音乐、Bilibili）

用法：
1. 把所有 iframe 代码放在 iframes_input.txt 中（每行一个或多个）
2. 运行脚本：python reiframe.py
3. 清理后的链接会保存在 iframes_output.txt 中

支持平台：
- YouTube (youtube.com / youtube-nocookie.com)
- 网易云音乐 (music.163.com)
- Bilibili (player.bilibili.com)
"""

import re
import sys

def extract_youtube_urls(text):
    """提取 YouTube 嵌入链接（完整保留所有参数）"""
    # 匹配完整的 src 属性内容
    pattern = r'src=["\']?((?:https?:)?//(?:www\.)?youtube(?:-nocookie)?\.com/embed/[^"\'>\s]+)["\']?'
    matches = re.findall(pattern, text)
    urls = []
    for url in matches:
        # 补全协议
        if url.startswith('//'):
            url = 'https:' + url
        urls.append(url)
    return urls

def extract_netease_urls(text):
    """提取网易云音乐嵌入链接（完整保留所有参数）"""
    pattern = r'src=["\']?((?:https?:)?//music\.163\.com/outchain/player\?[^"\'>\s]+)["\']?'
    matches = re.findall(pattern, text)
    urls = []
    for url in matches:
        # 补全协议
        if url.startswith('//'):
            url = 'https:' + url
        urls.append(url)
    return urls

def extract_bilibili_urls(text):
    """提取 Bilibili 嵌入链接（完整保留所有参数）"""
    pattern = r'src=["\']?((?:https?:)?//player\.bilibili\.com/player\.html\?[^"\'>\s]+)["\']?'
    matches = re.findall(pattern, text)
    urls = []
    for url in matches:
        # 补全协议
        if url.startswith('//'):
            url = 'https:' + url
        urls.append(url)
    return urls

def extract_all_urls(text):
    """提取所有支持平台的链接"""
    all_urls = []
    
    # YouTube
    youtube_urls = extract_youtube_urls(text)
    all_urls.extend([("YouTube", url) for url in youtube_urls])
    
    # 网易云音乐
    netease_urls = extract_netease_urls(text)
    all_urls.extend([("网易云", url) for url in netease_urls])
    
    # Bilibili
    bilibili_urls = extract_bilibili_urls(text)
    all_urls.extend([("Bilibili", url) for url in bilibili_urls])
    
    return all_urls


def process_file(input_file="iframes_input.txt", output_file="iframes_output.txt"):
    """批量处理文件，保留专辑名、歌曲名和空行"""
    try:
        # 读取输入文件（按行处理）
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        output_lines = []
        total_urls = 0
        
        for line in lines:
            line_stripped = line.strip()
            
            # 空行直接保留
            if not line_stripped:
                output_lines.append("\n")
                continue
            
            # HTML 注释行跳过
            if line_stripped.startswith('<!--'):
                continue
            
            # 如果这一行不包含 iframe，可能是专辑名或歌曲名，直接保留
            if '<iframe' not in line_stripped:
                output_lines.append(line)
                continue
            
            # 提取这一行中的所有链接
            url_pairs = extract_all_urls(line_stripped)
            
            if url_pairs:
                # 每个链接单独一行
                for platform, url in url_pairs:
                    output_lines.append(url + "\n")
                    total_urls += 1
        
        if total_urls == 0:
            print(f"❌ 未在 {input_file} 中找到任何支持的嵌入链接")
            print("支持的平台：YouTube、网易云音乐、Bilibili")
            return
        
        # 写入输出文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.writelines(output_lines)
        
        print(f"✅ 成功处理 {total_urls} 个链接")
        print(f"📥 输入文件: {input_file}")
        print(f"📤 输出文件: {output_file}")
        print(f"✓ 已保留专辑名、歌曲名和空行格式")
        
        # 统计平台数量
        platform_counts = {}
        for line in output_lines:
            line_stripped = line.strip()
            if 'youtube.com' in line_stripped or 'youtube-nocookie.com' in line_stripped:
                platform_counts['YouTube'] = platform_counts.get('YouTube', 0) + 1
            elif 'music.163.com' in line_stripped:
                platform_counts['网易云'] = platform_counts.get('网易云', 0) + 1
            elif 'bilibili.com' in line_stripped:
                platform_counts['Bilibili'] = platform_counts.get('Bilibili', 0) + 1
        
        print(f"\n平台统计：")
        for platform, count in platform_counts.items():
            print(f"  {platform}: {count} 个")
    
    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 {input_file}")
        print(f"请创建 {input_file} 并在其中粘贴 iframe 代码（每行一个或多个）")
        
        # 创建示例输入文件
        with open(input_file, "w", encoding="utf-8") as f:
            f.write('''<!-- 示例：把你的 iframe 代码粘贴在这里，支持多平台 -->

<!-- YouTube 示例 -->
<iframe src="https://www.youtube-nocookie.com/embed/GJI4Gv7NbmE?si=xxx&amp;controls=0"></iframe>

<!-- 网易云音乐示例 -->
<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=330 height=86 src="//music.163.com/outchain/player?type=2&id=1467858858&auto=0&height=66"></iframe>

<!-- Bilibili 示例 -->
<iframe src="//player.bilibili.com/player.html?isOutside=true&aid=574197402&bvid=BV15z4y1s7G7&cid=1218233981&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>

<!-- 把你的实际 iframe 粘贴到下面 -->
''')
        print(f"✅ 已创建示例文件 {input_file}，请编辑后重新运行脚本")
    
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 可以通过命令行参数自定义文件名
    input_file = sys.argv[1] if len(sys.argv) > 1 else "iframes_input.txt"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "iframes_output.txt"
    
    process_file(input_file, output_file)