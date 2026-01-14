# BACKLOG_SUGGESTIONS_EXT.md

Danh sách backlog mở rộng (40+ mục) cho plat-portal-api, nhóm theo chủ đề. Mỗi mục gồm: **Type/Priority** (H/M/L), vấn đề, hướng giải pháp, acceptance ngắn. Dùng để tham khảo, ưu tiên và tạo ticket PS-xxx.

---

## Performance & Scalability
- **PS-PERF-01 (H)**: Hard rate limit login/OTP/reset (Anon/User + scoped throttles). Acceptance: throttle in settings, headers trả rate limit, test brute-force.
- **PS-PERF-02 (H)**: N+1 cleanup hot paths (org/client/user list, permissions). Acceptance: select_related/prefetch_related applied; query count budget per endpoint.
- **PS-PERF-03 (M)**: Cache permission trees per user/org/client + invalidation khi role/perm đổi. Acceptance: cache hit >80%, TTL hợp lý, invalidation hook.
- **PS-PERF-04 (M)**: Response caching cho read-heavy GET (configs, modules). Acceptance: cache layer + etag/last-modified, purge on change.
- **PS-PERF-05 (M)**: DB index review; thêm composite indexes cho fields lọc nhiều. Acceptance: top 10 slow queries improved.
- **PS-PERF-06 (L)**: Cursor-based pagination cho danh sách lớn; giảm `MAX_PAGINATE_BY` (<=200). Acceptance: docs + tests.
- **PS-PERF-07 (M)**: Bulk operations API (create/update/delete users/permissions). Acceptance: transactional, partial-failure handling.
- **PS-PERF-08 (M)**: Celery task timeouts/backoff; circuit breaker cho external calls. Acceptance: task SLA + retry policy được cấu hình.
- **PS-PERF-09 (L)**: GZip/Brotli cho responses tĩnh/lớn. Acceptance: enabled + size reduction verified.
- **PS-PERF-10 (M)**: Optimize permission compose service (bitset, caching). Acceptance: latency permission check giảm >=30%.

## Reliability & Observability
- **PS-REL-01 (H)**: Health endpoints (/health, /health/db, /health/redis). Acceptance: return status, latency; integration monitor.
- **PS-REL-02 (H)**: Metrics /metrics (Prometheus): HTTP codes, latency, DB queries, Celery queue depth. Acceptance: exported metrics + alerts.
- **PS-REL-03 (M)**: Structured logging + correlation-id per request; log sampling for noisy paths. Acceptance: correlation-id in logs.
- **PS-REL-04 (M)**: Error handling: replace generic `except Exception`; standardized error payloads. Acceptance: lint for bare excepts; tests.
- **PS-REL-05 (M)**: Dead-letter queue cho Celery; alert khi DLQ > 0. Acceptance: DLQ + alert wiring.
- **PS-REL-06 (L)**: Graceful shutdown hooks (Celery worker/beat, web). Acceptance: in-flight tasks handled or requeued.
- **PS-REL-07 (M)**: Config drift detection (env diff between envs). Acceptance: checklist + automated diff.

## Security & Compliance
- **PS-SEC-01 (H)**: Enforce HTTPS + HSTS, X-Frame-Options, CSP, Referrer-Policy. Acceptance: headers present in prod.
- **PS-SEC-02 (H)**: CSRF review; minimize exemptions. Acceptance: doc exemptions; tests.
- **PS-SEC-03 (H)**: Secrets hygiene scan (detect hardcoded keys). Acceptance: CI secret scan gate.
- **PS-SEC-04 (H)**: Auth refactor (PS-906 follow-up) – unify token/JWT flows; remove TODOs. Acceptance: tests green; TODO cleared.
- **PS-SEC-05 (M)**: Password policy validator (length, upper/lower/num/special). Acceptance: validator enabled + tests.
- **PS-SEC-06 (M)**: Sensitive log scrubber (password/token/cc). Acceptance: scrubbed fields; regression test.
- **PS-SEC-07 (M)**: Rate limit sensitive endpoints (login/reset/register/OTP) – scoped limits. Acceptance: limits configured + tested.
- **PS-SEC-08 (M)**: Dependency uplift (urllib3>=2.x, Django/DRF compatible). Acceptance: deps updated, smoke tests.
- **PS-SEC-09 (L)**: Audit logging enrichment (permission changes, data exports, admin actions). Acceptance: audit events persisted.
- **PS-SEC-10 (M)**: File upload validation (ext, size, magic bytes). Acceptance: validator with tests.

## Data & Search
- **PS-DATA-01 (M)**: Pagination + streaming export for large datasets. Acceptance: chunked export, memory-bounded.
- **PS-DATA-02 (M)**: Background re-index / search refresh hooks (if search is added). Acceptance: async refresh jobs + retries.
- **PS-DATA-03 (L)**: Data retention policy for logs/audit/files. Acceptance: retention config + cleanup job.
- **PS-DATA-04 (L)**: Seed / fixtures hardening (no weak passwords). Acceptance: sanitized fixtures.

