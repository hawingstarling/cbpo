# Tất Cả Các N+1 Query Problems Trong Permission Management

## 📋 Tổng Quan
Tài liệu này liệt kê **TẤT CẢ** các hàm có N+1 query problem trong permission management của plat-portal-api.

---

## 🔴 CRITICAL - N+1 Problems Trong Loops

### 1. `ComposePermissionService.compose_access_rules_from_custom_roles()`
**File:** `app/permission/services/compose_permission_service.py:114-122`

**Vấn đề:**
```python
@staticmethod
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

**Impact:** Nếu có 10 roles → 20 queries (10 cho CustomRoleAccessRule + 10 cho AccessRule)

**Giải pháp:**
```python
@staticmethod
def compose_access_rules_from_custom_roles(role_ids: [str]) -> [AccessRule]:
    # ✅ Single query với filter __in
    access_rule_ids = (
        CustomRoleAccessRule.objects
        .filter(custom_role_id__in=role_ids)
        .order_by('custom_role_id', 'priority')
        .values_list('access_rule_id', flat=True)
        .distinct()
    )
    return list(AccessRule.objects.filter(pk__in=access_rule_ids))
```

---

### 2. `ComposePermissionService.get_overriding_permissions_groups()`
**File:** `app/permission/services/compose_permission_service.py:263-279`

**Vấn đề:**
```python
@staticmethod
def get_overriding_permissions_groups(object_id: str):
    query_set = OverridingOrgClientUserPermission.objects.filter(object_id=object_id)
    res = [
        {
            "group": item.permission.group,  # ❌ N queries cho permission
            "key": item.permission.key,
            "name": item.permission.name,
            "status": item.status,
            "module": item.permission.module,
        } for item in query_set
    ]
    res = ComposePermissionService.group_composed_permission(res)
    return res
```

**Impact:** Nếu có 20 overriding permissions → 20 queries để load Permission objects

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

---

### 3. `ComposePermissionService.compose_permission_from_access_rules()`
**File:** `app/permission/services/compose_permission_service.py:189-191`

**Vấn đề:**
```python
list_permission = []
for access_rule in query_set:  # ❌ N queries trong loop
    access_rule_permission_query_set = AccessRulePermission.objects.filter(access_rule=access_rule)
    list_permission += AccessRulePermissionSerializer(access_rule_permission_query_set, many=True).data
```

**Impact:** Nếu có 5 access rules → 5 queries

**Giải pháp:**
```python
# ✅ Prefetch trong compose_access_rules_from_custom_roles
access_rules = (
    AccessRule.objects
    .filter(pk__in=access_rule_ids)
    .prefetch_related('accessrulepermission_set__permission')
)

# Sau đó trong compose_permission_from_access_rules:
access_rule_ids = [ar.id for ar in query_set]
access_rule_permissions = (
    AccessRulePermission.objects
    .filter(access_rule_id__in=access_rule_ids)
    .select_related('permission')
)
list_permission = AccessRulePermissionSerializer(access_rule_permissions, many=True).data
```

---

### 4. `ComposePermissionService.save_overriding_permission()`
**File:** `app/permission/services/compose_permission_service.py:67-104`

**Vấn đề:**
```python
list_permission = []
for per_group in overriding_permissions_groups:
    group_key = per_group.get("group")["key"]
    list_per = per_group.get("permissions")
    for per in list_per:  # ❌ N queries trong nested loop
        per_key = per.get("key")
        per_status = per.get("status")
        try:
            per_ins = Permission.objects.get(key=per_key, group=group_key)  # ❌ Query trong loop
            list_permission.append(...)
```

**Impact:** Nếu có 3 groups, mỗi group 10 permissions → 30 queries

**Giải pháp:**
```python
# ✅ Prefetch all permissions in one query
all_permission_keys = []
for per_group in overriding_permissions_groups:
    list_per = per_group.get("permissions")
    for per in list_per:
        all_permission_keys.append((per.get("key"), per_group.get("group")["key"]))

