# 邻里帮 Phase 7 交接文档

更新时间：2026-06-25

## 1. 当前项目状态

- 项目目录：`C:\Users\19164\Documents\python101\linlibang\phases\phase_7_react_web`
- 技术栈：React + Vite + Supabase
- 当前线上地址：
  - 用户端：`https://linlibang2026.pages.dev/`
  - 后台端：`https://linlibang2026.pages.dev/admin`
- Cloudflare Pages 项目名：`linlibang2026`
- 当前 GitHub 仓库：`https://github.com/daiyulin2024/linlibang2026`

## 2. 已完成内容

### 用户端

- 登录、注册、自动保持登录态
- 首页服务入口、联系社区拨号
- 提交需求、图片上传、录音上传兜底
- 我的工单
- 社区服务站
- 邻里圈四类内容：
  - 公告栏
  - 社区活动
  - 邻里互助
  - 共治反馈
- 我的、健康信息更新、服务记录

### 后台端

- 后台登录
- 居民审核
- 工单分流
- 后台代填工单
- 服务商管理
- 志愿者管理
- 邻里圈内容管理
- 服务记录台账

## 3. 数据库与存储

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

当前 Storage bucket：

- `images`
- `audios`

已知需要保留的增量 SQL：

- `supabase_activities_image_migration.sql`
- `supabase_service_providers_more_seed.sql`

## 4. 部署与登录

### Cloudflare Pages

- 线上网站已部署成功。
- 运行方式：Cloudflare Pages + Vite 静态站点。
- Cloudflare Wrangler 已登录当前账号，可继续部署更新。

### 本地构建

```powershell
cd C:\Users\19164\Documents\python101\linlibang\phases\phase_7_react_web
npm install
npm run build
```

### 重新部署

```powershell
cd C:\Users\19164\Documents\python101\linlibang\phases\phase_7_react_web
npx wrangler pages deploy dist --project-name linlibang2026 --commit-dirty=true
```

## 5. GitHub 与 Cloudflare 的关系

- GitHub 只存代码，不直接连数据库。
- Cloudflare Pages 从 GitHub 拉取代码后构建发布。
- 前端通过环境变量连接 Supabase：

```env
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
VITE_ADMIN_PASSWORD=...
```

- 当前 `.env.local` 只保留在本地，不应提交到 GitHub。

## 6. 手机麦克风与照片上传

- 云端部署后使用 HTTPS，手机浏览器才有正常调用麦克风的条件。
- 本地局域网预览时，部分手机浏览器会限制录音，这是浏览器安全策略。
- 页面已提供“上传录音文件”兜底入口。
- 手机端上传照片时有两个入口：
  - 拍照上传
  - 选择本地文件
- 电脑端只显示本地文件上传。

## 7. 后续修改原则

- 先改本地代码，再 `npm run build`。
- 若涉及数据库字段变化，先单独生成 SQL，再让用户去 Supabase SQL Editor 执行。
- 若只涉及演示数据，优先用增量 seed SQL，不改表结构。
- 不要把 Supabase secrets 写进 GitHub 或交接文档。
- 如果要继续调视觉，优先改 `src/main.jsx` 和 `src/styles.css`。

## 8. 推荐下一个动作

如果继续迭代，建议顺序是：

1. 先在本地和手机上检查线上页面细节。
2. 继续按设计图微调用户端首页、服务站、邻里圈。
3. 再决定是否要把 GitHub 仓库切到 `linlibang2026` 的新分支或独立仓库结构。
4. 若要长期自动部署，再把 GitHub 仓库连接到 Cloudflare Pages。

