import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Bell,
  BriefcaseBusiness,
  CalendarClock,
  CheckCircle2,
  ChevronLeft,
  ClipboardList,
  Heart,
  Home,
  Image as ImageIcon,
  Megaphone,
  Mic,
  Phone,
  PlusCircle,
  ShieldCheck,
  Store,
  User,
  Users,
  Wrench
} from "lucide-react";
import { createClient } from "@supabase/supabase-js";
import "./styles.css";

const COMMUNITY = "安靖社区";
const COMMUNITY_INVITE_CODE = "ANJING2026";
const COMMUNITY_PHONE = "16608008838";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
const adminPassword = import.meta.env.VITE_ADMIN_PASSWORD || "";
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

const requestTypes = {
  "生活需求": { icon: BriefcaseBusiness, detail: "买药、取物、日常照看", placeholder: "例如：想买照片里的降压药，家里已经吃完了。" },
  "上门事项": { icon: Wrench, detail: "维修、家政、理发、助浴", placeholder: "例如：厨房水龙头漏水，地上很滑。" },
  "外出协助": { icon: Users, detail: "陪诊、复查、办事、短途陪同", placeholder: "例如：明天去医院复查，希望有人陪同。" },
  "社区反馈": { icon: Megaphone, detail: "楼道、照明、通行隐患", placeholder: "例如：2号楼3层楼道灯坏了，晚上看不清。" }
};

const ticketStatuses = ["待接收", "待社区分流", "处理中", "已预约", "待社区电话确认", "已完成"];
const activityStatuses = ["待发布", "审核中", "已发布", "已隐藏"];
const activityCategories = ["社区活动", "邻里互助", "共治反馈", "文体活动", "健康讲座", "社区通知", "便民服务", "志愿服务"];

function cx(...parts) {
  return parts.filter(Boolean).join(" ");
}

function shortTime(value) {
  if (!value) return "时间未记录";
  return String(value).replace("T", " ").slice(0, 16);
}

function moneyText(value) {
  if (value === null || value === undefined || value === "") return "待记录";
  if (Number(value) === 0) return "X";
  const n = Number(value);
  return Number.isFinite(n) ? `${n} 元` : String(value);
}

function isMobileBrowser() {
  return /Android|iPhone|iPad|iPod|Mobile|MicroMessenger/i.test(navigator.userAgent || "");
}

function statusTone(status) {
  if (status === "已完成") return "done";
  if (["处理中", "已预约"].includes(status)) return "blue";
  if (status === "待社区电话确认") return "urgent";
  return "orange";
}

async function q(builder) {
  const { data, error } = await builder;
  if (error) throw error;
  return data || [];
}

function ConfigGate({ children }) {
  if (supabase) return children;
  return (
    <main className="mobile-shell">
      <section className="login-hero">
        <div className="logo-mark"><Home /></div>
        <h1>邻里帮</h1>
        <p>正式网页需要先配置 Supabase anon key。</p>
      </section>
      <article className="card">
        <h2>缺少环境变量</h2>
        <p className="muted">复制 `.env.example` 为 `.env.local`，填写 `VITE_SUPABASE_URL` 和 `VITE_SUPABASE_ANON_KEY`。</p>
      </article>
    </main>
  );
}

function MobileTop({ title, onBack, right }) {
  return (
    <header className="mobile-top">
      <button className="icon-button" onClick={onBack}><ChevronLeft /></button>
      <strong>{title}</strong>
      <div>{right}</div>
    </header>
  );
}

function BottomNav({ page, setPage }) {
  const items = [
    ["home", "首页", Home],
    ["community", "邻里圈", Users],
    ["profile", "我的", User]
  ];
  return (
    <nav className="bottom-nav">
      {items.map(([key, label, Icon]) => (
        <button key={key} className={page === key ? "active" : ""} onClick={() => setPage(key)}>
          <Icon />
          <span>{label}</span>
        </button>
      ))}
    </nav>
  );
}

function Login({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [form, setForm] = useState({ name: "", phone: "", address: "", invite: "" });
  const [message, setMessage] = useState("");

  async function login() {
    setMessage("");
    const rows = await q(
      supabase
        .from("residents")
        .select("*, communities(name, service_phone, duty_name, duty_phone)")
        .eq("phone", phone.trim())
        .eq("auth_code", code.trim())
        .eq("status", "已通过")
        .limit(1)
    );
    if (!rows.length) {
      setMessage("手机号或认证码不正确，或账号尚未通过审核。");
      return;
    }
    onLogin(rows[0]);
  }

  async function register() {
    setMessage("");
    if (!form.name.trim() || !form.phone.trim() || !form.address.trim() || form.invite.trim() !== COMMUNITY_INVITE_CODE) {
      setMessage("请完整填写信息，并确认社区邀请码正确。");
      return;
    }
    const communities = await q(supabase.from("communities").select("id").eq("invite_code", COMMUNITY_INVITE_CODE).limit(1));
    const payload = {
      community_id: communities[0]?.id,
      name: form.name.trim(),
      phone: form.phone.trim(),
      address: form.address.trim(),
      status: "待审核",
      health_profile: {}
    };
    const existing = await q(supabase.from("residents").select("id").eq("phone", payload.phone).limit(1));
    if (existing.length) await q(supabase.from("residents").update(payload).eq("id", existing[0].id).select());
    else await q(supabase.from("residents").insert(payload).select());
    setMessage("已提交社区审核。请联系社区管理员获得认证码，审核通过后即可登录。");
    setMode("login");
  }

  return (
    <main className="mobile-shell">
      <section className="login-hero">
        <div className="brand-row">
          <div className="logo-mark"><Home /></div>
          <div>
            <h1>邻里帮</h1>
            <p>{COMMUNITY}养老服务台</p>
          </div>
        </div>
        <span className="stamp">服务台</span>
      </section>

      {mode === "login" ? (
        <article className="card auth-card">
          <h2>居民登录</h2>
          <label>手机号<input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="请输入手机号" /></label>
          <label>六位认证码<input value={code} onChange={(e) => setCode(e.target.value)} placeholder="请输入认证码" /></label>
          <button className="primary" onClick={login}>进入服务台</button>
          <button className="secondary" onClick={() => setMode("register")}>注册</button>
        </article>
      ) : (
        <article className="card auth-card">
          <h2>居民信息登记</h2>
          <p className="muted">注册时不填写健康信息和紧急联系人，后续可在“我的”页面补充。</p>
          <label>姓名<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="请输入姓名" /></label>
          <label>手机号<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="请输入手机号" /></label>
          <label>住址<input value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} placeholder="请输入详细住址" /></label>
          <label>社区邀请码<input value={form.invite} onChange={(e) => setForm({ ...form, invite: e.target.value })} placeholder="请输入社区邀请码" /></label>
          <button className="primary" onClick={register}>提交社区审核</button>
          <button className="ghost" onClick={() => setMode("login")}>返回登录</button>
        </article>
      )}
      {message && <div className="toast">{message}</div>}
      <a className="emergency-phone" href={`tel:${COMMUNITY_PHONE}`}><Phone /> 直接联系社区</a>
    </main>
  );
}

