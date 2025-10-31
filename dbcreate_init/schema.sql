-- 数据库结构定义文件
-- 此文件只包含表结构,数据由 init_db.py 插入

-- 专辑表
CREATE TABLE albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    release_date TEXT,
    cover_image TEXT
);

-- 曲目表
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL,
    track_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    duration TEXT,
    audio_url TEXT,  -- 音频文件链接（需要填充实际链接）
    lyrics TEXT,     -- 歌词内容（需要填充实际歌词，每行用 \n 分隔）
    FOREIGN KEY (album_id) REFERENCES albums(id)
);
