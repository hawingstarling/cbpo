# Phân Tích Hệ Thống Permission Management - Best Practices & Performance

## Tổng Quan
Hệ thống permission management sử dụng kiến trúc phức tạp với:
- Custom Roles → Access Rules → Permissions
- Cache permissions trong `OrgClientUserPermission`
- Override permissions trong `OverridingOrgClientUserPermission`
- Generic Foreign Keys cho Organization/Client level

---

## 🔴 VẤN ĐỀ VỀ PERFORMANCE

### 1. **Thiếu Database Indexes (CRITICAL)**

**Vấn đề:**
- Các bảng permission không có indexes trên các trường thường xuyên query
- Generic Foreign Keys (`object_id`, `content_type_id`) không có composite index
- Các trường filter thường dùng không có index

**Impact:** 
- Query chậm khi có nhiều records
- Full table scans trên các bảng lớn
- Performance degradation khi scale

**Giải pháp:**
```python
# app/permission/models.py

class OrgClientUserPermission(TimeStampedModel):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['object_id', 'content_type']),  # Composite index cho Generic FK
            models.Index(fields=['object_id', 'module', 'enabled']),  # Cho filter permissions
            models.Index(fields=['key', 'group']),  # Cho permission lookup
            models.Index(fields=['object_id', 'key']),  # Cho permission check
        ]

class OverridingOrgClientUserPermission(TimeStampedModel, SoftDeletableModel):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['object_id', 'content_type']),
            models.Index(fields=['permission', 'status']),
        ]

class OrgClientCustomRoleUser(TimeStampedModel, SoftDeletableModel):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['object_id', 'content_type']),
            models.Index(fields=['object_id', 'priority']),  # Cho order_by
            models.Index(fields=['custom_role', 'priority']),
        ]

class CustomRoleAccessRule(TimeStampedModel, SoftDeletableModel):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['custom_role', 'priority']),  # Cho compose_access_rules_from_custom_roles
        ]

class AccessRulePermission(TimeStampedModel, SoftDeletableModel):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['access_rule', 'permission']),
            models.Index(fields=['access_rule', 'status']),
        ]
```

---

### 2. **N+1 Query Problem (HIGH PRIORITY)**

**Vấn đề 1: `compose_access_rules_from_custom_roles`**
```python
# app/permission/services/compose_permission_service.py:114-122
def compose_access_rules_from_custom_roles(role_ids: [str]) -> [AccessRule]:
    query_set = []
    for role_id in role_ids:  # ❌ N queries trong loop
        acc_rule_ids = (
            CustomRoleAccessRule.objects.filter(custom_role_id=role_id)
            .values("access_rule").order_by("priority")
        )
        access_rules = AccessRule.objects.filter(pk__in=acc_rule_ids)
        query_set.extend(access_rules)
    return query_set
```

**Giải pháp:**
```python
@staticmethod
def compose_access_rules_from_custom_roles(role_ids: [str]) -> [AccessRule]:
    # ✅ Single query với select_related
    access_rule_ids = (
        CustomRoleAccessRule.objects
        .filter(custom_role_id__in=role_ids)
        .order_by('custom_role_id', 'priority')
        .values_list('access_rule_id', flat=True)
        .distinct()
    )
    return list(AccessRule.objects.filter(pk__in=access_rule_ids))
```

**Vấn đề 2: `get_overriding_permissions_groups`**
```python
# app/permission/services/compose_permission_service.py:268-277
query_set = OverridingOrgClientUserPermission.objects.filter(object_id=object_id)
res = [
    {
        "group": item.permission.group,  # ❌ N queries cho permission
        "key": item.permission.key,
        # ...
    } for item in query_set
]
```

**Giải pháp:**
```python
@staticmethod
def get_overriding_permissions_groups(object_id: str):
    query_set = (
        OverridingOrgClientUserPermission.objects
        .filter(object_id=object_id)
        .select_related('permission')  # ✅ Prefetch permission
    )
    res = [
        {
            "group": item.permission.group,
            "key": item.permission.key,
            "name": item.permission.name,
            "status": item.status,
            "module": item.permission.module,
        } for item in query_set
    ]
    res = ComposePermissionService.group_composed_permission(res)
    return res
```

**Vấn đề 3: `get_generic_obj_user_current` trong views**
```python
# app/permission/sub_views/base_view.py:28-39
def get_generic_obj_user_current(self):
    # ❌ Không có select_related/prefetch_related
    if level == ORG_LEVEL_KEY:
        generic_obj_user = OrganizationUserProxy.objects.get(
            user=self.request.user, 
            organization=content_obj
        )
```

