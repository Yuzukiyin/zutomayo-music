# 🎵 ZUTOMAYO 音乐网站

一个展示 ZUTOMAYO（ずっと真夜中でいいのに。）音乐作品的 Flask 网站，支持多平台播放器轮播。

## ✨ 功能特性

- 📀 **专辑展示** - 按时间顺序展示所有专辑
- 🎵 **曲目列表** - 完整的曲目信息和时长
- 🎬 **多平台播放器** - 支持 YouTube、Bilibili、网易云音乐
- 🔄 **播放器轮播** - 可在不同平台间切换
- 📝 **歌词显示** - 支持显示歌曲描述/歌词
- 📱 **响应式设计** - 适配桌面和移动设备

## 🎨 播放器配置

- **网易云音乐**: 330×86 (小巧的音频播放器)
- **Bilibili**: 680×400 (视频播放器，国内稳定)
- **YouTube**: 680×400 (备选，需特殊网络)

## 🚀 快速开始

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/你的用户名/zutomayo-music.git
cd zutomayo-music

# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

访问: http://localhost:5000

### 部署到线上

详见 [DEPLOYMENT.md](DEPLOYMENT.md)

**推荐方式（5分钟完成）：**

1. 双击运行 `deploy_prepare.bat`
2. 访问 https://vercel.com 用 GitHub 登录
3. Import Project → 选择仓库
4. 一键部署完成！

## 📁 项目结构

```
music_site/
├── app.py                 # Flask 应用主文件
├── music.db              # SQLite 数据库
├── requirements.txt      # Python 依赖
├── templates/            # HTML 模板
│   ├── layout.html       # 基础布局
│   ├── index.html        # 首页
│   ├── album.html        # 专辑详情
│   └── track.html        # 单曲详情
├── static/               # 静态资源
│   ├── css/style.css     # 样式表
│   └── js/               # JavaScript
└── dbupdate/             # 数据库更新工具
```

## 🛠️ 技术栈

- **后端**: Flask 3.0
- **数据库**: SQLite (开发) / PostgreSQL (生产推荐)
- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **部署**: Vercel / Railway / VPS

## 📝 数据库管理

### 更新曲目信息

```bash
cd dbupdate

# 查看某首歌
python update_track_meta.py --album-title "专辑名" --track-title "曲目名" --show

# 更新播放器链接
python update_track_meta.py --json updates.json --apply

# 调整播放器顺序
python prioritize_bilibili.py --apply
```

## 🎯 部署选项

| 平台 | 难度 | 费用 | 推荐度 |
|------|------|------|--------|
| **Vercel** | ⭐ 极简单 | 免费 | ⭐⭐⭐⭐⭐ |
| **Railway** | ⭐⭐ 简单 | $5/月免费额度 | ⭐⭐⭐⭐ |
| **VPS** | ⭐⭐⭐⭐ 需配置 | ~$5/月起 | ⭐⭐⭐ |
| **Cloudflare Tunnel** | ⭐⭐⭐ 中等 | 免费 | ⭐⭐⭐⭐ |

## ⚠️ 注意事项

### YouTube 播放限制
- YouTube iframe 在国内可能受网络限制
- 即使部署到正式域名，仍可能需要特殊网络
- **建议**: 优先使用 Bilibili 和网易云音乐

### 数据库持久化
- Vercel/Railway 等平台 SQLite 是只读的
- 生产环境推荐使用 PostgreSQL（Supabase 免费）
- 或在每次部署时上传数据库文件

## 📄 许可

本项目仅用于学习交流，音乐版权归 ZUTOMAYO 及相关权利人所有。

## 🔗 相关链接

- [ZUTOMAYO 官网](https://zutomayo.net/)
- [ZUTOMAYO YouTube](https://www.youtube.com/@zutomayo)
- [部署文档](DEPLOYMENT.md)

---

Made with ❤️ for ZUTOMAYO fans
