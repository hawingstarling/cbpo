# Backlog Suggestions - Performance, Bug Fixes & New Features

Tài liệu này đề xuất các backlog tickets mới dựa trên phân tích codebase, bao gồm:
- **Performance Improvements**: Tối ưu hóa queries, caching, N+1 problems
- **Bug Fixes**: Các lỗi tiềm ẩn và technical debt
- **New Features**: Tính năng cần thiết cho tương lai

---

## 🚀 Performance Improvements

### 1. **Optimize Permission Queries - N+1 Problem**
**Priority**: High  
**Type**: Performance  
**Estimated Effort**: Medium

**Vấn đề**:
- File: `app/permission/services/compose_permission_service.py` (lines 387, 416)
- TODO comments về optimization trong `get_org_client_user_permission_cache_and_grouping()`
- Có thể có N+1 queries khi fetch permissions cho nhiều users

**Impact**:
- Slow response time khi load permissions cho nhiều users
- High database load
- Poor scalability

**Solution**:
```python
# Sử dụng select_related/prefetch_related
permissions = generic_user_level.group_permissions.select_related(
    'group', 'module'
).prefetch_related(
    'permission_overrides'
).values("group", "module", "key", "enabled", "name")
```

**Acceptance Criteria**:
- [ ] Reduce database queries từ N+1 xuống 2-3 queries
- [ ] Response time giảm 50%+
- [ ] Add query monitoring/benchmarking

---

### 2. **Implement Query Optimization với select_related/prefetch_related**
**Priority**: High  
**Type**: Performance  
**Estimated Effort**: High

**Vấn đề**:
- Nhiều queries không sử dụng `select_related` hoặc `prefetch_related`
- File: `app/permission/services/compose_permission_service.py`
- File: `app/tenancies/sub_views/organization.py`
- File: `app/tenancies/sub_views/client.py`

**Impact**:
- Multiple database round trips
- Slow API responses
- High database connection usage

**Solution**:
- Audit tất cả queries trong codebase
- Add `select_related` cho ForeignKey relationships
- Add `prefetch_related` cho ManyToMany và reverse ForeignKey
- Sử dụng Django Debug Toolbar hoặc django-silk để identify slow queries

**Files cần review**:
- `app/permission/services/compose_permission_service.py`
- `app/tenancies/services.py`
- `app/tenancies/sub_views/*.py`

**Acceptance Criteria**:
- [ ] Audit report về slow queries
- [ ] Optimize top 10 slowest queries
- [ ] Add query monitoring middleware
- [ ] Performance benchmarks before/after

---

### 3. **Implement Caching Strategy cho Permissions**
**Priority**: Medium  
**Type**: Performance  
**Estimated Effort**: Medium

**Vấn đề**:
- Permissions được tính toán lại mỗi request
- File: `app/permission/services/compose_permission_service.py`
- Method: `get_org_client_user_permission_cache_and_grouping()` có comment về cache nhưng chưa implement đầy đủ

**Impact**:
- Redundant permission calculations
- Slow permission checks
- High CPU usage

**Solution**:
```python
from django.core.cache import cache

def get_org_client_user_permission_cache_and_grouping(...):
    cache_key = f"permissions:{user_id}:{org_id}:{client_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Calculate permissions
    permissions = calculate_permissions(...)
    
    # Cache for 5 minutes
    cache.set(cache_key, permissions, 300)
    return permissions
```

**Acceptance Criteria**:
- [ ] Cache permissions với TTL phù hợp
- [ ] Cache invalidation khi permissions thay đổi
- [ ] Cache hit rate > 80%
- [ ] Response time giảm 30%+

---

### 4. **Database Index Optimization**
**Priority**: Medium  
**Type**: Performance  
**Estimated Effort**: Low-Medium

**Vấn đề**:
- Cần audit database indexes
- Một số queries có thể thiếu indexes

**Solution**:
- Analyze slow queries
- Add indexes cho frequently queried fields
- Review composite indexes

