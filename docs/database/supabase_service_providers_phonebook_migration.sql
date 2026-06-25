-- 邻里帮 V6.1 服务电话簿增量迁移
-- 适用于已经建好 Supabase 表、不想清空重建数据的环境。

alter table service_providers add column if not exists organization text;
alter table service_providers add column if not exists work_hours text;
alter table service_providers add column if not exists eta_note text;
alter table service_providers add column if not exists coverage_note text;
alter table service_providers add column if not exists sort_order int default 0;

insert into service_providers (
  community_id,
  name,
  category,
  description,
  phone,
  organization,
  work_hours,
  eta_note,
  address,
  certified,
  fee_note,
  coverage_note,
  sort_order,
  status
)
select
  c.id,
  v.name,
  v.category,
  v.description,
  v.phone,
  v.organization,
  v.work_hours,
  v.eta_note,
  v.address,
  v.certified,
  v.fee_note,
  v.coverage_note,
  v.sort_order,
  v.status
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
  and not exists (
    select 1
    from service_providers sp
    where sp.community_id = c.id
      and sp.name = v.name
  );