## Payments / Billing (if applicable)
- **PS-PAY-01 (M)**: Webhook idempotency + signature verify for Stripe/others. Acceptance: idempotency keys + signature check.
- **PS-PAY-02 (M)**: Retry/backoff for payment webhooks; DLQ for failures. Acceptance: retries + DLQ metrics.
- **PS-PAY-03 (L)**: Billing plan cache + stale-while-revalidate. Acceptance: cache hit >80%, purge on plan change.

## AuthN/AuthZ & Permissions
- **PS-AUTH-01 (H)**: Session/JWT expiry alignment; refresh/rotate tokens; logout-all-sessions. Acceptance: tests for expiry/rotation.
- **PS-AUTH-02 (M)**: Social auth hardening (state, nonce, redirect allowlist). Acceptance: tests + config.
- **PS-AUTH-03 (M)**: Permission evaluation cache (per user/org/client) + invalidation hooks. Acceptance: hit rate, correctness tests.
- **PS-AUTH-04 (M)**: Least-privilege defaults for new roles/apps. Acceptance: default denies; explicit grants.

## Tenancy & Isolation
- **PS-TEN-01 (H)**: Tenant isolation checks on all object accesses; add guard utility. Acceptance: guard used in views/services; tests.
- **PS-TEN-02 (M)**: Soft-delete consistency (org/client/users) and background purge. Acceptance: purge job + integrity checks.
- **PS-TEN-03 (M)**: Invitation flows hardening (idempotent resend, expiry). Acceptance: tests for resend/expiry.

## Notifications & Comms
- **PS-NOTI-01 (M)**: Async email/FCM queue + retry/backoff; template versioning. Acceptance: queue metrics; failure alerts.
- **PS-NOTI-02 (L)**: Digest/aggregation for noisy notifications. Acceptance: grouped sends; user preference respected.

## DevEx / Tooling
- **PS-DEV-01 (M)**: Pre-commit hooks (lint/format/tests subset). Acceptance: hook enabled in repo docs.
- **PS-DEV-02 (M)**: CI flaky-test detector + quarantine. Acceptance: flaky list + alerts.
- **PS-DEV-03 (L)**: Local dev DX script (one-shot: env, migrate, run). Acceptance: doc + script works on fresh clone.
- **PS-DEV-04 (M)**: Perf profiling tool (django-silk or debug toolbar guarded by env). Acceptance: enabled in dev only.

## Documentation & Governance
- **PS-DOC-01 (L)**: API versioning policy + deprecation guide. Acceptance: doc + headers if versioned.
- **PS-DOC-02 (L)**: Runbook for incidents (auth, db, redis, queue). Acceptance: runbook links.
- **PS-DOC-03 (L)**: Security checklist kept in sync with fixes. Acceptance: checklist updated per release.

## Analytics / Product
- **PS-ANA-01 (M)**: Event logging for key flows (login, invite, payments) with PII minimization. Acceptance: events defined; privacy scrub.
- **PS-ANA-02 (L)**: Feature flag framework for gradual rollout. Acceptance: flags controllable per env.

## Backlog Hygiene
- **PS-BLG-01 (M)**: Link all TODO/FIXME to tickets; burn down PS-906 items. Acceptance: zero orphan TODOs.
- **PS-BLG-02 (L)**: Changelog link correction (PS-895 link). Acceptance: link fixed.

---

### Hướng dẫn ưu tiên nhanh
- **Làm trước (H)**: PS-PERF-01, PS-PERF-02, PS-REL-01/02, PS-SEC-01/02/03/04/07, PS-AUTH-01, PS-TEN-01.
- **Tiếp theo (M)**: Cache permissions (PS-PERF-03), response caching (PS-PERF-04), DB index (PS-PERF-05), bulk ops (PS-PERF-07), error handling (PS-REL-04), secret scrub logs (PS-SEC-06), file upload validation (PS-SEC-10), audit enrich (PS-SEC-09), async notifications (PS-NOTI-01), tooling (PS-DEV-01/02), tenant soft-delete cleanup (PS-TEN-02), invitations hardening (PS-TEN-03).
- **Sau (L)**: Pagination tweak, gzip, governance docs, feature flags, analytics events, webhook system (nếu cần), GraphQL/real-time nếu có nhu cầu sản phẩm.

### Cách sử dụng
1) Chọn mục có business impact cao + effort vừa phải (bắt đầu từ nhóm High).  
2) Tạo ticket PS-xxxx, copy tiêu đề + acceptance.  
3) Thêm link sang file này trong description.  
4) Cập nhật trạng thái khi hoàn thành.  


