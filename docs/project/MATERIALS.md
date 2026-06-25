# 邻里帮材料索引

本文件记录当前已经整理进 `C:\Users\19164\Documents\python101\linlibang` 的项目成果和材料。后续修改报告、网页、截图、展示材料时，以本目录为准。

## 1. 可运行网页工具

位置：

```text
phases/phase_1_elder_request_app/
```

关键文件：

```text
app.py          用户端网页
admin_app.py    社区后台网页
README.md       演示路线和数据说明
requirements.txt
data/phase1.sqlite3
uploads/
```

当前用户端地址：

```text
http://127.0.0.1:8501
```

当前后台端地址：

```text
http://127.0.0.1:8502
```

## 2. 项目报告

位置：

```text
materials/reports/
```

当前文件：

```text
_邻里帮_——聚焦社区、有温度的养老服务调度工具.docx
```

说明：

- 这是目前按“选项 B：公共服务创新路演”改写后的报告初稿。
- 已把项目主题收束为“居家社区养老需求收集、适老化环境隐患反馈与邻里活动发布工具”。
- “批判性反思”和“AI 使用声明/协作日志”后续仍需继续补充。

## 3. 课程规则和评分材料

位置：

```text
materials/course_requirements/
```

文件：

```text
PP创新节规则补充.pdf
评分细则v2.pdf
项目要求v2.pdf
```

用途：

- 写报告、海报、AI 协作日志时对照要求。
- 当前项目走“选项 B：公共服务创新路演”。

## 4. 安靖社区现场照片

位置：

```text
materials/fieldwork_photos/
```

内容：

- 消防通道和通行空间杂物。
- 楼梯通道堆放物。
- 公共场所墙体和柱体掉皮。
- 消防器材放置问题。
- 地下停车场积水。
- 环保宣传活动现场。
- 额外整理的 `fire_exit_corridor_bicycle.jpg`。

使用口径：

这些照片不是为了把项目改成泛泛的社区治理平台，而是用于说明“适老化生活环境反馈”：凡是影响老人安全、通行、居住便利和基本生活质量的问题，都可以通过社区反馈入口形成工单。

## 5. 页面截图和报告拼图

位置：

```text
materials/screenshots_and_collages/
```

文件：

```text
ui_home.png
ui_request.png
ui_community.png
ui_admin.png
ui_user_collage.jpg
field_issues_collage.jpg
community_activity.jpg
```

用途：

- 报告插图。
- 海报产品展示区。
- 现场汇报时说明“用户端和后台端分离，但数据互通”。

## 6. 组内分享材料

位置：

```text
materials/presentation/
```

文件：

```text
邻里帮_组内分享_下一步准备.pptx
组内分享说明_下一步准备.md
```

说明：

原来位于 `C:\Users\19164\Documents\python101\项目分享材料`，现在已经迁移进本项目目录，原目录已删除，避免后续材料分散。

## 7. 整理、报告生成与检查脚本

位置：

```text
tools/
tools/report/
```

文件：

```text
tools/organize_linlibang_assets.py
tools/report/build_linlibang_report.py
tools/report/check_linlibang_report.py
```

用途：

- `tools/organize_linlibang_assets.py`：把桌面和 Codex 临时工作区中属于邻里帮的报告、截图、照片、课程规则和分享材料整理进本项目目录。
- `tools/report/build_linlibang_report.py`：从现有照片、截图和正文模板重新生成报告 Word。
- `tools/report/check_linlibang_report.py`：检查报告字数、表格、图片数量和关键口径。

注意：

后续如果直接在 Word 里手工改报告，重新运行 `build_linlibang_report.py` 会覆盖手工修改。运行前要确认是否需要先把手工修改同步进脚本。

## 8. 已清理的冗余项

已处理：

- 删除 `linlibang` 内的 `__pycache__`。
- 将 `C:\Users\19164\Documents\python101\项目分享材料` 迁移到 `materials/presentation/` 后删除原目录。

未处理：

- 桌面上的原始 Word 备份和 Codex 临时工作区未删除。它们不再作为后续主工作目录，只作为历史备份或临时文件存在。
