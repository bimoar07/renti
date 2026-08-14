# 🔌 Kontrak API Renti — Single Source of Truth

> **Status:** Draf MVP. Backend **wajib** memenuhi kontrak ini; mobile **wajib** mengonsumsi kontrak ini. Perubahan kontrak dilakukan di sini **dulu**, baru sisi lain menyesuaikan.

## Base URL (dev)

- Lokal backend: `http://localhost:8000`
- Swagger/OpenAPI: `http://localhost:8000/docs`

## Endpoint

| Method | Path | Fungsi | Status |
|---|---|---|---|
| `GET` | `/health` | Health check | ✅ MVP |
| `POST` | `/api/v1/conversations` | Buat conversation + baseline readiness | ✅ MVP |
| `POST` | `/api/v1/chat` | Jalur utama chatbot (JSON) | ✅ MVP |
| `POST` | `/api/v1/chat/stream` | SSE adapter | ⏳ Ditunda |

---

## `POST /api/v1/conversations`

Membuat percakapan baru + menyimpan tahap kesiapan awal pengguna (`readiness_stage`).

**Request**
```json
{
  "user_id": "demo-user-001",
  "readiness_stage": "contemplation"
}
```
> `readiness_stage` opsional (default `contemplation`). Nilai: `precontemplation | contemplation | action | maintenance | relapse`.

**Response (201)**
```json
{
  "conversation_id": "conversation-001",
  "user_id": "demo-user-001",
  "readiness_stage": "contemplation",
  "created_at": "2026-08-11T10:00:00Z"
}
```

---

## `POST /api/v1/chat`

Jalur utama chatbot. Terima pesan pengguna + konteks; balas respon terstruktur lengkap dengan metadata routing/policy/readiness/memory/provider.

**Request**
```json
{
  "user_id": "demo-user-001",
  "conversation_id": "conversation-001",
  "message": "Gue lagi pengin ngerokok banget di warkop.",
  "client_context": {
    "location_chip": "warkop",
    "offline": false
  }
}
```

**Response normal (200)**
```json
{
  "conversation_id": "conversation-001",
  "reply": "Gue paham, craving bisa terasa kuat. Yuk lewati beberapa menit pertama dulu dengan napas pelan dan urge surfing.",
  "route": "zone_1_craving",
  "intent": "cessation_support",
  "readiness_stage": "action",
  "policy_action": "ALLOW",
  "memory": {
    "updated": true,
    "context_tags": { "trigger": "craving", "location": "warkop" }
  },
  "provider": { "name": "primary", "fallback_used": false }
}
```

**Response fallback/krisis (tidak diteruskan ke generasi normal)**
```json
{
  "conversation_id": "conversation-001",
  "reply": "Aku ikut prihatin. Jika kamu berada dalam bahaya atau ingin menyakiti diri, segera hubungi layanan darurat (119) atau orang tepercaya di dekatmu.",
  "route": "crisis",
  "intent": "crisis_support",
  "readiness_stage": "action",
  "policy_action": "BLOCK_AND_SIGNPOST",
  "memory": { "updated": false, "context_tags": {} },
  "provider": { "name": "policy_fallback", "fallback_used": true }
}
```

## Field Responsibility

| Field | Diisi backend | Dipakai mobile untuk |
|---|---|---|
| `reply` | Ya | Menampilkan pesan balasan |
| `route` | Ya | (opsional) metadata/penanda |
| `intent` | Ya | (opsional) metadata |
| `readiness_stage` | Ya | Tampilan konteks user |
| `policy_action` | Ya | Render state aman: ALLOW / SAFE_REDIRECT / CLARIFY / BLOCK_AND_SIGNPOST |
| `memory.updated` | Ya | Menampilkan status penyimpanan |
| `memory.context_tags` | Ya | (opsional) insight |
| `provider` | Ya | (opsional) debug/label |

## Kode Status & Error

| Kode | Arti |
|---|---|
| `200` | Normal / fallback dengan policy_action |
| `201` | Conversation dibuat |
| `400` | Payload invalid (Pydantic) |
| `422` | Validasi schema gagal |
| `429` | Rate limit / provider quota (fallback dipicu di sisi backend) |
| `500` | Error internal (Mobile harus menampilkan pesan aman, bukan raw) |

> Error terstruktur (JSON) agar mobile bisa membedakan loading / normal / redirect / block / error / fallback.
