# 邻里帮 Phase 7 正式网页

这是从 Streamlit 原型迁出的 React/Vite 正式网页版本。

## 页面入口

- 用户端：`/`
- 后台端：`/admin`

本地默认地址：

```powershell
http://localhost:5173/
http://localhost:5173/admin
```

手机和电脑在同一个 Wi-Fi 下时，可用 Vite 输出的 Network 地址预览，例如：

```powershell
http://10.250.159.14:5173/
http://10.250.159.14:5173/admin
```

## 本地运行

```powershell
cd C:\Users\19164\Documents\python101\linlibang\phases\phase_7_react_web
npm install
npm run dev -- --port 5173
```

## 构建检查

```powershell
npm run build
```

构建产物在：

```text
dist/
```

## 环境变量

复制 `.env.example` 为 `.env.local`，填写：

```env
VITE_SUPABASE_URL=你的 Supabase URL
VITE_SUPABASE_ANON_KEY=你的 Supabase anon public key
VITE_ADMIN_PASSWORD=后台演示密码
```

注意：正式部署到浏览器的 Supabase key 必须使用 anon/public key，不要使用 service role key。

## Cloudflare Pages 部署

1. 将代码推到 GitHub。
2. 在 Cloudflare Pages 新建项目并连接 GitHub 仓库。
3. Root directory 选择：

```text
phases/phase_7_react_web
```

4. Framework preset 选择 `Vite`。
5. Build command：

```bash
npm run build
```

6. Build output directory：

```text
dist
```

7. 在 Cloudflare Pages 的环境变量中配置 `.env.local` 里的三个变量。

## 当前功能范围

用户端：

- 居民登录、居民登记
- 首页服务入口、联系社区拨号
- 需求提交、图片上传、录音上传
- 我的工单、进行中/已完成分段
- 社区服务站
- 邻里圈四类信息流：公告栏、社区活动、邻里互助、共治反馈
- 我的、健康信息更新、服务记录

后台端：

- 后台登录
- 居民审核、永久认证码、健康信息/紧急联系人待补充展示
- 工单分流、指派对象、备注、状态保存
- 后台代填工单
- 服务商新增、编辑、启停
- 志愿者新增、编辑、启停
- 邻里圈内容发布、图片上传、状态/类型调整
- 服务记录台账

## 可选 SQL：补充更多服务商

如果希望“社区服务站”每个类别都有多家服务商，在 Supabase SQL Editor 执行：

```text
supabase_service_providers_more_seed.sql
```

这份 SQL 不改表结构，只补充演示数据；同名服务商已存在时不会重复插入。

## 手机录音说明

手机浏览器通常要求 HTTPS 才允许网页调用麦克风。本地用局域网地址预览时，例如：

```text
http://10.250.159.14:5173/
```

部分手机浏览器会禁用录音，这是浏览器安全策略，不是代码问题。部署到 Cloudflare Pages 后会自动使用 HTTPS，录音兼容性会更好。

当前页面也提供“上传录音文件”兜底入口，即使浏览器不能直接录音，也可以先用手机系统录音后上传。

## 手机照片上传说明

用户提交工单时：

- 手机端显示“拍照上传”和“选择本地文件”两个入口。
- 电脑端隐藏拍照入口，只显示本地文件上传。