function HomePage({ resident, setPage, setRequestType, tickets }) {
  const activeCount = tickets.filter((x) => x.status !== "已完成").length;
  return (
    <>
      <section className="home-hero">
        <div>
          <h1>{resident.communities?.name || COMMUNITY} · 服务台</h1>
          <p>邻里有事找帮忙，社区为您解决</p>
        </div>
        <a href={`tel:${COMMUNITY_PHONE}`} className="call-pill"><Phone /> 联系社区</a>
      </section>
      <section className="notice"><Megaphone /> <span>社区公告：便民理发服务周三下午 2:00 开放，医保咨询周五上午 9:30 开始。</span></section>
      <h3 className="section-title">常用服务</h3>
      <div className="service-grid">
        {Object.entries(requestTypes).map(([name, info]) => {
          const Icon = info.icon;
          return (
            <button key={name} className="service-tile" onClick={() => { setRequestType(name); setPage("request"); }}>
              <span><Icon /></span>
              <strong>{name}</strong>
              <small>{info.detail}</small>
            </button>
          );
        })}
      </div>
      <button className="wide-row" onClick={() => setPage("services")}><Store /> 社区服务站 <span>查看认证资源</span></button>
      <button className="wide-row" onClick={() => setPage("tickets")}><ClipboardList /> 我的工单 <span>{activeCount} 个进行中</span></button>
    </>
  );
}

