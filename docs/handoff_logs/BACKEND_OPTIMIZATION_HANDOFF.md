# 邻里帮 V6.1 后台代码优化交接文档

更新时间：2026-06-24

## 1. 当前工作区

- 工作区：`C:\Users\19164\Documents\python101`
- 当前版本目录：`C:\Users\19164\Documents\python101\linlibang\phases\phase_6_streamlit_cloud_supabase`
- 用户端入口：`app.py`
- 后台入口：`admin_app.py`
- 后台实现位置：`app.py` 中的 `admin_main()` 及 `admin_*_panel()` 系列函数
- 本地用户端地址：`http://127.0.0.1:8601`
- 本地后台端地址：`http://127.0.0.1:8602`

不要把 `.streamlit/secrets.toml` 的任何真实密钥写进文档、GitHub 或聊天输出。

## 2. 协作规则

- 继续在本地优化代码。
- 用户明确说“代码完全改好了，可以上传 / 推送 / 部署”之前，不要执行 `git add`、`git commit`、`git push`。
- Render 是后续云端部署方向，但当前阶段先做本地代码完善和本地验证。
- 如果后台优化涉及 Supabase 表结构变化，必须单独生成 SQL，并提醒用户去 Supabase SQL Editor 执行。
- 目前健康信息使用 `residents.health_profile` JSONB 保存，暂不需要新表字段，除非后续决定把健康字段拆成独立列。

## 3. 当前本地代码状态

当前 `git status --short` 显示：

```text
 M linlibang/phases/phase_6_streamlit_cloud_supabase/app.py
?? linlibang/MATERIALS.md
?? linlibang/README.md
?? linlibang/agents.md
?? linlibang/design_refs/
?? linlibang/materials/
?? linlibang/phases/phase_1_elder_request_app/
?? linlibang/phases/phase_2_voice_image/
?? linlibang/phases/phase_3_routing_backend/
?? linlibang/phases/phase_4_neighborhood_admin/
?? linlibang/phases/phase_5_demo_materials/
?? linlibang/phases/phase_6_streamlit_cloud_supabase/app_supabase_experiment_backup.py
?? linlibang/skills/
?? linlibang/specs/
?? linlibang/tools/
```

注意：这些未跟踪文件大多是项目归档和阶段资料，不要随手删除或回滚。当前主要业务代码改动集中在 `app.py`。

## 4. 用户端近期已做事项

- 首页第五张卡片已改为“社区服务站”。
- 四张首页核心卡片仍代表“社区帮我安排”的入口。
- 社区服务站页面按类别展示认证服务商，每个服务商独立信息框。
- 用户端“我的”页增加健康信息和紧急联系人展示。
- “更新健康信息”进入单独页面，保存到 `residents.health_profile` JSONB。
- 后台居民审核面板已能展示居民健康信息摘要和最后更新时间。
- 语音识别逻辑已尝试改为讯飞 WebAPI 实际识别，但用户仍反馈前端体验和识别稳定性需要继续查。
- 底部导航曾因 HTML 链接导致登录状态丢失，已改回 Streamlit 原生按钮方式，但视觉仍需优化。

## 5. 后台现有功能位置

后台入口：

- `admin_app.py` 调用 `app.py` 中的 `admin_main()`

后台主要函数：

- `require_admin_password()`：后台密码入口
- `admin_residents_panel()`：居民审核、认证码、健康信息查看
- `admin_create_ticket_form()`：工作人员代填工单
- `admin_tickets_panel()`：工单分流、状态、指派、费用记录
- `admin_providers_panel()`：认证服务商管理
- `admin_volunteers_panel()`：志愿者管理
- `admin_activities_panel()`：邻里圈活动管理
- `admin_records_panel()`：服务记录查看
- `admin_main()`：后台 tabs 总入口

## 6. 后台下一轮优化重点

建议按小步做，不要一次性大改。

1. 后台整体 UI 适配
   - 当前后台仍是 Streamlit 默认 tab + expander 形态。
   - 需要整理为更清晰的“社区值班工作台”风格。
   - 优先保证可读性、字段完整、操作按钮明确，不追求复杂动效。

2. 居民审核页
   - 居民信息卡片改得更清楚：姓名、电话、住址、状态、认证码、健康信息、紧急联系人。
   - 健康信息 JSONB 字段需要后台完整可读。
   - 审核通过、拒绝、重置认证码按钮要避免误触。

3. 工单分流页
   - 恢复并强化紧急程度、风险等级、推荐处理方、当前状态。
   - 保留“联系社区工作人员 / 电话确认”相关操作。
   - 原始语音应能播放；识别文字应能进入工单说明。
   - 工单多时需要更适合滚动查看和筛选。

4. 服务商管理页
   - 字段需覆盖电话簿展示字段：
     - `category`
     - `name`
     - `phone`
     - `organization`
     - `work_hours`
     - `eta_note`
     - `fee_note`
     - `coverage_note`
     - `description`
     - `certified`
     - `status`
     - `sort_order`
   - 当前应重点补充编辑、停用、排序能力。
   - 如表字段缺失，使用 `supabase_service_providers_phonebook_migration.sql` 或生成新的增量 SQL。

5. 邻里圈管理页
   - 活动新增和审核状态需要更直观。
   - 区分社区活动、邻里互助、共治反馈。
   - 对可公开内容做提示，避免公开隐私。

6. 服务记录页
   - 后台查看服务记录时应能关联居民、工单、服务商、费用。
   - 用户端已有“服务记录”，后台需保证记录来源和展示字段一致。

## 7. 数据库注意事项

当前已知 Supabase 表：

- `communities`
- `residents`
- `tickets`
- `ticket_images`
- `ticket_audio`
- `service_providers`
- `volunteers`
- `service_records`
- `activities`

当前已知 Storage bucket：

- `images`
- `audios`

服务商电话簿字段迁移文件：

```text
supabase_service_providers_phonebook_migration.sql
```

如果下一轮后台优化只调整界面和查询逻辑，不需要数据库迁移。

如果要新增后台筛选字段、健康信息独立列、服务商编辑审计字段等，需要生成新的 SQL 迁移脚本，并明确告诉用户执行位置。

## 8. 待确认或已知问题

- 用户端语音识别仍被用户反馈“不行”，后台优化前可先决定是否一起排查 XFYUN 录音格式、WebSocket 返回、Streamlit `st.audio_input` 输出格式。
- 用户端提交工单页曾出现样式变黑、紧急程度消失、联系社区工作人员消失等反馈，后续如果影响后台工单字段，需要同步核对。
- Figma 视觉稿流程曾开始准备，但新建 Figma 文件时出现 MCP 网络传输错误，尚未完成设计稿输出。
- 不要在后台优化阶段顺手推送 GitHub。

## 9. 新对话开场建议

在新对话中可以直接发：

```text
请继续优化“邻里帮 V6.1 云端版”的后台端代码。
先阅读：
C:\Users\19164\Documents\python101\linlibang\phases\phase_6_streamlit_cloud_supabase\BACKEND_OPTIMIZATION_HANDOFF.md

当前重点：优化后台 `admin_app.py` / `app.py` 中的 `admin_main()` 和后台各管理面板。
要求：先检查当前代码和 Supabase 脚本，不要输出 secrets，不要推送 GitHub；如涉及数据库结构变化，生成 SQL 并提醒我去 Supabase SQL Editor 执行。
```