**Acceptance Criteria**:
- [ ] Database query analysis report
- [ ] Add missing indexes
- [ ] Query time improvement metrics

---

### 5. **Pagination Optimization**
**Priority**: Low  
**Type**: Performance  
**Estimated Effort**: Low

**Vấn đề**:
- `MAX_PAGINATE_BY = 500` có thể quá lớn
- File: `config/settings/common.py` (line 230)

**Solution**:
- Reduce `MAX_PAGINATE_BY` xuống 100-200
- Implement cursor-based pagination cho large datasets
- Add pagination size limits per endpoint

**Acceptance Criteria**:
- [ ] Reduce max pagination size
- [ ] Implement cursor pagination cho large lists
- [ ] Add pagination documentation

---

## 🐛 Bug Fixes & Technical Debt

### 6. **Fix urllib3 Dependency Version Issue**
**Priority**: Medium  
**Type**: Bug Fix / Dependency  
**Estimated Effort**: Low

**Vấn đề**:
- File: `requirements/base.txt` (line 86)
- TODO comment: `urllib3==1.26.16` - version >=2.x incompatible với Django version
- Technical debt cần resolve

**Impact**:
- Security vulnerabilities trong urllib3 cũ
- Không thể upgrade Django lên version mới hơn
- Dependency conflicts

**Solution**:
- Upgrade Django lên version hỗ trợ urllib3 >= 2.x
- Hoặc tìm alternative solution
- Update requirements

**Acceptance Criteria**:
- [ ] Resolve dependency conflict
- [ ] Upgrade urllib3 lên version mới nhất
- [ ] Test compatibility với Django version hiện tại
- [ ] Update documentation

---

### 7. **Complete PS-906: REST Auth Refactoring**
**Priority**: High  
**Type**: Technical Debt  
**Estimated Effort**: Medium

**Vấn đề**:
- File: `config/settings/common.py` (lines 236, 257)
- File: `app/tenancies/tests/client/test_user_login.py` (line 48)
- File: `app/tenancies/serializers.py` (line 856)
- Nhiều TODO comments về PS-906

**Impact**:
- Inconsistent authentication handling
- Test code có workaround (sử dụng 'key' thay vì 'token')
- Technical debt tích lũy

**Solution**:
- Complete migration từ token-based sang JWT-based
- Remove TODO comments
- Fix test cases
- Update documentation

**Acceptance Criteria**:
- [ ] Complete auth refactoring
- [ ] Remove all TODO comments related to PS-906
- [ ] Fix test cases
- [ ] Update API documentation

---

### 8. **Fix Commented Out Middleware**
**Priority**: Low  
**Type**: Technical Debt  
**Estimated Effort**: Low

**Vấn đề**:
- File: `config/settings/common.py` (line 125)
- `PortalAppContextMiddleware` bị comment out
- File: `app/core/context.py` - middleware có thể cần được enable

**Impact**:
- Missing context data có thể cần thiết
- Incomplete implementation

**Solution**:
- Review xem middleware có cần thiết không
- Nếu cần: fix và enable
- Nếu không: remove code

**Acceptance Criteria**:
- [ ] Review middleware requirements
- [ ] Fix hoặc remove commented code
- [ ] Update documentation

---

### 9. **Improve Error Handling**
**Priority**: Medium  
**Type**: Bug Fix  
**Estimated Effort**: Medium

**Vấn đề**:
- File: `app/tenancies/sub_views/user.py`
- Nhiều generic `except Exception` blocks
- Error messages có thể không đủ informative

**Impact**:
- Difficult to debug issues
- Poor error messages cho users
- Potential information leakage

**Solution**:
- Replace generic exceptions với specific exception types
- Improve error messages
- Add proper logging
- Return user-friendly error messages

**Acceptance Criteria**:
- [ ] Replace generic exceptions
- [ ] Add specific exception handling
- [ ] Improve error messages
- [ ] Add error logging

---

