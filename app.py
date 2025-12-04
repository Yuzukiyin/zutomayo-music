from flask import Flask, render_template, jsonify, request
from cs50 import SQL
import json
import os
import random

app = Flask(__name__)

# 配置数据库
db = SQL("sqlite:///music.db")

@app.route('/')
def index():
    """首页 - 显示所有专辑"""
    albums = db.execute("SELECT * FROM albums ORDER BY release_date")
    
    # 检查每个专辑是否有预生成的悬停文本，如果没有则动态生成
    for album in albums:
        if not album.get('hover_texts'):
            album['hover_texts'] = generate_album_hover_text(album['id'])
    
    return render_template('index.html', albums=albums)

def generate_album_hover_text(album_id):
    """为专辑生成悬停文本，从对应歌曲的lyrics文件中随机抽取两行，并标注歌曲名"""
    try:
        # 获取该专辑的所有曲目
        tracks = db.execute(
            "SELECT title FROM tracks WHERE album_id = ? ORDER BY track_number",
            album_id
        )
        
        if not tracks:
            return None
        
        # lyrics 文件夹路径
        lyrics_dir = os.path.join(os.path.dirname(__file__), 'dbupdate', 'lyrics')
        
        # 收集所有可用的歌曲及其内容
        available_tracks = []
        
        # 遍历每首歌曲
        for track in tracks:
            track_title = track['title']
            lyrics_file = os.path.join(lyrics_dir, f"{track_title}.txt")
            
            # 如果歌词文件存在
            if os.path.exists(lyrics_file):
                try:
                    with open(lyrics_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # 过滤空行，保留有内容的行
                        non_empty_lines = [line.strip() for line in lines if line.strip()]
                        if len(non_empty_lines) >= 2:
                            available_tracks.append({
                                'title': track_title,
                                'lines': non_empty_lines
                            })
                except Exception as e:
                    print(f"读取歌词文件失败 {lyrics_file}: {e}")
                    continue
        
        # 如果有可用的歌曲文件
        if available_tracks:
            total_texts = 30  # 总共生成30组悬停文本
            num_tracks = len(available_tracks)
            
            # 计算每首歌应该生成的文本数量
            base_count = total_texts // num_tracks  # 每首歌的基础数量
            remainder = total_texts % num_tracks     # 余数
            
            hover_texts = []
            
            # 为每首歌生成基础数量的文本
            for track_data in available_tracks:
                track_title = track_data['title']
                lines = track_data['lines']
                
                # 为这首歌生成 base_count 组文本
                for _ in range(base_count):
                    if len(lines) >= 2:
                        sample_lines = random.sample(lines, 2)
                        hover_text = '\n'.join(sample_lines) + f'\n——{track_title}'
                        hover_texts.append(hover_text)
            
            # 余数部分随机分配给各首歌
            if remainder > 0:
                # 随机选择 remainder 首歌，每首再生成一组
                random_tracks = random.sample(available_tracks, min(remainder, num_tracks))
                for track_data in random_tracks:
                    track_title = track_data['title']
                    lines = track_data['lines']
                    
                    if len(lines) >= 2:
                        sample_lines = random.sample(lines, 2)
                        hover_text = '\n'.join(sample_lines) + f'\n——{track_title}'
                        hover_texts.append(hover_text)
            
            # 打乱顺序，避免按歌曲顺序显示
            random.shuffle(hover_texts)
            
            # 用 | 分隔多组文本，返回给前端
            return '|'.join(hover_texts) if hover_texts else None
        
        return None
        
    except Exception as e:
        print(f"生成悬停文本失败: {e}")
        return None

@app.route('/album/<int:album_id>')
def album(album_id):
    """专辑详情页 - 显示专辑信息和曲目列表"""
    # 获取专辑信息
    album = db.execute("SELECT * FROM albums WHERE id = ?", album_id)
    if not album:
        return "专辑未找到", 404
    
    # 获取曲目列表
    tracks = db.execute(
        "SELECT * FROM tracks WHERE album_id = ? ORDER BY track_number",
        album_id
    )
    
    return render_template('album.html', album=album[0], tracks=tracks)

@app.route('/track/<int:track_id>')
def track(track_id):
    """单曲详情页 - 显示单曲信息、封面、播放器和歌词"""
    # 获取曲目信息
    track = db.execute("SELECT * FROM tracks WHERE id = ?", track_id)
    if not track:
        return "曲目未找到", 404
    
    # 获取专辑信息（用于显示封面）
    album = db.execute("SELECT * FROM albums WHERE id = ?", track[0]['album_id'])
    
    # 解析 audio_url（支持数组格式的多播放器）
    track_data = track[0]
    if track_data.get('audio_url'):
        try:
            # 尝试解析为 JSON 数组
            parsed = json.loads(track_data['audio_url'])
            track_data['audio_url'] = parsed
        except (json.JSONDecodeError, TypeError):
            # 保持原样（字符串格式，兼容旧数据）
            pass
    
    return render_template('track.html', track=track_data, album=album[0])

@app.route('/api/albums')
def api_albums():
    """API - 获取所有专辑"""
    albums = db.execute("SELECT * FROM albums ORDER BY release_date")
    return jsonify(albums)

@app.route('/api/album/<int:album_id>')
def api_album(album_id):
    """API - 获取指定专辑及其曲目"""
    album = db.execute("SELECT * FROM albums WHERE id = ?", album_id)
    if not album:
        return jsonify({"error": "专辑未找到"}), 404
    
    tracks = db.execute(
        "SELECT * FROM tracks WHERE album_id = ? ORDER BY track_number",
        album_id
    )
    
    return jsonify({
        "album": album[0],
        "tracks": tracks
    })

@app.route('/api/search')
def api_search():
    """API - 搜索专辑和曲目"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    # 搜索专辑(只搜索标题)
    albums = db.execute(
        "SELECT * FROM albums WHERE title LIKE ?",
        f"%{query}%"
    )
    
    # 搜索曲目
    tracks = db.execute(
        "SELECT tracks.*, albums.title as album_title FROM tracks "
        "JOIN albums ON tracks.album_id = albums.id "
        "WHERE tracks.title LIKE ?",
        f"%{query}%"
    )
    
    return jsonify({
        "albums": albums,
        "tracks": tracks
    })


# Vercel 需要的应用实例
application = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
