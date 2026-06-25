# V6.1 阶段保存结构

## 目标

从 V6.1 开始，项目代码按阶段独立保存，避免旧版 `quick_demo`、`web_demo`、`ppt_quick_demo` 等目录与新版本冲突。

## 当前目录

```text
linlibang/
  README.md
  agents.md
  design_refs/
  specs/
  skills/
  phases/
    phase_1_elder_request_app/
      app.py
      README.md
      requirements.txt
      data/
      uploads/
    phase_2_voice_image/
      README.md
    phase_3_routing_backend/
      README.md
    phase_4_neighborhood_admin/
      README.md
    phase_5_demo_materials/
      README.md
```

## 保留内容

- `specs/`：需求、阶段规格和协作记录。
- `design_refs/`：视觉参考和设计决策记录。
- `skills/`：项目规则。
- `phases/`：各阶段代码与产物。

## 删除内容

已删除旧实现目录：

- `quick_demo/`
- `web_demo/`
- `ppt_quick_demo/`
- `ppt_assets/`
- `ppt_source/`
- `tools/`
- `long_term/`

## 后续规则

- Phase 1 只改 `phases/phase_1_elder_request_app/`。
- Phase 2 新增内容只放 `phases/phase_2_voice_image/`。
- 不把新代码写回旧目录。
- 数据库、上传图片等运行时文件放在对应阶段目录内部。