function RequestPage({ resident, requestType, setPage, onCreated }) {
  const info = requestTypes[requestType] || requestTypes["生活需求"];
  const [content, setContent] = useState("");
  const [urgency, setUrgency] = useState("今天需要");
  const [needsCallback, setNeedsCallback] = useState(false);
  const [files, setFiles] = useState([]);
  const [audioFile, setAudioFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [photoDialogOpen, setPhotoDialogOpen] = useState(false);
  const cameraInputRef = useRef(null);
  const fileInputRef = useRef(null);
  const mobile = isMobileBrowser();
  const Icon = info.icon;

  async function submit() {
    if (!content.trim() && !files.length && !audioFile) return;
    setBusy(true);
    const route = requestType === "上门事项" ? "认证服务商" : requestType === "生活需求" || requestType === "外出协助" ? "邻里志愿者" : "社区工作人员";
    const { data, error } = await supabase.from("tickets").insert({
      resident_id: resident.id,
      community_id: resident.community_id,
      request_type: requestType,
      content: content.trim(),
      urgency,
      needs_callback: needsCallback,
      status: route === "社区工作人员" ? "待接收" : "待社区分流",
      route_type: route,
      handler_note: route === "认证服务商" ? "专业服务，推荐认证服务商" : route === "邻里志愿者" ? "邻里优先，后台确认" : "社区先电话确认"
    }).select().single();
    if (error) throw error;
    if (audioFile) {
      const path = `tickets/${data.id}/audio/${Date.now()}_${audioFile.name || "voice.webm"}`;
      const upload = await supabase.storage.from("audios").upload(path, audioFile, { upsert: true, contentType: audioFile.type || "audio/webm" });
      if (upload.error) throw upload.error;
      const audioUrl = supabase.storage.from("audios").getPublicUrl(path).data.publicUrl;
      await q(supabase.from("ticket_audio").insert({ ticket_id: data.id, audio_url: audioUrl, storage_path: path, transcript: "" }).select());
      await q(supabase.from("tickets").update({ voice_url: audioUrl, voice_storage_path: path }).eq("id", data.id).select());
    }
    for (let i = 0; i < files.length; i += 1) {
      const file = files[i];
      const path = `tickets/${data.id}/images/${Date.now()}_${i}_${file.name}`;
      const upload = await supabase.storage.from("images").upload(path, file, { upsert: true, contentType: file.type || "image/jpeg" });
      if (upload.error) throw upload.error;
      const publicUrl = supabase.storage.from("images").getPublicUrl(path).data.publicUrl;
      await q(supabase.from("ticket_images").insert({ ticket_id: data.id, image_url: publicUrl, storage_path: path }).select());
    }
    setBusy(false);
    onCreated(data.id);
  }

  return (
    <>
      <MobileTop title="提交需求" onBack={() => setPage("home")} />
      <article className="type-card"><Icon /><div><strong>{requestType}</strong><p>{info.detail}</p></div></article>
      <label className="field">需求描述<textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder={info.placeholder} /></label>
      <VoiceRecorder onReady={setAudioFile} />
      <section className="upload-box" onClick={() => setPhotoDialogOpen(true)}>
        <ImageIcon />
        <strong>上传照片</strong>
        <span>{mobile ? "点击后可选择拍照或本地照片。" : "点击后从电脑本地选择照片。"}</span>
      </section>
      <input
        ref={cameraInputRef}
        className="hidden-input"
        type="file"
        accept="image/*"
        capture="environment"
        onChange={(e) => setFiles((old) => [...old, ...Array.from(e.target.files || [])])}
      />
      <input
        ref={fileInputRef}
        className="hidden-input"
        type="file"
        accept="image/*"
        multiple
        onChange={(e) => setFiles((old) => [...old, ...Array.from(e.target.files || [])])}
      />
      {photoDialogOpen && (
        <div className="photo-dialog-backdrop" onClick={() => setPhotoDialogOpen(false)}>
          <div className="photo-dialog" onClick={(e) => e.stopPropagation()}>
            <h3>上传照片</h3>
            <p>{mobile ? "请选择拍照或从手机相册/文件中选择。" : "电脑网页端仅显示本地文件上传。"}</p>
            {mobile && <button onClick={() => { setPhotoDialogOpen(false); cameraInputRef.current?.click(); }}>拍照上传</button>}
            <button onClick={() => { setPhotoDialogOpen(false); fileInputRef.current?.click(); }}>选择本地文件</button>
            <button className="ghost-dialog" onClick={() => setPhotoDialogOpen(false)}>取消</button>
          </div>
        </div>
      )}
      {!!files.length && <div className="muted">已选择 {files.length} 张照片</div>}
      <div className="chips">
        {["不急", "今天需要", "很紧急"].map((x) => <button key={x} className={urgency === x ? "active" : ""} onClick={() => setUrgency(x)}>{x}</button>)}
      </div>
      <label className="checkline"><input type="checkbox" checked={needsCallback} onChange={(e) => setNeedsCallback(e.target.checked)} /> 需要社区工作人员电话联系我</label>
      <button className="primary" disabled={busy || (!content.trim() && !files.length && !audioFile)} onClick={submit}>生成工单</button>
    </>
  );
}

function VoiceRecorder({ onReady }) {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioUrl, setAudioUrl] = useState("");
  const canRecord = Boolean(navigator.mediaDevices?.getUserMedia && window.isSecureContext);

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    const chunks = [];
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunks.push(event.data);
    };
    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
      const file = new File([blob], `voice_${Date.now()}.webm`, { type: blob.type });
      setAudioUrl(URL.createObjectURL(blob));
      onReady(file);
      stream.getTracks().forEach((track) => track.stop());
    };
    recorder.start();
    setMediaRecorder(recorder);
    setRecording(true);
  }

  function stop() {
    mediaRecorder?.stop();
    setRecording(false);
  }

  return (
    <section className="voice-box">
      <div><Mic /><strong>语音说明</strong><span>{canRecord ? "可录一段原声随工单保存" : "手机浏览器常要求 HTTPS 才能录音，可先上传录音文件或填写文字"}</span></div>
      {canRecord && <button className={recording ? "danger" : ""} onClick={recording ? stop : start}>{recording ? "停止录音" : "开始录音"}</button>}
      <label className="audio-upload">上传录音文件
        <input type="file" accept="audio/*" onChange={(e) => {
          const file = e.target.files?.[0];
          if (!file) return;
          setAudioUrl(URL.createObjectURL(file));
          onReady(file);
        }} />
      </label>
      {audioUrl && <audio src={audioUrl} controls />}
    </section>
  );
}

function TicketsPage({ tickets, setPage }) {
  const [mode, setMode] = useState("进行中");
  const active = tickets.filter((x) => x.status !== "已完成");
  const done = tickets.filter((x) => x.status === "已完成");
  const list = mode === "已完成" ? done : active;
  return (
    <>
      <button className="plain-back" onClick={() => setPage("home")}><ChevronLeft /></button>
      <section className="ticket-hero">
        <div><h1>我的工单</h1><p>查看进度与处理结果</p></div>
        <div className="hero-art"><ClipboardList /></div>
      </section>
      <div className="segment">
        <button className={mode === "进行中" ? "active" : ""} onClick={() => setMode("进行中")}>进行中 <b>{active.length}</b></button>
        <button className={mode === "已完成" ? "active" : ""} onClick={() => setMode("已完成")}>已完成 <b>{done.length}</b></button>
      </div>
      {list.map((ticket) => <TicketCard key={ticket.id} ticket={ticket} />)}
      {!list.length && <article className="empty-card">当前分类下暂无工单。</article>}
    </>
  );
}

function TicketCard({ ticket }) {
  const tone = statusTone(ticket.status);
  const images = ticket.ticket_images || [];
  const audio = ticket.ticket_audio || [];
  return (
    <article className={cx("ticket-card", tone)}>
      <div className="ticket-head">
        <strong>#{ticket.id} · {ticket.request_type}</strong>
        <span className={cx("badge", tone)}>{ticket.status || "待接收"}</span>
      </div>
      <h3>{ticket.content || ticket.voice_text || "未填写文字说明"}</h3>
      <p className="handler">{ticket.handler_note || ticket.route_type || "社区将根据情况处理"}</p>
      <footer>
        <span>{shortTime(ticket.created_at)}</span>
        <span>{audio.length || ticket.voice_url ? <><Mic size={18} /> 有语音</> : null}</span>
        <span>{images.length ? <><ImageIcon size={18} /> 有照片</> : null}</span>
      </footer>
    </article>
  );
}