### 10. **Fix CHANGELOG Link Error**
**Priority**: Low  
**Type**: Documentation Bug  
**Estimated Effort**: Very Low

**Vấn đề**:
- File: `CHANGELOG.md` (line 12)
- PS-895 link trỏ đến PS-894 thay vì PS-895

**Solution**:
- Fix link trong CHANGELOG.md

**Acceptance Criteria**:
- [ ] Fix incorrect Jira link

---

## ✨ New Features

### 11. **Implement Rate Limiting**
**Priority**: High  
**Type**: Security / Feature  
**Estimated Effort**: Medium

**Vấn đề**:
- Không có rate limiting cho API endpoints
- Security issue (xem `SECURITY_VULNERABILITIES_AND_ISSUES.md`)

**Impact**:
- Vulnerable to brute force attacks
- DDoS attacks possible
- Resource exhaustion

**Solution**:
```python
# config/settings/common.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute',
        'password_reset': '3/hour',
    }
}
```

**Acceptance Criteria**:
- [ ] Implement rate limiting cho sensitive endpoints
- [ ] Configure appropriate rate limits
- [ ] Add rate limit headers trong responses
- [ ] Document rate limits trong API docs
- [ ] Add monitoring/alerting cho rate limit violations

---

### 12. **API Response Caching**
**Priority**: Medium  
**Type**: Performance / Feature  
**Estimated Effort**: Medium

**Vấn đề**:
- Không có response caching cho read-only endpoints
- Redundant database queries

**Solution**:
- Implement response caching cho:
  - GET endpoints với static data
  - List endpoints (với appropriate cache keys)
- Sử dụng Redis hoặc Django cache framework
- Cache invalidation strategy

**Acceptance Criteria**:
- [ ] Implement response caching
- [ ] Cache invalidation strategy
- [ ] Cache headers trong responses
- [ ] Monitoring cache hit rates

---

### 13. **API Versioning**
**Priority**: Low-Medium  
**Type**: Feature  
**Estimated Effort**: Medium

**Vấn đề**:
- Không có API versioning strategy rõ ràng
- Breaking changes có thể ảnh hưởng clients

**Solution**:
- Implement API versioning (URL-based hoặc header-based)
- Version management strategy
- Deprecation policy

**Acceptance Criteria**:
- [ ] API versioning implementation
- [ ] Version documentation
- [ ] Deprecation policy
- [ ] Migration guide

---

### 14. **Comprehensive API Documentation**
**Priority**: Medium  
**Type**: Feature / Documentation  
**Estimated Effort**: Medium

**Vấn đề**:
- API documentation có thể chưa đầy đủ
- Swagger/OpenAPI docs cần được improve

**Solution**:
- Enhance Swagger documentation
- Add examples cho tất cả endpoints
- Add request/response schemas
- Add error response documentation

**Acceptance Criteria**:
- [ ] Complete API documentation
- [ ] Examples cho all endpoints
- [ ] Error response documentation
- [ ] Interactive API docs

---

### 15. **Health Check & Monitoring Endpoints**
**Priority**: Medium  
**Type**: Feature / DevOps  
**Estimated Effort**: Low

**Vấn đề**:
- Cần health check endpoints cho monitoring
- Database connectivity check
- External service status

**Solution**:
- Implement `/health` endpoint
- Implement `/health/db` endpoint
- Implement `/health/redis` endpoint
- Add metrics endpoint

**Acceptance Criteria**:
- [ ] Health check endpoints
- [ ] Database health check
- [ ] Redis health check
- [ ] Metrics endpoint
- [ ] Integration với monitoring tools

---

### 16. **Audit Logging Enhancement**
**Priority**: Medium  
**Type**: Feature / Security  
**Estimated Effort**: Medium

**Vấn đề**:
- Cần comprehensive audit logging
- Security events cần được log đầy đủ

**Solution**:
- Enhance audit logging
- Log security events (login, permission changes, etc.)
- Log sensitive operations
- Centralized logging

