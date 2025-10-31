"""
根据 iframes_output.txt 自动填充 updates.json 的 audio_url 字段
"""

import json
import re

# 读取 iframes_output.txt
with open('iframes_output.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 解析歌曲名和对应的 URL
song_urls = {}
current_song = None
current_urls = []

for line in lines:
    line = line.strip()
    
    # 跳过空行
    if not line:
        # 如果有当前歌曲，保存它
        if current_song and current_urls:
            song_urls[current_song] = current_urls
            current_urls = []
        continue
    
    # 如果是 URL（以 http 开头）
    if line.startswith('http'):
        current_urls.append(line)
    else:
        # 保存上一首歌
        if current_song and current_urls:
            song_urls[current_song] = current_urls
        # 开始新歌
        current_song = line
        current_urls = []

# 保存最后一首歌
if current_song and current_urls:
    song_urls[current_song] = current_urls

print(f"从 iframes_output.txt 中提取了 {len(song_urls)} 首歌曲的链接\n")

# 读取 updates.json
with open('updates.json', 'r', encoding='utf-8') as f:
    updates = json.load(f)

# 更新 audio_url
updated_count = 0
not_found = []

for item in updates:
    track_title = item['track_title']
    
    # 移除可能的特殊字符差异（比如全角半角括号）
    normalized_title = track_title.replace('（', '(').replace('）', ')')
    
    # 尝试匹配
    if track_title in song_urls:
        item['audio_url'] = song_urls[track_title]
        updated_count += 1
        print(f"✓ {track_title}: {len(song_urls[track_title])} 个链接")
    elif normalized_title in song_urls:
        item['audio_url'] = song_urls[normalized_title]
        updated_count += 1
        print(f"✓ {track_title}: {len(song_urls[normalized_title])} 个链接")
    else:
        # 尝试模糊匹配（去除空格、特殊符号等）
        found = False
        for song_name, urls in song_urls.items():
            if song_name.replace(' ', '') == track_title.replace(' ', ''):
                item['audio_url'] = urls
                updated_count += 1
                found = True
                print(f"✓ {track_title} (匹配为 {song_name}): {len(urls)} 个链接")
                break
        
        if not found:
            not_found.append(track_title)
            print(f"✗ {track_title}: 未找到匹配")

# 保存更新后的 updates.json
with open('updates.json', 'w', encoding='utf-8') as f:
    json.dump(updates, f, ensure_ascii=False, indent=2)

print(f"\n" + "="*60)
print(f"✅ 已更新 {updated_count} 首歌曲的链接")
print(f"📝 保存到 updates.json")

if not_found:
    print(f"\n❌ 未找到匹配的歌曲 ({len(not_found)} 首):")
    for title in not_found:
        print(f"   - {title}")
else:
    print(f"\n🎉 所有歌曲都已匹配成功！")