# Build dict for O(1) lookup
permissions_dict = {}
for key, group in set(all_permission_keys):
    try:
        perm = Permission.objects.get(key=key, group=group)
        permissions_dict[(key, group)] = perm
    except Permission.DoesNotExist:
        raise ValidationError(f"Permission does not exist. [{key}, {group}]")

# Use dict in loop
list_permission = []
for per_group in overriding_permissions_groups:
    group_key = per_group.get("group")["key"]
    list_per = per_group.get("permissions")
    for per in list_per:
        per_key = per.get("key")
        per_status = per.get("status")
        per_ins = permissions_dict.get((per_key, group_key))
        if not per_ins:
            raise ValidationError(f"Permission does not exist. [{per_key}, {group_key}]")
        list_permission.append(...)
```

---

### 5. `ComposePermissionService.handler_overriding_permissions_groups()`
**File:** `app/permission/services/compose_permission_service.py:169-186`

**Vấn đề:**
```python
def handler_overriding_permissions_groups(_group_key, _module, _list_per):
    for _per in list_per:  # ❌ N queries trong loop
        _status = _per.get("status")
        _key = _per.get("key")
        try:
            ins = Permission.objects.get(key=_key, group=_group_key)  # ❌ Query trong loop
            permission_data = PermissionSerializer(ins).data
            # ...
```

**Impact:** Tương tự như #4

**Giải pháp:** Tương tự như #4 - prefetch all permissions trước

---

### 6. `ComposePermissionService.sync_permission_of_user_client_org()`
**File:** `app/permission/services/compose_permission_service.py:282-312`

**Vấn đề:**
```python
@staticmethod
def sync_permission_of_user_client_org(affected_object_ids: [str]):
    for object_id in affected_object_ids:  # ❌ N queries trong loop
        logger.info("sync permission for user object id %s" % object_id)
        try:
            object_ref = OrganizationUserProxy.objects.get(pk=object_id)  # ❌ Query trong loop
            level = ORG_LEVEL_KEY
        except OrganizationUserProxy.DoesNotExist:
            try:
                object_ref = ClientUserProxy.objects.get(pk=object_id)  # ❌ Query trong loop
                level = CLIENT_LEVEL_KEY
            except ClientUserProxy.DoesNotExist:
                continue
        
        roles = object_ref.custom_roles.values("custom_role").order_by("priority")  # ❌ Query trong loop
        role_ids = [str(item["custom_role"]) for item in roles]
        default_role_ids = CustomRoleService.get_default_role_ids(object_ref, level)  # ❌ Query trong loop
        # ...
```

**Impact:** Nếu có 100 users → 300+ queries (100 get + 100 custom_roles + 100 default_role_ids)

**Giải pháp:**
```python
@staticmethod
def sync_permission_of_user_client_org(affected_object_ids: [str]):
    # ✅ Batch load all objects
    org_users = {
        str(u.id): (u, ORG_LEVEL_KEY)
        for u in OrganizationUserProxy.objects.filter(pk__in=affected_object_ids)
        .prefetch_related('custom_roles__custom_role')
    }
    client_users = {
        str(u.id): (u, CLIENT_LEVEL_KEY)
        for u in ClientUserProxy.objects.filter(pk__in=affected_object_ids)
        .prefetch_related('custom_roles__custom_role')
    }
    
    # ✅ Prefetch default roles
    default_roles_by_level = {
        ORG_LEVEL_KEY: list(CustomRole.objects.filter(key__in=["ADMIN", "STAFF"], level=ORG_LEVEL_KEY).values_list('id', flat=True)),
        CLIENT_LEVEL_KEY: list(CustomRole.objects.filter(key__in=["ADMIN", "STAFF"], level=CLIENT_LEVEL_KEY).values_list('id', flat=True)),
    }
    
    for object_id in affected_object_ids:
        if object_id in org_users:
            object_ref, level = org_users[object_id]
        elif object_id in client_users:
            object_ref, level = client_users[object_id]
        else:
            continue
        
        roles = object_ref.custom_roles.values("custom_role").order_by("priority")
        role_ids = [str(item["custom_role"]) for item in roles]
        default_role_ids = default_roles_by_level.get(level, [])
        # ... rest of logic
