# 邻里帮 V6.1 后续代码完善交接文档

更新时间：2026-06-24

## 1. 当前工作区

- 工作区：`C:\Users\19164\Documents\python101`
- 主项目：`C:\Users\19164\Documents\python101\linlibang`
- 当前版本目录：`C:\Users\19164\Documents\python101\linlibang\phases\phase_6_streamlit_cloud_supabase`
- 用户端入口：`app.py`
- 后台入口：`admin_app.py`
- 依赖：`requirements.txt`
- Supabase 初始化脚本：`supabase_schema_v6_cloud.sql`
- 服务电话簿增量迁移：`supabase_service_providers_phonebook_migration.sql`
- Render Blueprint 配置：`C:\Users\19164\Documents\python101\render.yaml`
- Render 说明：`C:\Users\19164\Documents\python101\RENDER_DEPLOY.md`

本地真实密钥文件：

```text
C:\Users\19164\Documents\python101\linlibang\phases\phase_6_streamlit_cloud_supabase\.streamlit\secrets.toml
```

该文件保留在本地，已被 `.gitignore` 排除。交接文档和 GitHub 仓库不写入真实密钥。

## 2. GitHub 与 Render 状态

GitHub 仓库：

```text
https://github.com/daiyulin2024/linlibang2026
```

分支：

```text
main
```

当前选择的云端方式是 Render。Render 相关仓库文件已恢复并保留：

- `render.yaml`
- `RENDER_DEPLOY.md`

当前 Render 地址：

- 用户端：`https://linlibang2026-user.onrender.com`
- 后台端：`https://linlibang2026-manage.onrender.com`

Render 免费实例会空闲休眠，首次访问可能等待较久。

## 3. 后续协作规则

用户要求：

- 后续修改代码时，只在本地改代码和测试。
- 不要在每次修改后自动上传 GitHub。
- 只有当用户明确说“代码完全改好了，可以上传 / 推送 / 部署”时，才执行：

```text
git add -> git commit -> git push
```

如果涉及 Supabase 表结构变更，需要单独提供 SQL 迁移脚本，并提醒用户去 Supabase SQL Editor 执行。代码 push 不会自动修改 Supabase 表结构。

## 4. 当前主要功能

### 用户端

- 居民登录：手机号 + 六位认证码。
- 居民注册：姓名、手机号、地址、社区邀请码。
- 社区邀请码固定：`ANJING2026`。
- 社区电话：`16608008838`。
- 注册信息写入 Supabase `residents`，初始状态为待审核。
- 后台审核通过后生成六位认证码，由工作人员告知用户。
- 首页保持 V6.1 绿色手机竖屏服务台视觉。
- 首页包含公告、四大服务卡片、我的工单、语音输入、底部导航。
- 底部导航：首页 / 邻里圈 / 我的。
- 工单提交支持文字、语音、图片多张上传。
- 图片上传到 Supabase Storage `images` bucket，并记录到 `ticket_images`。
- 音频上传到 Supabase Storage `audios` bucket，并记录到 `ticket_audio`。
- 语音听写使用讯飞 WebAPI，基于 `st.audio_input`。
- “联系社区”使用 `tel:` 链接打开拨号盘。

### 首页入口

首页保留四张 V6.1 原卡片：

- 生活需求
- 上门事项
- 外出协助
- 社区反馈

这四张卡片代表“社区帮我安排”，点击后进入提交需求页，由后台分流。

新增第五张卡片：

- 自己选服务

点击进入“社区服务电话簿”，不是提交工单。

### 服务电话簿

已实现 `page_services()`：

- 标题：自己选服务 / 社区服务电话簿。
- 按类别展示服务商。
- 默认类别：
  - 水电维修
  - 家政保洁
  - 跑腿代办
  - 陪同外出
  - 便民理发
  - 健康照护
- 每个服务商一条独立信息框。
- 展示电话、机构、工作时间、预计到达、费用、覆盖范围、服务说明、认证/备案标签。
- 电话使用 `tel:` 链接。

### 后台端

- `admin_app.py` 调用 `app.py` 中的 `admin_main()`。
- 后台使用 `ADMIN_PASSWORD` 环境变量保护。
- 居民审核：通过、拒绝、重置认证码。
- 工单分流：查看工单、播放语音、保存状态、指派志愿者或服务商、生成服务记录。
- 支持工作人员为已通过居民代填工单。
- 服务商管理字段：
  - 所属机构 `organization`
  - 工作时间段 `work_hours`
  - 预计到达时间 `eta_note`
  - 费用/说明 `fee_note`
  - 地址或覆盖范围 `coverage_note`
  - 排序 `sort_order`
- 后台还包含志愿者、邻里圈活动、服务记录管理。

## 5. 数据库

当前 Supabase 表：

- `communities`
- `residents`
- `tickets`
- `ticket_images`
- `ticket_audio`
- `service_providers`
- `volunteers`
- `service_records`
- `activities`

当前 Supabase Storage bucket：

- `images`
- `audios`

`service_providers` 电话簿字段：

```sql
organization text
work_hours text
eta_note text
coverage_note text
sort_order int default 0
```

首次建库运行：

```text
supabase_schema_v6_cloud.sql
```

已有库只补电话簿字段和示例服务商时运行：

```text
supabase_service_providers_phonebook_migration.sql
```

## 6. 环境变量

当前代码依赖以下环境变量：

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
- 用户端和后台端都使用同一套环境变量。

## 7. 后续优先任务建议

1. 继续本地代码完善，不以部署为当前重点。
2. 本地完整跑通用户端和后台端。
3. 检查 Supabase 表字段是否与代码一致。
4. 走一遍完整流程：
   - 用户端注册居民。
   - 后台审核通过并生成认证码。
   - 用户端登录。
   - 四大卡片提交工单。
   - 自己选服务电话簿展示服务商。
   - 后台工单分流并生成服务记录。
5. 后续可优化：
   - 登录/注册页视觉更精细。
   - 后台服务商支持编辑、停用、删除。
   - 电话簿支持筛选或搜索。
   - 语音识别失败时的降级提示。
   - 图片/音频上传错误提示。

## 8. 新线程开场建议

新线程请先阅读本文件：

```text
C:\Users\19164\Documents\python101\linlibang\phases\phase_6_streamlit_cloud_supabase\NEXT_THREAD_HANDOFF.md
```

然后继续在本地修改代码。除非用户明确说“可以上传/推送/部署”，否则不要 push 到 GitHub。