function CommunityPage({ feed, setPage }) {
  const [tab, setTab] = useState("公告栏");
  const tabs = ["公告栏", "社区活动", "邻里互助", "共治反馈"];
  const items = feed[tab] || [];
  return (
    <>
      <MobileTop title="邻里圈" onBack={() => setPage("home")} />
      <div className="community-tabs">
        {tabs.map((x) => <button key={x} className={tab === x ? "active" : ""} onClick={() => setTab(x)}>{x}</button>)}
      </div>
      {items.map((item, idx) => <FeedCard key={`${item.kind}-${idx}`} item={item} />)}
      {!items.length && <article className="empty-card">暂无内容。</article>}
    </>
  );
}

function FeedCard({ item }) {
  return (
    <article className={cx("feed-card", !item.image_url && "no-image")}>
      <div>
        <span className="badge done">{item.kind}</span>
        <h2>{item.title || "社区动态"}</h2>
        <p>{item.description || "社区已记录。"}</p>
        <div className="feed-meta" dangerouslySetInnerHTML={{ __html: item.meta || "" }} />
      </div>
      {item.image_url && <img src={item.image_url} alt="" />}
    </article>
  );
}

function ServicesPage({ providers, setPage }) {
  const groups = providers.reduce((acc, item) => {
    const key = item.category || "其他服务";
    acc[key] = acc[key] || [];
    acc[key].push(item);
    return acc;
  }, {});
  return (
    <>
      <MobileTop title="社区服务站" onBack={() => setPage("home")} />
      {Object.entries(groups).map(([category, items]) => (
        <section className="provider-group" key={category}>
          <h3>{category}</h3>
          {items.map((p) => (
            <article className="service-row" key={p.id}>
              <Store />
              <div>
                <strong>{p.name}</strong>
                <p>{p.description || p.organization || category}</p>
                <small>电话：{p.phone || COMMUNITY_PHONE}</small>
                <small>距离/范围：{p.coverage_note || p.address || "安靖社区周边约 1-3 公里"}</small>
                <small>时间：{p.work_hours || "电话确认"} · 费用：{p.fee_note || "电话沟通"}</small>
              </div>
              <a href={`tel:${p.phone || COMMUNITY_PHONE}`}>拨打</a>
            </article>
          ))}
        </section>
      ))}
      {!providers.length && <article className="empty-card">暂无服务商信息。</article>}
    </>
  );
}

function ProfilePage({ resident, onLogout, setPage, records }) {
  const health = resident.health_profile || {};
  return (
    <>
      <section className="profile-head">
        <div className="avatar"><User /></div>
        <div><h2>{resident.name}</h2><p>{resident.address}<br />电话：{resident.phone}</p></div>
      </section>
      <button className="wide-row" onClick={() => setPage("health")}><Heart /> 健康信息 <span>{health.health_updated_at || "待补充"}</span></button>
      <button className="wide-row" onClick={() => setPage("records")}><ClipboardList /> 服务记录 <span>{records.length} 条</span></button>
      <button className="secondary" onClick={onLogout}>切换用户</button>
    </>
  );
}

function HealthPage({ resident, setResident, setPage }) {
  const [profile, setProfile] = useState(resident.health_profile || {});
  async function save() {
    const next = { ...profile, health_updated_at: new Date().toLocaleString("zh-CN", { hour12: false }) };
    await q(supabase.from("residents").update({ health_profile: next }).eq("id", resident.id).select());
    setResident({ ...resident, health_profile: next });
    setPage("profile");
  }
  return (
    <>
      <MobileTop title="更新健康信息" onBack={() => setPage("profile")} />
      {[
        ["blood_pressure", "血压", "例如：132/82 mmHg"],
        ["medical_history", "病史", "例如：高血压、糖尿病"],
        ["allergy", "过敏情况", "例如：青霉素过敏"],
        ["medication", "长期用药", "例如：降压药，每日一次"],
        ["emergency_contact_name", "紧急联系人姓名", ""],
        ["emergency_contact_phone", "紧急联系人电话", ""]
      ].map(([key, label, placeholder]) => (
        <label className="field" key={key}>{label}<input value={profile[key] || ""} placeholder={placeholder} onChange={(e) => setProfile({ ...profile, [key]: e.target.value })} /></label>
      ))}
      <button className="primary" onClick={save}>保存健康信息</button>
    </>
  );
}

function RecordsPage({ records, setPage }) {
  return (
    <>
      <MobileTop title="服务记录" onBack={() => setPage("profile")} />
      {records.map((r) => (
        <article className="record-card" key={r.id}>
          <span className="badge done">{r.service_type}</span>
          <h3>{r.service_time}</h3>
          <p>{r.handler_name} · {r.note}</p>
          <small>原费用：{moneyText(r.item_cost)} · 酬劳：{moneyText(r.reward)}</small>
        </article>
      ))}
      {!records.length && <article className="empty-card">暂无服务记录。</article>}
    </>
  );
}

