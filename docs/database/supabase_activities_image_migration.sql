-- 邻里帮 V6.1：邻里圈内容图片字段增量迁移
-- 用途：支持后台发布邻里圈内容时可选上传图片，并在用户端邻里圈展示。
-- 这是增量脚本，不会清空现有数据。

alter table activities
add column if not exists image_url text,
add column if not exists image_storage_path text;
