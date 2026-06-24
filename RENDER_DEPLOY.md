# Render 部署说明

本仓库使用 `render.yaml` 作为 Render Blueprint 配置，一次创建两个 Web Service：

- `linlibang2026-user`：用户端
- `linlibang2026-manage`：后台端

## 部署入口

Render 选择 `New +` -> `Blueprint`，连接 GitHub 仓库：

```text
daiyulin2024/linlibang2026
```

默认读取仓库根目录：

```text
render.yaml
```

## 环境变量

两个服务都需要同一套环境变量：

```text
SUPABASE_URL
SUPABASE_KEY
ADMIN_PASSWORD
XFYUN_APP_ID
XFYUN_API_KEY
XFYUN_API_SECRET
```

说明：

- `ADMIN_PASSWORD` 是后台工作人员统一登录密码，不是居民密码。
- 居民登录方式是手机号 + 六位认证码。
- `XFYUN_*` 三项用于语音识别，不用语音时可暂不配置，但相关功能会不可用。

## Supabase

首次初始化数据库时，先在 Supabase SQL Editor 运行：

```text
linlibang/phases/phase_6_streamlit_cloud_supabase/supabase_schema_v6_cloud.sql
```

若数据库已存在，只补电话簿字段与示例服务商，运行：

```text
linlibang/phases/phase_6_streamlit_cloud_supabase/supabase_service_providers_phonebook_migration.sql
```

## 运行方式

用户端启动命令：

```bash
python -m streamlit run linlibang/phases/phase_6_streamlit_cloud_supabase/app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true --browser.gatherUsageStats=false
```

后台端启动命令：

```bash
python -m streamlit run linlibang/phases/phase_6_streamlit_cloud_supabase/admin_app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true --browser.gatherUsageStats=false
```

依赖安装命令：

```bash
pip install --upgrade pip && pip install -r linlibang/phases/phase_6_streamlit_cloud_supabase/requirements.txt
```

## 当前 Render 地址

- 用户端：`https://linlibang2026-user.onrender.com`
- 后台端：`https://linlibang2026-manage.onrender.com`

Render 免费实例会在空闲后休眠，首次访问可能需要等待一段时间。
