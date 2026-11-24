# LFS-Tool 部署指南（Docker Compose）

## 一、整体架构

整套服务分成两个容器，由 `docker-compose.yml` 编排：

| 容器 | 作用 | 对外端口 |
| --- | --- | --- |
| `lfs-backend` | Django + gunicorn，跑格式转换；内置 LibreOffice Writer + 中文字体 | 仅内部网络，不对外 |
| `lfs-frontend` | Nginx 托管 Vue 打包产物，并把 `/api/`、`/media/` 反代到后端 | 宿主机 80 |

数据持久化在宿主机 `./data/` 目录（转换产物、临时上传、SQLite 数据库），容器重建或换服务器都不丢。

```
浏览器 ──▶ Nginx(frontend:80) ──┬─ /            静态网页
                                 ├─ /api/  ──▶ backend:8000 (Django)
                                 └─ /media/ ──▶ backend:8000 (下载文件)
```

## 二、服务器前置准备

1. 阿里云 ECS，Ubuntu/Debian 系，建议 2C4G 以上；当前 2G 内存可跑，但 LibreOffice 转换时偏紧，避免并发上传。
2. 安全组放行 **80 端口**（TCP）。路径：阿里云控制台 → 实例 → 安全组 → 配置规则 → 入方向添加 80 端口。
3. 服务器能访问外网（装 Docker、拉镜像、pip/npm 装依赖用）。

## 三、本地先提交代码（在你自己电脑的 WSL 里）

服务器是通过 Git 拉代码的，所以先把本次 Docker 化改动推到 GitHub：

```bash
cd /home/lfs/LFS/LFS-Tool
git add -A
git commit -m "feat: Docker 化部署，compose 编排前后端容器"
git push origin main
```

## 四、服务器上安装 Docker

SSH 登录服务器后执行（Ubuntu/Debian）：

```bash
# 安装 Docker Engine 和 compose 插件
curl -fsSL https://get.docker.com | sh

# 启动并设置开机自启
sudo systemctl enable --now docker

# 验证
docker --version
docker compose version
```

## 五、拉取代码并启动

```bash
# 拉代码（换成你的仓库地址）
git clone https://github.com/Eason-2001/LFS-Tool.git
cd LFS-Tool

# 准备持久化目录
mkdir -p data/outputs data/tmp_uploads

# 配置本地环境变量（.env 已被 .gitignore 忽略，不会进仓库）
cp .env.example .env
# 编辑 .env 填入：
#   MYSQL_PASSWORD / MYSQL_ROOT_PASSWORD / DB_PASSWORD  数据库密码（DB_PASSWORD 与 MYSQL_PASSWORD 填同一值）
#   SENIVERSE_KEY  心知天气 Key（天气板块，留空则天气不可用）
#   SHOWAPI_KEY    万维易源 appKey（命理测算：紫微排盘 / 生肖运势 / 黄历，留空则中式测算不可用）
vi .env

# 构建并后台启动（首次构建要装系统依赖、pip、npm，耗时较长）
sudo docker compose up -d --build

# 查看容器状态
sudo docker compose ps

# 看后端日志（排查转换报错用）
sudo docker compose logs -f backend
```

启动后浏览器访问 `http://47.109.110.119` 即可。

## 六、验收清单

```bash
# 1. 接口通不通（应返回 code 200 和格式列表）
curl http://127.0.0.1/api/converter/supported/

# 2. 容器状态都是 running
sudo docker compose ps
```

页面上验证：打开首页 → 进格式转换 → 选分类 → 上传一个文件转换 → 点下载链接能正常下载。

## 七、日常运维命令

```bash
cd ~/LFS-Tool

# 查看日志
sudo docker compose logs -f backend
sudo docker compose logs -f frontend

# 重启 / 停止 / 启动
sudo docker compose restart
sudo docker compose stop
sudo docker compose start

# 代码更新后重新部署
git pull
sudo docker compose up -d --build

# 进入后端容器排查
sudo docker compose exec backend bash
```

## 八、备份与迁移到新服务器

所有需要保留的数据都在 `./data/` 目录：

- `data/outputs/`：转换结果文件
- `data/tmp_uploads/`：临时上传（可不清空）
- `data/db.sqlite3`：数据库

迁移步骤：

1. 新服务器装好 Docker（见第四节）；
2. 打包旧服务器的 `data/` 目录传过去；
3. `git clone` 代码，把 `data/` 放到仓库目录下；
4. `sudo docker compose up -d --build` 即可。

镜像和环境都打包在 Dockerfile 里，不需要在新机器上手动配 Python、装字体。

## 九、常见问题

- **80 端口被占用**：改 `docker-compose.yml` 里 frontend 的端口映射，如 `"8080:80"`，并在安全组放行 8080。
- **前端页面打开但接口 404/跨域**：确认前端容器 Nginx 反代到了 `backend:8000`；后端容器名必须是 `backend`（compose 服务名）。
- **转换大文件超时**：调大 `Dockerfile.backend` 里 gunicorn 的 `--timeout`，以及 `nginx/default.conf` 里的 `proxy_read_timeout`。
- **2G 内存构建报错/被 OOM**：先 `docker compose build backend` 单独构建，或加 swap 交换分区；LibreOffice 镜像本身体积较大。
- **中文乱码**：确认后端镜像装了 `fonts-noto-cjk`（Dockerfile.backend 已包含）。

## 十、本地开发（不使用容器）

后端：

```bash
cd ~/LFS/LFS-Tool
# 本地直连 127.0.0.1:3306 的 MySQL，默认账号 lfs / lfs123456（与 settings 兜底一致）；
# 要改库地址/账号时再导出 DB_HOST / DB_NAME / DB_USER / DB_PASSWORD / DB_PORT。
# 需要命理 / 天气板块时，先导出对应密钥（不导出则对应板块提示未配置）
export SHOWAPI_KEY=万维易源appKey
export SENIVERSE_KEY=心知天气Key
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

前端：

```bash
cd frontend
npm run dev
```

前端 Vite 已配置代理，`/api/`、`/media/` 自动转发到本机 8000。
