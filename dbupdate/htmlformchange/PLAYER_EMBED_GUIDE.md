## 完整工作流示例
```bash
# 1. 收集 iframe 代码
# 粘贴到 iframes_input.txt

# 2. 提取播放器链接
python reiframe.py

# 3. 编辑 updates.json
# 复制 iframes_output.txt 中的链接

# 4. 批量更新数据库
python update_track_meta.py --json updates.json --apply

# 5. 启动网站
python app.py

# 6. 访问 http://localhost:5000 查看效果
```
## 相关文件
- `templates/track.html` - 播放器模板（自动识别平台）
- `static/css/style.css` - 播放器样式
- `reiframe.py` - iframe 链接提取工具
- `update_track_meta.py` - 数据库批量更新工具
