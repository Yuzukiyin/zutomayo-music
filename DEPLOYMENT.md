# ZUTOMAYO 音乐网站 - 部署指南

## 方案 1：Vercel 部署（最简单，推荐）

### 步骤：

1. **安装 Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **登录 Vercel**
   ```bash
   vercel login
   ```

3. **部署**
   ```bash
   cd d:\AAAStudy\flask\music_site
   vercel
   ```

4. **按提示操作**
   - Set up and deploy? → Yes
   - Which scope? → 选择你的账号
   - Link to existing project? → No
   - Project name? → zutomayo-music
   - In which directory is your code located? → ./

5. **完成！**
   - Vercel 会给你一个域名，如：`https://zutomayo-music.vercel.app`
   - 每次 git push 会自动重新部署

### 优点：
- ✅ 完全免费
- ✅ 自动 HTTPS
- ✅ 全球 CDN
- ✅ 自动部署

### 缺点：
- ⚠️ 数据库是只读的（SQLite 文件会随部署重置）
- 💡 需要改用外部数据库（如 PlanetScale、Supabase）或每次部署时上传数据库

---

## 方案 2：Railway 部署

### 步骤：

1. **访问** https://railway.app
2. **登录** GitHub 账号
3. **New Project** → Deploy from GitHub repo
4. **选择** 你的仓库（需要先推送到 GitHub）
5. **自动检测** Procfile 和部署
6. **生成域名** - Railway 会给你一个免费域名

### 优点：
- ✅ 支持持久化存储（可以保存数据库）
- ✅ 免费额度：$5/月
- ✅ 简单易用

### 缺点：
- ⚠️ 免费额度有限
- ⚠️ 可能需要绑定信用卡（验证用途）

---

## 方案 3：自己的 VPS（最灵活）

### 准备：
- 购买 VPS（阿里云/腾讯云/Vultr 等）
- 域名（可选，可用 IP 访问）

### 部署步骤：

1. **SSH 连接服务器**
   ```bash
   ssh root@your-server-ip
   ```

2. **安装 Python 和依赖**
   ```bash
   apt update
   apt install python3 python3-pip nginx -y
   ```

3. **上传项目**
   ```bash
   # 在本地
   scp -r d:\AAAStudy\flask\music_site root@your-server-ip:/var/www/
   ```

4. **安装依赖**
   ```bash
   cd /var/www/music_site
   pip3 install -r requirements.txt
   ```

5. **配置 Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:5000 app:app
   ```

6. **配置 Nginx（可选，用于反向代理）**
   ```nginx
   # /etc/nginx/sites-available/music_site
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /static {
           alias /var/www/music_site/static;
       }
   }
   ```

7. **启用配置**
   ```bash
   ln -s /etc/nginx/sites-available/music_site /etc/nginx/sites-enabled/
   systemctl restart nginx
   ```

8. **使用 Systemd 保持运行**
   ```ini
   # /etc/systemd/system/music_site.service
   [Unit]
   Description=ZUTOMAYO Music Site
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/music_site
   ExecStart=/usr/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   systemctl enable music_site
   systemctl start music_site
   ```

---

## 方案 4：Cloudflare Tunnel（本地运行，外网访问）

### 优点：
- ✅ 不需要购买服务器
- ✅ 在本地运行，外网可访问
- ✅ 自动 HTTPS
- ✅ 免费

### 步骤：

1. **下载 Cloudflared**
   - Windows: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

2. **登录**
   ```bash
   cloudflared tunnel login
   ```

3. **创建隧道**
   ```bash
   cloudflared tunnel create zutomayo-music
   ```

4. **配置文件**
   创建 `config.yml`:
   ```yaml
   tunnel: <YOUR-TUNNEL-ID>
   credentials-file: C:\Users\YourName\.cloudflared\<TUNNEL-ID>.json

   ingress:
     - hostname: music.yourdomain.com
       service: http://localhost:5000
     - service: http_status:404
   ```

5. **添加 DNS 记录**
   ```bash
   cloudflared tunnel route dns zutomayo-music music.yourdomain.com
   ```

6. **运行**
   ```bash
   # 启动 Flask
   python app.py

   # 新终端启动隧道
   cloudflared tunnel run zutomayo-music
   ```

---

## 推荐流程（新手）

### 快速测试：
**Vercel** → 5 分钟内部署完成

### 步骤：
1. 确保代码已推送到 GitHub
2. 访问 https://vercel.com
3. Import Project → 选择仓库
4. 自动部署
5. 获得域名：`https://你的项目名.vercel.app`

---

## GitHub 推送步骤

```bash
# 进入项目目录
cd d:\AAAStudy\flask\music_site

# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit - ZUTOMAYO music site"

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/zutomayo-music.git

# 推送
git push -u origin main
```

---

## 注意事项

### 数据库问题：
- ⚠️ SQLite 在 Vercel/Railway 等平台是**只读**的
- 💡 解决方案：
  1. 使用外部数据库（推荐 Supabase PostgreSQL - 免费）
  2. 或每次部署时上传 `music.db` 文件

### 修改 app.py 使用环境变量：
```python
import os

# 开发环境用 SQLite，生产环境用 PostgreSQL
database_url = os.getenv('DATABASE_URL', 'sqlite:///music.db')
db = SQL(database_url)
```

### Vercel 环境变量设置：
1. 项目设置 → Environment Variables
2. 添加：`DATABASE_URL` = `你的数据库连接字符串`

---

## 测试部署

部署后测试这些功能：
- [ ] 首页显示所有专辑
- [ ] 点击专辑进入详情页
- [ ] 点击曲目进入单曲页
- [ ] 播放器轮播功能
- [ ] YouTube/Bilibili/网易云播放器
- [ ] 歌词显示

---

## 常见问题

### Q: YouTube 还是无法播放？
A: 即使部署到正式域名，YouTube 在国内仍可能受限。建议用户优先使用 Bilibili 和网易云。

### Q: 如何更新网站？
A: 
- **Vercel/Railway**: `git push` 即可自动重新部署
- **VPS**: `git pull` 然后 `systemctl restart music_site`

### Q: 如何绑定自己的域名？
A:
- **Vercel**: 项目设置 → Domains → 添加域名
- **Railway**: Settings → Networking → Custom Domain
- **VPS**: 在域名 DNS 设置中添加 A 记录指向服务器 IP

---

## 下一步

选择一个方案开始部署吧！推荐从 **Vercel** 开始，5 分钟就能看到效果。