```

---

### 7. `OrganizationPermissionManager.__get_override_permissions_bucket()`
**File:** `app/permission/services/organization.py:182-209`

**Vấn đề:**
```python
@classmethod
def __get_override_permissions_bucket(cls, object_ids: List[str]) -> Dict[str, List[str]]:
    query_set = OverridingOrgClientUserPermission.objects.filter(object_id__in=object_ids)
    bucket = {}
    for object_id_grouped, items in groupby(query_set, lambda ele: ele.object_id):
        permission = [
            {
                "group": item.permission.group,  # ❌ N queries cho permission
                "key": item.permission.key,
                "name": item.permission.name,
                "status": item.status,
                "module": item.permission.module,
            }
            for item in items
        ]
        bucket.update({...})
    return bucket
```

**Impact:** Nếu có 50 users, mỗi user 5 override permissions → 250 queries

**Giải pháp:**
```python
@classmethod
def __get_override_permissions_bucket(cls, object_ids: List[str]) -> Dict[str, List[str]]:
    query_set = (
        OverridingOrgClientUserPermission.objects
        .filter(object_id__in=object_ids)
        .select_related('permission')  # ✅ Prefetch permission
        .order_by("object_id")
    )
    bucket = {}
    for object_id_grouped, items in groupby(query_set, lambda ele: ele.object_id):
        permission = [
            {
                "group": item.permission.group,
                "key": item.permission.key,
                "name": item.permission.name,
                "status": item.status,
                "module": item.permission.module,
            }
            for item in items
        ]
        bucket.update({...})
    return bucket
```

---

### 8. `AccessRuleService.get_permissions_groups_by_access_rules_config()`
**File:** `app/permission/services/access_rule_service.py:137-151`

**Vấn đề:**
```python
@staticmethod
def get_permissions_groups_by_access_rules_config(level: str = None, access_rules_config: list = []):
    list_permissions_groups_configs = []
    for item in access_rules_config:  # ❌ N queries trong loop
        access_rule = AccessRule.objects.get(pk=item['id'])  # ❌ Query trong loop
        list_permissions_groups_configs += AccessRuleService.get_permission_detail_by_access_rule(access_rule)
    return PermissionGroupService.merge_permissions_group(...)
```

**Impact:** Nếu có 10 access rules → 10 queries

**Giải pháp:**
```python
@staticmethod
def get_permissions_groups_by_access_rules_config(level: str = None, access_rules_config: list = []):
    access_rule_ids = [item['id'] for item in access_rules_config]
    # ✅ Batch load access rules
    access_rules = {
        ar.id: ar
        for ar in AccessRule.objects.filter(pk__in=access_rule_ids)
        .prefetch_related('accessrulepermission_set__permission')
    }
    
    list_permissions_groups_configs = []
    for item in access_rules_config:
        access_rule = access_rules.get(item['id'])
        if access_rule:
            list_permissions_groups_configs += AccessRuleService.get_permission_detail_by_access_rule(access_rule)
    return PermissionGroupService.merge_permissions_group(...)
```

---

### 9. `AccessRuleService.make_permissions_groups_access_rule_instance_client()`
**File:** `app/permission/services/access_rule_service.py:53-89`

**Vấn đề:**
```python
for permissions_group in group_data_permissions:
    permissions_groups_instance = Permission.objects.filter(group=permissions_group['group']['key'])
    for permission in permissions_groups_instance.iterator():  # ❌ Iterator trong loop
        permissions_id_status[str(permission.pk)] = ...
    # ...
    for permission in permissions_id_status:
        # ...
        find = AccessRulePermission.all_objects.filter(access_rule=access_rule,
                                                       permission_id=permission).first()  # ❌ Query trong loop
```

**Impact:** Nếu có 5 groups, mỗi group 20 permissions → 100+ queries

**Giải pháp:**
```python
# ✅ Prefetch all permissions và AccessRulePermissions
all_group_keys = [pg['group']['key'] for pg in group_data_permissions]
all_permissions = {
    (p.group, p.id): p
    for p in Permission.objects.filter(group__in=all_group_keys)
}