function UserApp() {
  const [resident, setResident] = useState(null);
  const [restoring, setRestoring] = useState(true);
  const [page, setPage] = useState("home");
  const [requestType, setRequestType] = useState("生活需求");
  const [lastTicket, setLastTicket] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [providers, setProviders] = useState([]);
  const [records, setRecords] = useState([]);
  const [feed, setFeed] = useState({ 公告栏: [], 社区活动: [], 邻里互助: [], 共治反馈: [] });

  useEffect(() => {
    restoreResident();
  }, []);

  useEffect(() => {
    if (!resident) return;
    reload();
  }, [resident?.id]);

  async function restoreResident() {
    const savedId = localStorage.getItem("linlibang_resident_id");
    if (!savedId) {
      setRestoring(false);
      return;
    }
    try {
      const rows = await q(
        supabase
          .from("residents")
          .select("*, communities(name, service_phone, duty_name, duty_phone)")
          .eq("id", savedId)
          .eq("status", "已通过")
          .limit(1)
      );
      if (rows.length) setResident(rows[0]);
      else localStorage.removeItem("linlibang_resident_id");
    } finally {
      setRestoring(false);
    }
  }

  function handleLogin(row) {
    localStorage.setItem("linlibang_resident_id", String(row.id));
    setResident(row);
  }

  function handleLogout() {
    localStorage.removeItem("linlibang_resident_id");
    setResident(null);
    setPage("home");
  }

  async function reload() {
    const [ticketRows, providerRows, recordRows, feedData] = await Promise.all([
      q(supabase.from("tickets").select("*, ticket_images(image_url), ticket_audio(audio_url, transcript)").eq("resident_id", resident.id).order("id", { ascending: false })),
      q(supabase.from("service_providers").select("*").eq("community_id", resident.community_id).eq("status", "启用").order("sort_order")),
      q(supabase.from("service_records").select("*").eq("resident_id", resident.id).order("id", { ascending: false })),
      loadFeed(resident.community_id)
    ]);
    setTickets(ticketRows);
    setProviders(providerRows);
    setRecords(recordRows);
    setFeed(feedData);
  }

  if (restoring) return <main className="mobile-shell"><article className="empty-card">正在进入服务台...</article></main>;
  if (!resident) return <Login onLogin={handleLogin} />;
  return (
    <main className="mobile-shell">
      {page === "home" && <HomePage resident={resident} tickets={tickets} setPage={setPage} setRequestType={setRequestType} />}
      {page === "request" && <RequestPage resident={resident} requestType={requestType} setPage={setPage} onCreated={(id) => { setLastTicket(id); reload(); setPage("success"); }} />}
      {page === "success" && <SuccessPage id={lastTicket} setPage={setPage} />}
      {page === "tickets" && <TicketsPage tickets={tickets} setPage={setPage} />}
      {page === "community" && <CommunityPage feed={feed} setPage={setPage} />}
      {page === "services" && <ServicesPage providers={providers} setPage={setPage} />}
      {page === "profile" && <ProfilePage resident={resident} setResident={setResident} onLogout={handleLogout} setPage={setPage} records={records} />}
      {page === "health" && <HealthPage resident={resident} setResident={setResident} setPage={setPage} />}
      {page === "records" && <RecordsPage records={records} setPage={setPage} />}
      {["home", "community", "profile"].includes(page) && <BottomNav page={page} setPage={setPage} />}
    </main>
  );
}

function SuccessPage({ id, setPage }) {
  return (
    <>
      <MobileTop title="提交成功" onBack={() => setPage("home")} />
      <section className="success-card">
        <CheckCircle2 />
        <h1>提交成功</h1>
        <p>工单已生成</p>
        <div>编号 #{id}</div>
      </section>
      <button className="primary" onClick={() => setPage("tickets")}>查看我的工单</button>
      <button className="secondary" onClick={() => setPage("home")}>返回首页</button>
    </>
  );
}

async function loadFeed(communityId) {
  const [activities, records, feedback] = await Promise.all([
    q(supabase.from("activities").select("*").eq("community_id", communityId).eq("status", "已发布").order("id", { ascending: false })),
    q(supabase.from("service_records").select("*, residents(name), tickets(request_type, status, route_type, handler_note, assigned_name)").order("id", { ascending: false }).limit(30)),
    q(supabase.from("tickets").select("*, ticket_images(image_url)").eq("community_id", communityId).eq("request_type", "社区反馈").order("id", { ascending: false }).limit(30))
  ]);
  const activityItems = activities
    .filter((x) => !["邻里互助", "共治反馈"].includes(x.category || "社区活动"))
    .map((x) => ({
      kind: x.category || "社区活动",
      title: x.title,
      description: x.description,
      image_url: x.image_url,
      created_at: x.created_at,
      meta: `时间：${x.event_time || "待定"}<br/>地点：${x.location || "待定"}<br/>负责人：${x.contact_person || "社区服务台"}<br/>电话：${x.contact_phone || COMMUNITY_PHONE}`
    }));
  const helpItems = records
    .filter((x) => `${x.tickets?.route_type || ""} ${x.handler_name || ""}`.includes("志愿") || `${x.tickets?.route_type || ""}`.includes("邻里"))
    .map((x) => ({
      kind: "邻里互助",
      title: x.service_type || x.tickets?.request_type || "邻里互助服务",
      description: x.note || "邻里志愿者已完成互助服务记录。",
      created_at: x.created_at,
      meta: `居民：${x.residents?.name || "社区居民"}<br/>处理人：${x.handler_name || x.tickets?.assigned_name || "邻里志愿者"}<br/>时间：${x.service_time || shortTime(x.created_at)}`
    }));
  const feedbackItems = feedback.map((x) => ({
    kind: "共治反馈",
    title: x.content || x.voice_text || "社区反馈",
    description: x.handler_note || "社区已记录，正在按流程处理。",
    image_url: x.ticket_images?.[0]?.image_url,
    created_at: x.created_at,
    meta: `状态：${x.status || "待接收"}<br/>提交时间：${shortTime(x.created_at)}`
  }));
  const all = [...activityItems, ...helpItems, ...feedbackItems].sort((a, b) => String(b.created_at || "").localeCompare(String(a.created_at || "")));
  return { 公告栏: all, 社区活动: activityItems, 邻里互助: helpItems, 共治反馈: feedbackItems };
}