**Acceptance Criteria**:
- [ ] Enhanced audit logging
- [ ] Security event logging
- [ ] Log retention policy
- [ ] Log analysis tools integration

---

### 17. **Bulk Operations API**
**Priority**: Low-Medium  
**Type**: Feature  
**Estimated Effort**: Medium

**Vấn đề**:
- Một số operations cần được thực hiện bulk
- Reduce API calls

**Solution**:
- Implement bulk create/update/delete endpoints
- Batch operations cho:
  - User management
  - Permission updates
  - Organization/Client operations

**Acceptance Criteria**:
- [ ] Bulk operation endpoints
- [ ] Transaction handling
- [ ] Error handling cho partial failures
- [ ] Documentation

---

### 18. **Webhook System**
**Priority**: Low  
**Type**: Feature  
**Estimated Effort**: High

**Vấn đề**:
- Cần webhook system để notify external systems
- Event-driven architecture

**Solution**:
- Implement webhook system
- Event subscriptions
- Webhook delivery với retry logic
- Webhook security (signatures)

**Acceptance Criteria**:
- [ ] Webhook system
- [ ] Event subscriptions
- [ ] Retry logic
- [ ] Webhook security
- [ ] Webhook management UI/API

---

### 19. **GraphQL API (Optional)**
**Priority**: Low  
**Type**: Feature  
**Estimated Effort**: High

**Vấn đề**:
- REST API có thể không flexible cho complex queries
- Over-fetching/under-fetching data

**Solution**:
- Implement GraphQL API
- GraphQL schema
- Query optimization

**Acceptance Criteria**:
- [ ] GraphQL implementation
- [ ] Schema definition
- [ ] Query optimization
- [ ] Documentation

---

### 20. **Real-time Notifications**
**Priority**: Low-Medium  
**Type**: Feature  
**Estimated Effort**: High

**Vấn đề**:
- Cần real-time notifications
- WebSocket hoặc Server-Sent Events

**Solution**:
- Implement WebSocket hoặc SSE
- Real-time notification system
- Connection management

**Acceptance Criteria**:
- [ ] Real-time notification system
- [ ] WebSocket/SSE implementation
- [ ] Connection management
- [ ] Scalability considerations

---

## 📊 Priority Summary

### High Priority (Do First):
1. **Optimize Permission Queries - N+1 Problem** (Performance)
2. **Complete PS-906: REST Auth Refactoring** (Technical Debt)
3. **Implement Rate Limiting** (Security)

### Medium Priority (Do Soon):
4. **Implement Query Optimization** (Performance)
5. **Implement Caching Strategy** (Performance)
6. **Fix urllib3 Dependency** (Bug Fix)
7. **Improve Error Handling** (Bug Fix)
8. **API Response Caching** (Feature)
9. **Health Check Endpoints** (Feature)
10. **Audit Logging Enhancement** (Feature)

### Low Priority (Backlog):
11. **Database Index Optimization** (Performance)
12. **Pagination Optimization** (Performance)
13. **Fix Commented Out Middleware** (Technical Debt)
14. **Fix CHANGELOG Link Error** (Documentation)
15. **Comprehensive API Documentation** (Documentation)
16. **Bulk Operations API** (Feature)
17. **Webhook System** (Feature)
18. **GraphQL API** (Feature - Optional)
19. **Real-time Notifications** (Feature)

---

## 🔍 How to Use This Document

1. **Review each suggestion** với team
2. **Estimate effort** và business value
3. **Prioritize** dựa trên impact và effort
4. **Create Jira tickets** cho các items được approve
5. **Link tickets** về document này
6. **Update status** khi complete

---

## 📝 Notes

- Một số suggestions có thể overlap với existing tickets (PS-894, PS-906, etc.)
- Performance improvements nên được measure trước và sau khi implement
- Security improvements (rate limiting) nên được prioritize cao
- New features cần được validate với stakeholders trước khi implement