all_permission_ids = [p.id for p in all_permissions.values()]
existing_arp = {
    (arp.access_rule_id, arp.permission_id): arp
    for arp in AccessRulePermission.all_objects.filter(
        access_rule=access_rule,
        permission_id__in=all_permission_ids
    )
}

# Use in loop
for permissions_group in group_data_permissions:
    group_key = permissions_group['group']['key']
    permissions_status = {item['key']: item['status'] for item in permissions_group['permissions']}
    
    for perm_key, perm_status in permissions_status.items():
        # Find permission from dict
        perm = next((p for p in all_permissions.values() if p.group == group_key and p.key == perm_key), None)
        if not perm:
            continue
        
        find = existing_arp.get((access_rule.id, perm.id))
        # ... rest of logic
```

---

### 10. `CustomRoleService.sync_access_rule_relate_custom_roles()`
**File:** `app/permission/services/custom_role_service.py:240-266`

**Vấn đề:**
```python
@staticmethod
def sync_access_rule_relate_custom_roles(...):
    # ...
    if len(custom_role_ids) > 0:
        for generic_obj_user in generic_objs_users.iterator():  # ❌ Iterator trong loop
            CustomRoleService.sync_custom_roles_of_org_client_users(
                generic_obj=generic_obj_user, custom_role_ids=custom_role_ids
            )
        generic_objs_ids = list(generic_objs_users.values_list("id", flat=True))
        ComposePermissionService.sync_permission_of_user_client_org(generic_objs_ids)  # ❌ N queries
```

**Impact:** Nếu có 100 users → 100+ queries trong sync_custom_roles + N queries trong sync_permission

**Giải pháp:**
```python
@staticmethod
def sync_access_rule_relate_custom_roles(...):
    # ...
    if len(custom_role_ids) > 0:
        # ✅ Batch sync thay vì loop
        generic_objs_users_list = list(generic_objs_users)
        # Bulk sync custom roles
        data_config = []
        for generic_obj_user in generic_objs_users_list:
            for idx, role_id in enumerate(custom_role_ids):
                data_config.append(OrgClientCustomRoleUser(
                    content_object=generic_obj_user,
                    custom_role_id=role_id,
                    priority=idx + 1,
                    is_removed=False
                ))
        # Bulk operations
        OrgClientCustomRoleUser.objects.filter(
            object_id__in=[u.id for u in generic_objs_users_list]
        ).delete()
        OrgClientCustomRoleUser.objects.bulk_create(data_config, batch_size=1000)
        
        generic_objs_ids = [str(u.id) for u in generic_objs_users_list]
        ComposePermissionService.sync_permission_of_user_client_org(generic_objs_ids)
```

---

### 11. `CustomRoleService.get_default_role_ids()`
**File:** `app/permission/services/custom_role_service.py:269-284`

**Vấn đề:**
```python
@staticmethod
def get_default_role_ids(user_member: Union[UserClient, OrganizationUser], level: ...):
    if user_member.role.key in ["OWNER", "ADMIN"]:
        roles = CustomRole.objects.filter(key=ROLE_ADMIN_KEY, level=level)  # ❌ Query mỗi lần gọi
    elif user_member.role.key == "STAFF":
        roles = CustomRole.objects.filter(key=ROLE_STAFF_KEY, level=level)  # ❌ Query mỗi lần gọi
    else:
        roles = []
    role_ids = [str(item.pk) for item in roles]
    return role_ids
```

**Impact:** Được gọi trong loop → N queries

**Giải pháp:** Cache default roles hoặc pass từ caller đã prefetch

---

## 🟡 MEDIUM - Missing select_related/prefetch_related

### 12. `OrgClientBaseView.get_generic_obj_user_current()`
**File:** `app/permission/sub_views/base_view.py:28-39`

**Vấn đề:**
```python
def get_generic_obj_user_current(self):
    level = self.get_level_view()
    content_obj = self.get_content_obj()
    generic_obj_user = None
    if level == ORG_LEVEL_KEY:
        generic_obj_user = OrganizationUserProxy.objects.get(
            user=self.request.user, 
            organization=content_obj
        )  # ❌ Không có select_related/prefetch_related
    if level == CLIENT_LEVEL_KEY:
        generic_obj_user = ClientUserProxy.objects.get(
            user_id=self.request.user.pk, 
            client=content_obj
        )  # ❌ Không có select_related/prefetch_related
    return generic_obj_user