function AdminLogin({ onLogin }) {
  const [pass, setPass] = useState("");
  const [error, setError] = useState("");
  return (
    <main className="admin-login">
      <section className="admin-login-card">
        <div className="logo-mark"><Home /></div>
        <h1>后台管理入口</h1>
        <p>{COMMUNITY} · 服务台</p>
        <input type="password" value={pass} onChange={(e) => setPass(e.target.value)} placeholder="请输入后台密码" />
        <button className="primary" onClick={() => pass === adminPassword ? onLogin() : setError("密码不正确")}>进入后台</button>
        {error && <span className="error">{error}</span>}
      </section>
    </main>
  );
}

function AdminApp() {
  const [authed, setAuthed] = useState(false);
  const [tab, setTab] = useState("居民审核");
  const [data, setData] = useState({ residents: [], tickets: [], providers: [], volunteers: [], activities: [], records: [] });

  useEffect(() => {
    if (authed) reloadAdmin();
  }, [authed]);

  async function reloadAdmin() {
    const [residents, tickets, providers, volunteers, activities, records] = await Promise.all([
      q(supabase.from("residents").select("*, communities(name)").order("id", { ascending: false })),
      q(supabase.from("tickets").select("*, residents(name, phone, address), ticket_images(image_url), ticket_audio(audio_url, transcript)").order("id", { ascending: false })),
      q(supabase.from("service_providers").select("*").order("sort_order")),
      q(supabase.from("volunteers").select("*").order("id")),
      q(supabase.from("activities").select("*").order("id", { ascending: false })),
      q(supabase.from("service_records").select("*, residents(name, phone), tickets(request_type, status, assigned_name)").order("id", { ascending: false }))
    ]);
    setData({ residents, tickets, providers, volunteers, activities, records });
  }

  if (!authed) return <AdminLogin onLogin={() => setAuthed(true)} />;
  const tabs = ["居民审核", "工单分流", "服务商", "志愿者", "邻里圈", "服务记录"];
  return (
    <main className="admin-shell">
      <header className="admin-top">
        <div><Home /> <strong>邻里帮后台</strong> <span>V6.1 云端版</span></div>
        <div><User /> {COMMUNITY} · 服务台</div>
      </header>
      <nav className="admin-tabs">{tabs.map((x) => <button key={x} className={tab === x ? "active" : ""} onClick={() => setTab(x)}>{x}</button>)}</nav>
      {tab === "居民审核" && <AdminResidents rows={data.residents} reload={reloadAdmin} />}
      {tab === "工单分流" && <AdminTickets rows={data.tickets} residents={data.residents} providers={data.providers} volunteers={data.volunteers} reload={reloadAdmin} />}
      {tab === "服务商" && <AdminProviders rows={data.providers} reload={reloadAdmin} />}
      {tab === "志愿者" && <AdminVolunteers rows={data.volunteers} reload={reloadAdmin} />}
      {tab === "邻里圈" && <AdminActivities rows={data.activities} reload={reloadAdmin} />}
      {tab === "服务记录" && <AdminRecords rows={data.records} />}
    </main>
  );
}

function AdminResidents({ rows, reload }) {
  async function approve(row) {
    const auth_code = row.auth_code || String(Math.floor(Math.random() * 1000000)).padStart(6, "0");
    await q(supabase.from("residents").update({ status: "已通过", auth_code }).eq("id", row.id).select());
    reload();
  }
  return (
    <section className="admin-panel">
      <h1>居民审核与健康资料</h1>
      <p>不显示头像；未补充健康信息和紧急联系人时显示“待补充”；认证码永久有效。</p>
      {rows.map((r) => {
        const h = r.health_profile || {};
        return (
          <article className="resident-row" key={r.id}>
            <div><h2>{r.name} <span className="tag">{r.status}</span></h2><p>电话：{r.phone}<br/>地址：{r.address}<br/>社区：{r.communities?.name || COMMUNITY}</p></div>
            <div><strong>健康信息</strong><p>血压：{h.blood_pressure || "待补充"}<br/>病史：{h.medical_history || "待补充"}<br/>过敏：{h.allergy || "待补充"}<br/>长期用药：{h.medication || "待补充"}</p></div>
            <div><strong>紧急联系人</strong><p>姓名：{h.emergency_contact_name || h.emergency_contact || "待补充"}<br/>电话：{h.emergency_contact_phone || "待补充"}</p></div>
            <div className="code-box"><b>{r.auth_code || "未生成"}</b><span>永久有效</span>{r.status !== "已通过" && <button onClick={() => approve(r)}>通过认证</button>}</div>
          </article>
        );
      })}
    </section>
  );
}

function AdminTickets({ rows, residents, providers, volunteers, reload }) {
  return (
    <section className="admin-panel">
      <h1>工单分流</h1>
      <div className="admin-stats"><span>{rows.length} 工单</span><span>{rows.filter((x) => x.needs_callback).length} 需电话</span><span>{rows.filter((x) => x.status !== "已完成").length} 进行中</span></div>
      <AdminCreateTicket residents={residents} reload={reload} />
      {rows.map((t) => <AdminTicketItem key={t.id} ticket={t} providers={providers} volunteers={volunteers} reload={reload} />)}
    </section>
  );
}

