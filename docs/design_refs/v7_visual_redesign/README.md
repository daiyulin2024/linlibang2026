# 邻里帮 V7 视觉重构参考图

本目录保存本轮 UI 视觉重构的高保真参考图。后续代码修改时，以这些图片作为视觉材料，但不改变现有功能入口、跳转逻辑、工单生成、语音识别、图片上传和 Supabase 数据读写。

## 用户端

- `00_user_login.png`：居民登录页
- `00b_user_register.png`：居民信息登记页
- `01_user_home.png`：首页 / 社区服务台
- `02_user_request.png`：提交需求页
- `03_user_tickets.png`：我的工单页
- `04_user_success.png`：提交成功页
- `05_user_services.png`：社区服务站 / 服务电话簿
- `06_user_community.png`：邻里圈
- `07_user_profile.png`：我的页面
- `08_user_health_edit.png`：更新健康信息页
- `09_user_records.png`：服务记录页

## 后台端

- `10a_admin_login.png`：后台登录页
- `10_admin_ticket_routing.png`：工单分流页
- `11_admin_residents.png`：居民审核页
- `12_admin_providers.png`：服务商管理页
- `13_admin_volunteers.png`：志愿者管理页
- `14_admin_activities.png`：邻里圈内容管理页
- `15_admin_records.png`：服务记录台账页

## 复刻边界

优先修改：

- 全局 CSS
- 页面局部 HTML 结构
- 卡片、按钮、标签、表单控件样式
- 列表密度和视觉层级
- 空状态和状态提示的展示方式

避免修改：

- 页面入口和跳转关系
- `create_ticket()`
- `classify_ticket()`
- Supabase 表读写
- 语音识别逻辑
- 图片/音频上传逻辑
- 后台各 tab 的职责