**Giải pháp:**
```python
def get_generic_obj_user_current(self):
    level = self.get_level_view()
    content_obj = self.get_content_obj()
    
    if level == ORG_LEVEL_KEY:
        generic_obj_user = (
            OrganizationUserProxy.objects
            .select_related('user', 'organization')
            .prefetch_related('custom_roles__custom_role', 'group_permissions')
            .get(user=self.request.user, organization=content_obj)
        )
    elif level == CLIENT_LEVEL_KEY:
        generic_obj_user = (
            ClientUserProxy.objects
            .select_related('user', 'client', 'client__organization')
            .prefetch_related('custom_roles__custom_role', 'group_permissions')
            .get(user_id=self.request.user.pk, client=content_obj)
        )
    # ...
```

---

### 3. **Thiếu Caching Mechanism (HIGH PRIORITY)**

**Vấn đề:**
- Mỗi request phải query database để check permissions
- `OrgClientUserPermission` là cache table nhưng không có in-memory cache
- Permission checks lặp lại nhiều lần trong cùng request

**Giải pháp:**
```python
# app/permission/services/permission_cache.py (NEW FILE)
from functools import lru_cache
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType

class PermissionCacheService:
    CACHE_TIMEOUT = 300  # 5 minutes
    CACHE_KEY_PREFIX = "user_permissions"
    
    @classmethod
    def get_cache_key(cls, object_id: str, content_type_id: int) -> str:
        return f"{cls.CACHE_KEY_PREFIX}:{content_type_id}:{object_id}"
    
    @classmethod
    def get_user_permissions(cls, generic_user_obj):
        """Get cached permissions for user"""
        content_type = ContentType.objects.get_for_model(generic_user_obj)
        cache_key = cls.get_cache_key(
            str(generic_user_obj.id), 
            content_type.id
        )
        
        permissions = cache.get(cache_key)
        if permissions is None:
            permissions = list(
                generic_user_obj.group_permissions.values(
                    'key', 'group', 'module', 'enabled'
                )
            )
            cache.set(cache_key, permissions, cls.CACHE_TIMEOUT)
        
        return permissions
    
    @classmethod
    def invalidate_user_permissions(cls, object_id: str, content_type_id: int):
        """Invalidate cache when permissions change"""
        cache_key = cls.get_cache_key(object_id, content_type_id)
        cache.delete(cache_key)
    
    @classmethod
    def has_permission(cls, generic_user_obj, permission_key: str, module: str = None) -> bool:
        """Check if user has specific permission"""
        permissions = cls.get_user_permissions(generic_user_obj)
        
        for perm in permissions:
            if perm['key'] == permission_key:
                if module is None or perm['module'] == module:
                    return perm['enabled']
        return False
```

**Sử dụng trong ComposePermissionService:**
```python
# Sau khi save permissions, invalidate cache
@staticmethod
def save_composed_permission(permission, object_reference):
    # ... existing code ...
    bulk_sync(...)
    
    # ✅ Invalidate cache
    content_type = ContentType.objects.get_for_model(object_reference)
    PermissionCacheService.invalidate_user_permissions(
        str(object_reference.id),
        content_type.id
    )
```

---

### 4. **Inefficient Permission Lookup trong Loops**

**Vấn đề:**
```python
# app/permission/services/compose_permission_service.py:169-186
def handler_overriding_permissions_groups(_group_key, _module, _list_per):
    for _per in list_per:
        _status = _per.get("status")
        _key = _per.get("key")
        try:
            ins = Permission.objects.get(key=_key, group=_group_key)  # ❌ Query trong loop
            # ...
```

**Giải pháp:**
```python
def handler_overriding_permissions_groups(_group_key, _module, _list_per):
    # ✅ Prefetch all permissions in one query
    permission_keys = [_per.get("key") for _per in list_per]
    permissions_dict = {
        (p.key, p.group): p 
        for p in Permission.objects.filter(
            key__in=permission_keys, 
            group=_group_key
        )
    }
    
    for _per in list_per:
        _status = _per.get("status")
        _key = _per.get("key")
        ins = permissions_dict.get((_key, _group_key))
        if not ins:
            raise ValidationError(f"Permission does not exist. [{_key}, {_group_key}]")
        # ...
```

---

## 🟡 VẤN ĐỀ VỀ BEST PRACTICES

### 5. **Thiếu Transaction Management**

**Vấn đề:**
```python
# app/permission/services/organization.py:162-163
OrgClientUserPermission.objects.filter(object_id__in=all_object_ids).delete()
OrgClientUserPermission.objects.bulk_create(res, batch_size=5000)
# ❌ Không có transaction, có thể mất data nếu lỗi
```

**Giải pháp:**
```python
from django.db import transaction

def __sync(self, objects, default_role_ids):
    with transaction.atomic():
        all_object_ids = [ele.id for ele in objects]
        # ... existing code ...
        OrgClientUserPermission.objects.filter(object_id__in=all_object_ids).delete()
        OrgClientUserPermission.objects.bulk_create(res, batch_size=5000)
```