function AdminCreateTicket({ residents, reload }) {
  const approved = residents.filter((x) => x.status === "已通过");
  const [open, setOpen] = useState(false);
  const [residentId, setResidentId] = useState("");
  const [requestType, setRequestType] = useState("生活需求");
  const [content, setContent] = useState("");
  const [urgency, setUrgency] = useState("今天需要");
  const [needsCallback, setNeedsCallback] = useState(true);

  async function create() {
    const r = approved.find((x) => String(x.id) === String(residentId));
    if (!r || !content.trim()) return;
    const route = requestType === "上门事项" ? "认证服务商" : requestType === "生活需求" || requestType === "外出协助" ? "邻里志愿者" : "社区工作人员";
    await q(supabase.from("tickets").insert({
      resident_id: r.id,
      community_id: r.community_id,
      request_type: requestType,
      content,
      urgency,
      needs_callback: needsCallback,
      status: route === "社区工作人员" ? "待接收" : "待社区分流",
      route_type: route,
      handler_note: `后台代填：${route === "认证服务商" ? "专业服务，推荐认证服务商" : route === "邻里志愿者" ? "邻里优先，后台确认" : "社区先电话确认"}`
    }).select());
    setOpen(false);
    setContent("");
    reload();
  }

  return (
    <article className="admin-create-card">
      <button onClick={() => setOpen(!open)}><PlusCircle /> {open ? "收起代填工单" : "后台代填工单"}</button>
      {open && (
        <div className="admin-create-grid">
          <select value={residentId} onChange={(e) => setResidentId(e.target.value)}>
            <option value="">选择居民</option>
            {approved.map((r) => <option key={r.id} value={r.id}>{r.name} · {r.phone}</option>)}
          </select>
          <select value={requestType} onChange={(e) => setRequestType(e.target.value)}>{Object.keys(requestTypes).map((x) => <option key={x}>{x}</option>)}</select>
          <select value={urgency} onChange={(e) => setUrgency(e.target.value)}>{["不急", "今天需要", "很紧急"].map((x) => <option key={x}>{x}</option>)}</select>
          <label className="inline-check"><input type="checkbox" checked={needsCallback} onChange={(e) => setNeedsCallback(e.target.checked)} /> 电话联系</label>
          <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="需求说明" />
          <button onClick={create}>创建代填工单</button>
        </div>
      )}
    </article>
  );
}

function AdminTicketItem({ ticket, providers, volunteers, reload }) {
  const [status, setStatus] = useState(ticket.status || "待接收");
  const [assignee, setAssignee] = useState("");
  const [note, setNote] = useState(ticket.handler_note || "");
  const candidates = ["暂不指定", ...providers.map((p) => `服务商：${p.name} · ${p.phone}`), ...volunteers.map((v) => `志愿者：${v.name} · ${v.phone || "未填电话"}`)];
  async function save() {
    const assigned_name = assignee && assignee !== "暂不指定" ? assignee.split("：")[1].split(" · ")[0] : "";
    const assigned_phone = assignee && assignee !== "暂不指定" ? assignee.split(" · ")[1] : "";
    await q(supabase.from("tickets").update({ status, assigned_name, assigned_phone, handler_note: note }).eq("id", ticket.id).select());
    reload();
  }
  return (
    <article className="admin-ticket">
      <div><h2>#{ticket.id} · {ticket.request_type} · {ticket.residents?.name || "未知居民"}</h2><p>{ticket.content || ticket.voice_text || "无文字说明"}</p><small>{ticket.residents?.phone} · {ticket.residents?.address}</small></div>
      <select value={status} onChange={(e) => setStatus(e.target.value)}>{ticketStatuses.map((x) => <option key={x}>{x}</option>)}</select>
      <select value={assignee} onChange={(e) => setAssignee(e.target.value)}>{candidates.map((x) => <option key={x}>{x}</option>)}</select>
      <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="工作人员备注" />
      <button onClick={save}>保存处理</button>
    </article>
  );
}

function AdminProviders({ rows, reload }) {
  const blank = { name: "", category: "水电维修", phone: "", organization: "", work_hours: "", eta_note: "", fee_note: "", coverage_note: "", description: "", status: "启用", certified: true, sort_order: 0 };
  return <EditableAdminList title="服务商管理" rows={rows} table="service_providers" blank={blank} fields={[
    ["name", "名称"], ["category", "类别"], ["phone", "电话"], ["organization", "所属机构"], ["work_hours", "工作时间"], ["eta_note", "到达时间"], ["fee_note", "费用说明"], ["coverage_note", "覆盖范围"], ["description", "服务说明"], ["status", "状态"]
  ]} reload={reload} />;
}

function AdminVolunteers({ rows, reload }) {
  const blank = { name: "", phone: "", skills: "", status: "空闲" };
  return <EditableAdminList title="志愿者管理" rows={rows} table="volunteers" blank={blank} fields={[
    ["name", "姓名"], ["phone", "电话"], ["skills", "擅长事项"], ["status", "状态"]
  ]} reload={reload} />;
}

