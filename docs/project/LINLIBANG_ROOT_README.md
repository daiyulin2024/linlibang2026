# 邻里帮 V6.1

邻里帮 V6.1 是一个面向居家社区养老场景的需求收集、工单处理与邻里活动发布工具。

当前版本的定位不是泛泛的社区治理平台，也不是复杂养老服务下单平台，而是先跑通一个可展示、可解释、可继续迭代的小闭环：

> 老人、家属或热心居民能用最少步骤，把老人生活需求、上门事项、外出协助和影响老人安全通行的适老化环境隐患说清楚，并生成社区工作人员可以处理和追踪的工单。

## 后续工作位置

后续针对这个工具的所有改进，包括网页版、报告材料、展示材料、截图、照片整理和后续版本，都统一在这个目录下处理：

```text
C:\Users\19164\Documents\python101\linlibang
```

不要再把新的项目材料散放到 Codex 临时工作区或桌面目录。需要外部材料时，先复制到 `materials/` 再引用。

## 当前可运行版本

主应用目录：

```text
phases/phase_1_elder_request_app/
  app.py          用户端网页
  admin_app.py    社区后台网页
  requirements.txt
  data/
  uploads/
```

## 运行方法

进入应用目录：

```powershell
cd C:\Users\19164\Documents\python101\linlibang\phases\phase_1_elder_request_app
```

安装依赖：

```powershell
pip install -r requirements.txt
```

启动用户端：

```powershell
streamlit run app.py --server.port 8501
```

启动后台端：

```powershell
streamlit run admin_app.py --server.port 8502
```

浏览器打开：

```text
用户端：http://127.0.0.1:8501
后台端：http://127.0.0.1:8502
```

## 已实现成果

- 用户端首页：安靖社区服务台、滚动社区公告、四个核心入口、语音入口、底部导航。
- 需求提交页：文字说明、语音说明、上传照片与文件名展示、紧急程度、电话联系、生成工单。
- 工单流转：成功页、我的工单、工单详情、状态时间线。
- 后台看板：查看工单、已电话联系、转认证服务者、转邻里互助、标记完成。
- 数据互通：用户端和后台端共享同一个 SQLite 数据库，后台状态会反映到用户端。
- 邻里圈：社区活动、文体报名、社区通告、好人好事；一件事情一张卡，详情页报名。
- 邻里圈后台：发布、隐藏、结束、置顶内容，填写负责人和联系方式，查看报名名单。
- 报告材料：已整理到 `materials/`，包含项目报告、课程要求、现场照片、产品截图和组内分享材料。

## 当前不做

- 在线支付。
- 真实派单。
- 真实拨号。
- 复杂二级分类。
- 泛化的全社区事务平台。
- 真实政策补贴匹配。

## 目录说明

```text
design_refs/                         早期视觉参考
materials/
  course_requirements/               老师项目要求、评分细则、补充规则
  fieldwork_photos/                  安靖社区现场照片原图
  presentation/                      组内分享 PPT 和说明
  reports/                           当前项目报告 Word
  screenshots_and_collages/          用户端、后台端截图与报告拼图
phases/
  phase_1_elder_request_app/         当前可运行网页工具
  phase_2_voice_image/               后续语音和图片增强记录
  phase_3_routing_backend/           后续工单分流和后台管理记录
  phase_4_neighborhood_admin/        后续邻里圈和内容审核记录
  phase_5_demo_materials/            后续展示材料记录
skills/                              项目相关 Codex 技能记录
specs/                               需求、规格和 AI 协作模板
tools/
  report/                            报告生成与检查脚本
```

## 材料索引

详见：

```text
MATERIALS.md
```