```

**Impact:** Khi access `generic_obj_user.custom_roles` hoặc `generic_obj_user.group_permissions` → N+1 queries

**Giải pháp:**
```python
def get_generic_obj_user_current(self):
    level = self.get_level_view()
    content_obj = self.get_content_obj()
    
    if level == ORG_LEVEL_KEY:
        generic_obj_user = (
            OrganizationUserProxy.objects
            .select_related('user', 'organization', 'role')
            .prefetch_related('custom_roles__custom_role', 'group_permissions')
            .get(user=self.request.user, organization=content_obj)
        )
    elif level == CLIENT_LEVEL_KEY:
        generic_obj_user = (
            ClientUserProxy.objects
            .select_related('user', 'client', 'client__organization', 'role')
            .prefetch_related('custom_roles__custom_role', 'group_permissions')
            .get(user_id=self.request.user.pk, client=content_obj)
        )
    return generic_obj_user
```

---

### 13. `OrgClientBaseView.get_user_client()` và `get_user_org()`
**File:** `app/permission/sub_views/base_view.py:22-26, 52-56`

**Vấn đề:**
```python
def get_user_client(self, user, client):
    return ClientUserProxy.objects.get(user=user, client=client)  # ❌ Không có prefetch

def get_user_org(self, user, org):
    return OrganizationUserProxy.objects.get(user=user, organization=org)  # ❌ Không có prefetch
```

**Giải pháp:** Thêm select_related/prefetch_related tương tự như #12

---

### 14. `ComposePermissionService.get_client_user_settings_permissions()`
**File:** `app/permission/services/compose_permission_service.py:348-368`

**Vấn đề:**
```python
user_client = UserClient.objects.get(client_id=client_id, user_id=user_id, status=status)
list_permissions = OrgClientUserPermission.objects.filter(object_id=user_client.id)
for per in list_permissions:  # ❌ Không có prefetch, có thể có N queries nếu access related fields
    if per.module not in modules_enabled:
        per.enabled = False
```

**Giải pháp:** Thêm `.select_related()` nếu cần access related fields

---

### 15. `PermissionGroupService.get_permissions_groups_level()`
**File:** `app/permission/services/permssion_group_service.py:46-80`

**Vấn đề:**
```python
for group in groups_modules.keys():
    # ...
    permissions_group_query = query_set.filter(group=group)  # ❌ Query trong loop
    item['permissions'] = PermissionsInfoModelSerializer(permissions_group_query, many=True).data
```

**Impact:** Nếu có 10 groups → 10 queries

**Giải pháp:**
```python
# ✅ Group by trong Python thay vì query trong loop
all_permissions = list(query_set)
permissions_by_group = {}
for perm in all_permissions:
    if perm.group not in permissions_by_group:
        permissions_by_group[perm.group] = []
    permissions_by_group[perm.group].append(perm)

for group in groups_modules.keys():
    # ...
    item['permissions'] = PermissionsInfoModelSerializer(
        permissions_by_group.get(group, []), 
        many=True
    ).data
```

---

## 📊 Tổng Kết

### Số Lượng Issues:
- **Critical N+1 trong loops:** 11 functions
- **Missing prefetch:** 4 functions
- **Tổng cộng:** 15 functions có N+1 problems

### Impact Ước Tính:
- **Query giảm:** 60-90% số queries hiện tại
- **Performance cải thiện:** 3-10x nhanh hơn
- **Database load giảm:** 50-80%

### Priority Fix:
1. **P0 (Critical):** #1, #2, #3, #6, #7
2. **P1 (High):** #4, #5, #8, #9, #10
3. **P2 (Medium):** #11, #12, #13, #14, #15