function EditableAdminList({ title, rows, fields, table, blank, reload }) {
  const [draft, setDraft] = useState(blank);
  const [editing, setEditing] = useState({});
  const statusOptions = table === "volunteers" ? ["空闲", "可预约", "忙碌", "休息", "停用"] : ["启用", "停用"];

  async function add() {
    const communities = await q(supabase.from("communities").select("id").eq("invite_code", COMMUNITY_INVITE_CODE).limit(1));
    const payload = { ...draft };
    if (table !== "volunteers") payload.community_id = communities[0]?.id;
    else payload.community_id = communities[0]?.id;
    await q(supabase.from(table).insert(payload).select());
    setDraft(blank);
    reload();
  }

  async function save(row) {
    await q(supabase.from(table).update(editing[row.id] || {}).eq("id", row.id).select());
    reload();
  }

  async function toggle(row) {
    const current = (editing[row.id]?.status ?? row.status) || "启用";
    const next = current === "停用" ? "启用" : "停用";
    await q(supabase.from(table).update({ status: next }).eq("id", row.id).select());
    reload();
  }

  return (
    <section className="admin-panel">
      <h1>{title}</h1>
      <div className="admin-edit-grid">
        {fields.map(([key, label]) => (
          key === "status" ? (
            <select key={key} value={draft[key] ?? ""} onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}>
              {statusOptions.map((x) => <option key={x}>{x}</option>)}
            </select>
          ) : (
            <input key={key} value={draft[key] ?? ""} placeholder={label} onChange={(e) => setDraft({ ...draft, [key]: e.target.value })} />
          )
        ))}
        <button onClick={add}>新增保存</button>
      </div>
      {rows.map((row) => (
        <article className="admin-edit-row" key={row.id}>
          {fields.map(([key, label]) => (
            <label key={key}>{label}
              {key === "status" ? (
                <select
                  className={`status-select status-${String((editing[row.id]?.[key] ?? row[key]) || "").replace(/\s/g, "")}`}
                  value={(editing[row.id]?.[key] ?? row[key]) || statusOptions[0]}
                  onChange={(e) => setEditing({ ...editing, [row.id]: { ...(editing[row.id] || row), [key]: e.target.value } })}
                >
                  {statusOptions.map((x) => <option key={x}>{x}</option>)}
                </select>
              ) : (
                <input value={(editing[row.id]?.[key] ?? row[key]) || ""} onChange={(e) => setEditing({ ...editing, [row.id]: { ...(editing[row.id] || row), [key]: e.target.value } })} />
              )}
            </label>
          ))}
          <div className="admin-row-actions">
            <button onClick={() => save(row)}>保存</button>
            <button onClick={() => toggle(row)}>{((editing[row.id]?.status ?? row.status) === "停用") ? "启用" : "停用"}</button>
          </div>
        </article>
      ))}
    </section>
  );
}

function AdminActivities({ rows, reload }) {
  const [form, setForm] = useState({ title: "", category: "社区活动", description: "", event_time: "", location: "", contact_person: "", contact_phone: "", status: "待发布" });
  const [file, setFile] = useState(null);
  async function saveNew() {
    const communities = await q(supabase.from("communities").select("id").eq("invite_code", COMMUNITY_INVITE_CODE).limit(1));
    const payload = { ...form, community_id: communities[0]?.id };
    if (file) {
      const path = `activities/${Date.now()}_${file.name}`;
      const upload = await supabase.storage.from("images").upload(path, file, { upsert: true, contentType: file.type || "image/jpeg" });
      if (upload.error) throw upload.error;
      payload.image_url = supabase.storage.from("images").getPublicUrl(path).data.publicUrl;
      payload.image_storage_path = path;
    }
    await q(supabase.from("activities").insert(payload).select());
    setForm({ title: "", category: "社区活动", description: "", event_time: "", location: "", contact_person: "", contact_phone: "", status: "待发布" });
    setFile(null);
    reload();
  }
  async function update(row, patch) {
    await q(supabase.from("activities").update(patch).eq("id", row.id).select());
    reload();
  }
  return (
    <section className="admin-panel">
      <h1>邻里圈内容管理</h1>
      <div className="activity-form">
        <input placeholder="活动标题" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{activityCategories.map((x) => <option key={x}>{x}</option>)}</select>
        <input placeholder="时间" value={form.event_time} onChange={(e) => setForm({ ...form, event_time: e.target.value })} />
        <input placeholder="地址" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
        <input placeholder="负责人" value={form.contact_person} onChange={(e) => setForm({ ...form, contact_person: e.target.value })} />
        <input placeholder="联系方式" value={form.contact_phone} onChange={(e) => setForm({ ...form, contact_phone: e.target.value })} />
        <textarea placeholder="简介" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button onClick={saveNew}>保存活动</button>
      </div>
      {rows.map((row) => (
        <article className="activity-row" key={row.id}>
          {row.image_url && <img src={row.image_url} alt="" />}
          <div><span className="tag">{row.category}</span><h2>{row.title}</h2><p>{row.description}</p></div>
          <select value={row.status || "待发布"} onChange={(e) => update(row, { status: e.target.value })}>{activityStatuses.map((x) => <option key={x}>{x}</option>)}</select>
          <select value={row.category || "社区活动"} onChange={(e) => update(row, { category: e.target.value })}>{activityCategories.map((x) => <option key={x}>{x}</option>)}</select>
        </article>
      ))}
    </section>
  );
}

function AdminRecords({ rows }) {
  return (
    <section className="admin-panel">
      <h1>服务记录台账</h1>
      {rows.map((r) => (
        <article className="admin-line" key={r.id}>
          <span>{r.service_time}</span>
          <span>{r.service_type || r.tickets?.request_type}</span>
          <span>{r.residents?.name} · {r.residents?.phone}</span>
          <span>{r.handler_name || r.tickets?.assigned_name}</span>
          <span>{moneyText(r.item_cost)} / {moneyText(r.reward)}</span>
        </article>
      ))}
    </section>
  );
}

function App() {
  const isAdmin = window.location.pathname.startsWith("/admin") || window.location.hash === "#admin";
  return <ConfigGate>{isAdmin ? <AdminApp /> : <UserApp />}</ConfigGate>;
}

createRoot(document.getElementById("root")).render(<App />);
