-- 邻里帮 V6.1 云端版 Supabase 表结构
-- 在 Supabase SQL Editor 中运行一次。
-- 注意：这是一份清空重建版脚本，会删除旧测试表数据。

drop table if exists ticket_audio cascade;
drop table if exists ticket_images cascade;
drop table if exists service_records cascade;
drop table if exists tickets cascade;
drop table if exists activities cascade;
drop table if exists volunteers cascade;
drop table if exists service_providers cascade;
drop table if exists residents cascade;
drop table if exists communities cascade;

create table if not exists communities (
  id bigint generated always as identity primary key,
  name text not null,
  invite_code text not null unique,
  service_phone text not null,
  duty_name text default '张主任',
  duty_phone text default '16608008838',
  created_at timestamptz default now()
);

create table if not exists residents (
  id bigint generated always as identity primary key,
  community_id bigint references communities(id) on delete set null,
  name text not null,
  phone text not null unique,
  address text not null,
  status text default '待审核',
  auth_code text,
  health_profile jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

create table if not exists tickets (
  id bigint generated always as identity primary key,
  resident_id bigint references residents(id) on delete cascade,
  community_id bigint references communities(id) on delete set null,
  request_type text,
  content text,
  voice_text text,
  voice_url text,
  voice_storage_path text,
  urgency text,
  needs_callback boolean default false,
  status text default '待接收',
  route_type text,
  handler_note text,
  assigned_name text,
  assigned_phone text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists ticket_images (
  id bigint generated always as identity primary key,
  ticket_id bigint references tickets(id) on delete cascade,
  image_url text not null,
  storage_path text,
  created_at timestamptz default now()
);

create table if not exists ticket_audio (
  id bigint generated always as identity primary key,
  ticket_id bigint references tickets(id) on delete cascade,
  audio_url text not null,
  storage_path text,
  transcript text,
  created_at timestamptz default now()
);

create table if not exists service_providers (
  id bigint generated always as identity primary key,
  community_id bigint references communities(id) on delete set null,
  name text not null,
  category text,
  description text,
  phone text,
  organization text,
  work_hours text,
  eta_note text,
  address text,
  certified boolean default true,
  fee_note text,
  coverage_note text,
  sort_order int default 0,
  status text default '启用',
  created_at timestamptz default now()
);

create table if not exists volunteers (
  id bigint generated always as identity primary key,
  community_id bigint references communities(id) on delete set null,
  name text not null,
  phone text,
  skills text,
  status text default '启用',
  created_at timestamptz default now()
);

create table if not exists service_records (
  id bigint generated always as identity primary key,
  resident_id bigint references residents(id) on delete cascade,
  ticket_id bigint references tickets(id) on delete set null,
  service_time text,
  service_type text,
  handler_name text,
  item_cost numeric default 0,
  reward numeric default 0,
  note text,
  created_at timestamptz default now()
);

create table if not exists activities (
  id bigint generated always as identity primary key,
  community_id bigint references communities(id) on delete set null,
  title text not null,
  category text default '社区活动',
  description text,
  image_url text,
  image_storage_path text,
  event_time text,
  location text,
  contact_person text,
  contact_phone text,
  status text default '待发布',
  created_at timestamptz default now()
);

alter table communities enable row level security;
alter table residents enable row level security;
alter table tickets enable row level security;
alter table ticket_images enable row level security;
alter table ticket_audio enable row level security;
alter table service_providers enable row level security;
alter table volunteers enable row level security;
alter table service_records enable row level security;
alter table activities enable row level security;

drop policy if exists "linlibang_all_communities" on communities;
drop policy if exists "linlibang_all_residents" on residents;
drop policy if exists "linlibang_all_tickets" on tickets;
drop policy if exists "linlibang_all_ticket_images" on ticket_images;
drop policy if exists "linlibang_all_ticket_audio" on ticket_audio;
drop policy if exists "linlibang_all_service_providers" on service_providers;
drop policy if exists "linlibang_all_volunteers" on volunteers;
drop policy if exists "linlibang_all_service_records" on service_records;
drop policy if exists "linlibang_all_activities" on activities;

create policy "linlibang_all_communities" on communities for all using (true) with check (true);
create policy "linlibang_all_residents" on residents for all using (true) with check (true);
create policy "linlibang_all_tickets" on tickets for all using (true) with check (true);
create policy "linlibang_all_ticket_images" on ticket_images for all using (true) with check (true);
create policy "linlibang_all_ticket_audio" on ticket_audio for all using (true) with check (true);
create policy "linlibang_all_service_providers" on service_providers for all using (true) with check (true);
create policy "linlibang_all_volunteers" on volunteers for all using (true) with check (true);
create policy "linlibang_all_service_records" on service_records for all using (true) with check (true);
create policy "linlibang_all_activities" on activities for all using (true) with check (true);

drop policy if exists "storage_select_uploads_demo" on storage.objects;
drop policy if exists "storage_insert_uploads_demo" on storage.objects;
drop policy if exists "storage_update_uploads_demo" on storage.objects;
drop policy if exists "storage_delete_uploads_demo" on storage.objects;

create policy "storage_select_uploads_demo" on storage.objects
for select using (bucket_id in ('images', 'audios'));

create policy "storage_insert_uploads_demo" on storage.objects
for insert with check (bucket_id in ('images', 'audios'));

create policy "storage_update_uploads_demo" on storage.objects
for update using (bucket_id in ('images', 'audios')) with check (bucket_id in ('images', 'audios'));

create policy "storage_delete_uploads_demo" on storage.objects
for delete using (bucket_id in ('images', 'audios'));

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values
('images', 'images', true, 5242880, array['image/jpeg', 'image/png', 'image/jpg']),
('audios', 'audios', true, 20971520, array['audio/wav', 'audio/x-wav', 'audio/webm', 'audio/mpeg', 'audio/mp4', 'audio/ogg'])
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

insert into communities (name, invite_code, service_phone, duty_name, duty_phone)
values ('安靖社区', 'ANJING2026', '16608008838', '张主任', '16608008838')
on conflict (invite_code) do update set
  name = excluded.name,
  service_phone = excluded.service_phone,
  duty_name = excluded.duty_name,
  duty_phone = excluded.duty_phone;

insert into service_providers (community_id, name, category, description, phone, organization, work_hours, eta_note, address, certified, fee_note, coverage_note, sort_order, status)
select c.id, v.name, v.category, v.description, v.phone, v.organization, v.work_hours, v.eta_note, v.address, v.certified, v.fee_note, v.coverage_note, v.sort_order, v.status
from communities c
cross join (
  values
  ('安靖社区认证水电维修队', '水电维修', '社区备案维修队，适合水龙头、照明、电路等上门维修。', '16608008838', '安靖社区便民维修联盟', '周一至周六 8:30-18:00', '约 15-30 分钟', '安靖社区服务点', true, '上门前电话确认费用', '安靖社区及周边 3 公里', 10, '启用'),
  ('安心家政服务站', '家政保洁', '社区认证家政服务，适合保洁、整理、助浴前咨询等。', '16608008838', '安心家政服务站', '每天 8:00-19:00', '约 30-60 分钟', '安靖社区服务点', true, '按服务内容计费，电话确认', '安靖社区及周边', 20, '启用'),
  ('邻里跑腿代办队', '跑腿代办', '适合买药取物、缴费咨询、短途代取等。', '16608008838', '安靖社区志愿便民队', '周一至周日 9:00-18:00', '约 20-40 分钟', '安靖社区服务点', true, '公益或少量交通费用，电话确认', '安靖社区范围内', 30, '启用'),
  ('安心陪同外出服务', '陪同外出', '适合陪诊、复查、办事、短途陪同。', '16608008838', '安靖社区养老服务协作点', '周一至周五 8:30-17:30', '需提前 1 天预约', '安靖社区服务点', true, '按时长或路程确认费用', '社区周边医院、政务点、商超', 40, '启用'),
  ('居民推荐便民理发', '便民理发', '居民推荐资源，适合提前电话沟通时间。', '16608008838', '便民理发师傅', '周三 12:00-16:00，其他时间电话约', '需提前预约', '社区活动室或上门', false, '电话沟通', '安靖社区内', 50, '启用'),
  ('健康照护咨询员', '健康照护', '适合血压测量提醒、康复照护咨询、慢病随访前沟通。', '16608008838', '安靖社区健康照护协作点', '周一至周五 9:00-17:00', '约 30-60 分钟或预约', '安靖社区服务点', true, '基础咨询公益，专项服务电话确认', '安靖社区及周边', 60, '启用')
) as v(name, category, description, phone, organization, work_hours, eta_note, address, certified, fee_note, coverage_note, sort_order, status)
where c.invite_code = 'ANJING2026'
on conflict do nothing;

insert into volunteers (community_id, name, phone, skills, status)
select c.id, v.name, v.phone, v.skills, v.status
from communities c
cross join (
  values
  ('李阿姨', '16608008838', '倾向服务：买药取物、陪同活动；可服务时段：上午；备注：熟悉社区老人，适合生活需求类工单', '空闲'),
  ('周叔叔', '16608008838', '倾向服务：短途陪同、社区活动协助；可服务时段：下午；备注：适合外出协助和活动签到', '可预约'),
  ('王大姐', '16608008838', '倾向服务：陪同外出、医院复查、社区活动签到；可服务时段：工作日上午；备注：沟通耐心，适合陪同类工单', '空闲'),
  ('陈师傅', '16608008838', '倾向服务：简单维修查看、楼道巡查、搬取轻物；可服务时段：傍晚；备注：目前较忙，适合非紧急事项', '忙碌'),
  ('赵阿姨', '16608008838', '倾向服务：买菜买药、陪同散步、聊天照看；可服务时段：全天可预约；备注：适合生活照看类工单', '空闲'),
  ('刘叔叔', '16608008838', '倾向服务：跑腿代办、取快递、政务中心陪同；可服务时段：周末优先；备注：适合跑腿代办和短途办事', '可预约')
) as v(name, phone, skills, status)
where c.invite_code = 'ANJING2026'
on conflict do nothing;

insert into activities (community_id, title, category, description, event_time, location, contact_person, contact_phone, status)
select c.id, v.title, v.category, v.description, v.event_time, v.location, v.contact_person, v.contact_phone, v.status
from communities c
cross join (
  values
  ('社区健康讲座：高血压日常管理', '健康讲座', '面向社区老人和家属，讲解高血压日常监测、用药提醒和饮食注意事项。', '2026年6月25日 9:30-11:00', '安靖社区党群服务中心二楼活动室', '王老师', '16608008838', '已发布'),
  ('银龄文体活动：太极体验课', '文体活动', '适合初学者参加的轻量太极体验活动，现场有志愿者协助。', '2026年6月27日 15:00-16:30', '社区广场', '李师傅', '16608008838', '已发布')
) as v(title, category, description, event_time, location, contact_person, contact_phone, status)
where c.invite_code = 'ANJING2026'
on conflict do nothing;
