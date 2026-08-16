# ADR-13 — Amplop Keamanan Deterministik di Sekeliling LLM

**Status:** accepted

LLM (Gemini/Groq) hanya dipakai untuk konten: generate balasan, ekstraksi rolling summary, dan proposal readiness stage. Semua keputusan keamanan & kebijakan — policy engine (krisis/injeksi), zone routing, tone detection, validator transisi readiness, dan output guardrail — diimplementasikan **deterministik** (keyword/regex/`if`-`else`) dalam kode aplikasi, bukan diserahkan ke LLM. Provider dirancang **never-raise**: rantai fallback `Gemini → Groq → template deterministik`, sehingga error/timing-out/quota LLM tidak pernah menjadi HTTP 500. Output Guardrail deterministik **tidak pernah mengubah `policy_action`** (itu cermin keamanan pesan masuk), hanya isi `reply`.

Alasan: keamanan harus repeatable, dapat diuji offline tanpa koneksi/key, dan tidak bergantung pada model yang black box, berubah-ubah, lambat, atau berbayar. LLM adalah sumber konten yang tidak dipercaya untuk memutuskan batas medis/krisis; kode aplikasi yang memvalidasi & memutuskan.

Dipertimbangkan: LLM-as-judge untuk safety (lebih fleksibel secara semantik, tetapi non-deterministik, mahal, lambat, dan tidak bisa diuji offline). Ditolak karena keamanan adalah prioritas tertinggi.

Konsekuensi: balasan live berasal dari LLM, tetapi seluruh batas keamanan selalu deterministik dan tercakup oleh test suite tanpa jaringan.