---

### 6. **Thiếu Error Handling & Logging**

**Vấn đề:**
- Một số methods không có proper error handling
- Thiếu logging cho permission operations

**Giải pháp:**
```python
import logging
logger = logging.getLogger(__name__)

@staticmethod
def sync_permission_of_user_client_org(affected_object_ids: [str]):
    for object_id in affected_object_ids:
        try:
            logger.info(f"Syncing permission for user object id {object_id}")
            # ... existing code ...
        except Exception as err:
            logger.error(
                f"Failed to sync permission for object_id {object_id}: {str(err)}",
                exc_info=True
            )
            continue  # ✅ Continue với user khác thay vì fail toàn bộ
```

---

### 7. **Inefficient List Operations**

**Vấn đề:**
```python
# app/permission/services/compose_permission_service.py:138-140
find_exist = [item for item in res if item["key"] == x["key"]]  # ❌ O(n) lookup
if len(find_exist) == 0:
    res.append(x)
```

**Giải pháp:**
```python
def append_method(x, which="res"):
    target_list = res if which == "res" else res_inherit_not_handle
    # ✅ Use set for O(1) lookup
    if not hasattr(append_method, '_seen_keys'):
        append_method._seen_keys = set()
    
    key = x["key"]
    if key not in append_method._seen_keys:
        append_method._seen_keys.add(key)
        target_list.append(x)
```

**Hoặc tốt hơn:**
```python
def append_method(x, which="res"):
    target_list = res if which == "res" else res_inherit_not_handle
    seen_keys = {item["key"] for item in target_list}  # ✅ Set comprehension
    if x["key"] not in seen_keys:
        target_list.append(x)
```

---

### 8. **Missing select_related/prefetch_related**

**Vấn đề:**
```python
# app/permission/services/compose_permission_service.py:190-191
for access_rule in query_set:
    access_rule_permission_query_set = AccessRulePermission.objects.filter(
        access_rule=access_rule
    )  # ❌ N queries
```

**Giải pháp:**
```python
# ✅ Prefetch trong compose_access_rules_from_custom_roles
access_rules = (
    AccessRule.objects
    .filter(pk__in=access_rule_ids)
    .prefetch_related('accessrulepermission_set__permission')
)

# Sau đó trong compose_permission_from_access_rules:
for access_rule in query_set:
    # ✅ Sử dụng prefetched data
    access_rule_permissions = access_rule.accessrulepermission_set.all()
    list_permission += AccessRulePermissionSerializer(
        access_rule_permissions, many=True
    ).data
```

---

### 9. **Database Query Optimization**

**Vấn đề:**
```python
# app/permission/services/compose_permission_service.py:384
permissions = generic_user_level.group_permissions.all().values(...)
# ❌ Có thể load nhiều data không cần thiết
```

**Giải pháp:**
```python
# ✅ Chỉ load fields cần thiết, filter sớm
permissions = (
    generic_user_level.group_permissions
    .filter(enabled=True)  # ✅ Filter sớm nếu chỉ cần enabled
    .values("group", "module", "key", "enabled", "name")
    .order_by("group", "module")  # ✅ Order sớm
)
```

---

## 📋 PRIORITY IMPLEMENTATION PLAN

### Phase 1: Critical Performance (Week 1)
1. ✅ Thêm database indexes cho tất cả models
2. ✅ Fix N+1 queries trong `compose_access_rules_from_custom_roles`
3. ✅ Thêm select_related/prefetch_related trong views

### Phase 2: Caching & Optimization (Week 2)
4. ✅ Implement PermissionCacheService
5. ✅ Optimize permission lookups trong loops
6. ✅ Add transaction management

### Phase 3: Code Quality (Week 3)
7. ✅ Improve error handling & logging
8. ✅ Optimize list operations
9. ✅ Code review & testing

---

## 🧪 TESTING RECOMMENDATIONS

1. **Performance Testing:**
   - Load test với 1000+ users
   - Measure query count với django-debug-toolbar
   - Benchmark permission check time

2. **Unit Tests:**
   - Test cache invalidation
   - Test transaction rollback
   - Test permission composition logic

3. **Integration Tests:**
   - Test permission sync với bulk operations
   - Test permission override logic
   - Test multi-level permissions (ORG + CLIENT)

---

## 📊 EXPECTED IMPROVEMENTS

- **Query Count:** Giảm 60-80% số queries
- **Response Time:** Giảm 40-60% thời gian response
- **Database Load:** Giảm 50-70% database load
- **Scalability:** Hỗ trợ 10x số users hiện tại

---

## 🔍 MONITORING

Nên monitor:
- Query execution time cho permission-related queries
- Cache hit rate
- Number of permission sync operations
- Database connection pool usage



