# 曲目元数据更新指南

快速上手：使用 `update_track_meta.py` 批量更新 tracks 表的 audio_url 和 lyrics。

---

## 📋 基本流程（推荐）

### 1️⃣ 准备更新数据

编辑 `updates.json`（参考 `updates_template.json` 的格式）：

```json
[
  {
    "id": 1,
    "audio_url": "https://www.youtube.com/embed/xxxxx",
    "lyrics_file": "lyrics/秒針を噛む.txt"
  },
  {
    "album_title": "潜潜话",
    "track_title": "正義",
    "audio_url": "https://open.spotify.com/embed/track/xxxxx",
    "lyrics": "短摘录或链接（请遵守版权）"
  }
]
```

**定位曲目的三种方式**（任选其一）：
- `"id": 1` —— 直接按 track id
- `"album_title" + "track_title"` —— 按专辑名 + 曲名
- `"album_title" + "track_number"` —— 按专辑名 + 曲目序号

### 2️⃣ 预览变更（dry-run，不写入数据库）

```cmd
python update_track_meta.py --json updates.json
```

检查输出，确认要更新的曲目和字段正确。

### 3️⃣ 执行更新（真正写入）

```cmd
python update_track_meta.py --json updates.json --apply
```

✅ 完成！数据库已更新。

---

## 🛠️ 单条更新（快速命令）

### 按 id 更新（最简单）

查看曲目信息（不更新）：
```cmd
python update_track_meta.py --id 1 --show
```

更新 audio_url（预览）：
```cmd
python update_track_meta.py --id 1 --audio-url "https://www.youtube.com/embed/xxxxx"
```

更新并立即写入：
```cmd
python update_track_meta.py --id 1 --audio-url "https://www.youtube.com/embed/xxxxx" --apply
```

### 按专辑名 + 曲名更新

```cmd
python update_track_meta.py --album-title "潜潜话" --track-title "正義" --audio-url "https://open.spotify.com/embed/track/xxxxx" --apply
```

### 从文件读取歌词

```cmd
python update_track_meta.py --id 1 --lyrics-file "lyrics/秒針を噛む.txt" --apply
```

---

## 📁 文件结构说明

```
music_site/
├── music.db                  # SQLite 数据库（会自动生成）
├── update_track_meta.py      # 更新脚本（已有）
├── updates.json              # 你的实际更新清单（可编辑）
└── lyrics/                   # 歌词文本目录
    └── 你的歌词文件.txt       # UTF-8 编码
```

### 数据库备份
批量更新前建议备份：
```cmd
copy music.db music.db.bak
```

恢复备份：
```cmd
copy music.db.bak music.db
```

---

## 🔍 高级用法

### 查看脚本完整帮助

```cmd
python update_track_meta.py --help
```

### 指定数据库路径

```cmd
python update_track_meta.py --db "path\to\other.db" --json updates.json --apply
```

### 批量更新示例（JSON 结构）

参考 `updates_template.json` 中的完整示例，支持：
- 多种键名别名（如 `audio` = `audio_url`，`lyric` = `lyrics`）
- 混合使用 id 和 album_title 定位
- 灵活组合 audio_url 和 lyrics 字段

---

## 🐛 常见问题

**Q: "未找到匹配曲目"**  
A: 检查专辑名/曲名拼写，或使用 `--id` 直接定位。

**Q: "匹配到多条记录"**  
A: 加上 `track_number` 或直接用 `id` 精确定位。

**Q: 歌词文件未找到**  
A: 确保 `lyrics_file` 路径正确，相对路径基于 `music_site/` 目录。

**Q: 想批量清空某些歌词**  
A: 在 JSON 中设置 `"lyrics": null` 或 `"lyrics": ""`。

---

## 📚 更多信息

完整功能说明参见 `update_track_meta.py` 头部的文档注释。
