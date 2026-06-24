# 邻里帮 V6.1 云端版部署说明

本目录是 Streamlit Cloud + Supabase 部署版本。

## 入口文件

建议在 Streamlit Cloud 创建两个 App，共用同一个 Supabase 项目：

- 用户端：`linlibang/phases/phase_6_streamlit_cloud_supabase/app.py`
- 后台端：`linlibang/phases/phase_6_streamlit_cloud_supabase/admin_app.py`

## 依赖

Streamlit Cloud 会读取本目录下的 `requirements.txt`。

## Supabase 初始化

首次建库可运行：

```text
supabase_schema_v6_cloud.sql
```

已有表、只补服务电话簿字段时运行：

```text
supabase_service_providers_phonebook_migration.sql
```

## Streamlit Secrets

不要把真实密钥提交到 GitHub。部署后在 Streamlit Cloud 的 App settings -> Secrets 中填写：

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "paste_your_supabase_publishable_or_anon_key_here"
ADMIN_PASSWORD = "paste_admin_password_here"

# Optional: XFYUN speech recognition WebAPI.
XFYUN_APP_ID = "paste_xfyun_app_id_here"
XFYUN_API_KEY = "paste_xfyun_api_key_here"
XFYUN_API_SECRET = "paste_xfyun_api_secret_here"
```

本地开发可参考 `.streamlit/secrets.toml.example`，但真实 `.streamlit/secrets.toml` 已被 `.gitignore` 排除。

## 部署后检查

1. 用户端打开后注册居民。
2. 后台端审核居民并生成认证码。
3. 用户端用手机号和认证码登录。
4. 首页四大卡片进入提交需求。
5. “自己选服务”进入服务电话簿，并按类别显示服务商。
6. 后台服务商管理页可以新增机构、工作时间、预计到达、费用说明、覆盖范围和排序。
