# Render 部署说明

本仓库已包含 `render.yaml`，可以在 Render 使用 Blueprint 一次创建两个 Web Service：

- `linlibang2026-user`：老人端/用户端
- `linlibang2026-manage`：社区后台端

## 创建 Blueprint

1. 打开 Render Dashboard。
2. 选择 `New +` -> `Blueprint`。
3. 连接 GitHub 仓库 `daiyulin2024/linlibang2026`。
4. Render 会读取仓库根目录的 `render.yaml`。
5. 创建时按提示填写环境变量。

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

`XFYUN_*` 三项用于语音识别；如果暂时不使用语音，可以先留空或稍后再补。

## Supabase

如果数据库还没有初始化，先在 Supabase SQL Editor 运行：

```text
linlibang/phases/phase_6_streamlit_cloud_supabase/supabase_schema_v6_cloud.sql
```

如果数据库已经建好，只补服务电话簿字段，运行：

```text
linlibang/phases/phase_6_streamlit_cloud_supabase/supabase_service_providers_phonebook_migration.sql
```

## 单独创建服务时的命令

用户端 Start Command：

```bash
python -m streamlit run linlibang/phases/phase_6_streamlit_cloud_supabase/app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true --browser.gatherUsageStats=false
```

后台端 Start Command：

```bash
python -m streamlit run linlibang/phases/phase_6_streamlit_cloud_supabase/admin_app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true --browser.gatherUsageStats=false
```

Build Command：

```bash
pip install --upgrade pip && pip install -r linlibang/phases/phase_6_streamlit_cloud_supabase/requirements.txt
```
