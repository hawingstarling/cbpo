# Phân Tích Workflow Permission Management System

## 📋 Tổng Quan Kiến Trúc

Hệ thống permission management sử dụng **hierarchical permission model** với 3 levels:
- **Organization Level (ORG)**: Permissions cho toàn bộ organization
- **Client Level (CLIENT)**: Permissions cho từng workspace/client
- **User Level**: Permissions được assign cho từng user

---

## 🏗️ Kiến Trúc Components

### Core Models
```
Permission (Base)
    ↓
AccessRule (Rule chứa permissions)
    ↓
CustomRole (Role chứa access rules)
    ↓
OrgClientCustomRoleUser (User có custom roles)
    ↓
OrgClientUserPermission (Cache permissions cuối cùng)
```

### Key Relationships
- **CustomRole** → **CustomRoleAccessRule** → **AccessRule** → **AccessRulePermission** → **Permission**
- **OrganizationUser/UserClient** → **OrgClientCustomRoleUser** → **CustomRole**
- **OrganizationUser/UserClient** → **OrgClientUserPermission** (cached permissions)
- **OrganizationUser/UserClient** → **OverridingOrgClientUserPermission** (override permissions)

---

## 🔄 Workflow Chi Tiết

### 1. INITIAL SETUP - Khởi Tạo Permissions

#### 1.1. Config Permissions từ Static Config
**File:** `app/permission/management/commands/config_permission.py`

```python
# Chạy command: python manage.py config_permission
# Load từ PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL
# Tạo Permission objects trong database
```

**Flow:**
```
Static Config (config.py)
    ↓
config_permission command
    ↓
Permission.objects.bulk_create()
    ↓
Permissions được lưu trong DB
```

**Permissions được định nghĩa theo:**
- **Module**: PF, DS, DC, RA, MAP, MT, TR, SKUFLEX, SA
- **Group**: Mỗi module có nhiều permission groups
- **Level**: CLIENT hoặc ORGANIZATION

---

### 2. USER ONBOARDING - Khi User Join Organization/Client

#### 2.1. User Join Organization
**Trigger:** `CreateOrgMemberEffectListener`

**Flow:**
```
User được tạo OrganizationUser
    ↓
CreateOrgMemberEffectListener.run()
    ↓
OrganizationPermissionManager.run_with_org_user([user_id])
    ↓
__process() - Group users by role
    ↓
__sync() - Sync permissions cho user
    ↓
    ├─ Get default role (ADMIN/STAFF) based on user.role.key
    ├─ Get custom roles của user
    ├─ Compose access rules từ roles
    ├─ Compose permissions từ access rules
    └─ Save vào OrgClientUserPermission (cache)
```

**Code Path:**
```python
# app/tenancies/observer/crud_member/listener_create_org_member_effect.py
CreateOrgMemberEffectListener.run()
    → OrganizationPermissionManager.run_with_org_user([user_id])
        → __process(queryset, ORG_LEVEL_KEY)
            → __sync(objects, default_role_ids)
                → ComposePermissionService.compose_permission_from_access_rules()
                → OrgClientUserPermission.objects.bulk_create()
```

#### 2.2. User Join Client (Workspace)
**Trigger:** `CreateWorkspaceMemberEffectListener`

**Flow:**
```
User được tạo UserClient
    ↓
CreateWorkspaceMemberEffectListener.run()
    ↓
OrganizationPermissionManager.run_with_user_client([client_id], [user_id])
    ↓
__process() - Group users by role
    ↓
__sync() - Sync permissions cho user
    ↓
    ├─ Get default role (ADMIN/STAFF) based on user.role.key
    ├─ Get custom roles của user
    ├─ Compose access rules từ roles
    ├─ Compose permissions từ access rules
    └─ Save vào OrgClientUserPermission (cache)
```

#### 2.3. Client Mới Được Tạo
**Trigger:** `GrantUserClientAccessListener`

**Flow:**
```
Client mới được tạo
    ↓
GrantUserClientAccessListener.run()
    ↓
    ├─ Get all admin/owner users trong organization
    ├─ Bulk create UserClient cho các users này
    └─ OrganizationPermissionManager.process_user_in_ws([client.id])
        → Sync permissions cho tất cả users trong client
```

---

### 3. PERMISSION COMPOSITION - Cách Permissions Được Tính Toán

#### 3.1. Permission Composition Flow
**File:** `app/permission/services/compose_permission_service.py`

**Flow:**
```
User có:
    ├─ Default Role (ADMIN/STAFF) → CustomRole (system)
    ├─ Custom Roles (user-defined) → CustomRole (user)
    └─ Override Permissions → OverridingOrgClientUserPermission

    ↓

1. Collect all CustomRole IDs
    ├─ Default role IDs (from user.role.key)
    └─ Custom role IDs (from OrgClientCustomRoleUser)

    ↓

2. Compose Access Rules
    compose_access_rules_from_custom_roles(role_ids)
        → Query CustomRoleAccessRule by role_ids
        → Get AccessRule objects
        → Return list of AccessRule

    ↓

3. Compose Permissions from Access Rules
    compose_permission_from_access_rules(access_rules, overriding_permissions)
        → For each AccessRule:
            → Get AccessRulePermission objects
            → Extract Permission info (key, group, module, status)
        → Apply Override Permissions (higher priority)
        → Handle INHERIT status → convert to DENY
        → Return list of permissions with status

    ↓

4. Save Composed Permissions
    save_composed_permission(permissions, user_object)
        → Bulk sync vào OrgClientUserPermission
        → Cache permissions cho user
```

#### 3.2. Permission Priority
```
Priority (High → Low):
1. Override Permissions (OverridingOrgClientUserPermission)
2. Custom Roles (theo priority trong OrgClientCustomRoleUser)
3. Default Roles (ADMIN/STAFF based on user.role.key)
```

#### 3.3. Permission Status
- **ALLOW**: Permission được grant
- **DENY**: Permission bị deny
- **INHERIT**: Kế thừa từ parent (sẽ convert thành DENY nếu không có parent)

---

### 4. PERMISSION CHECKING - Khi User Thực Hiện Action

#### 4.1. API Request Flow
**File:** `app/permission/sub_views/base_view.py`, `app/permission/permissions.py`

**Flow:**
```
User gửi API Request
    ↓
JWT Authentication (JWTTokenHandlerAuthentication)
    ↓
Permission Check (IsAdminOrOwnerForActionRoleAndRule)
    ↓
has_permission() hoặc has_object_permission()
    ↓
get_generic_obj_user_current()
    ↓
    ├─ Get OrganizationUserProxy hoặc ClientUserProxy
    └─ Check is_admin_or_manager() hoặc specific permission

    ↓
View Logic
    ↓
    ├─ get_org_client_user_permission_cache_and_grouping()
    │   → Query OrgClientUserPermission (cached)
    │   → Filter by enabled modules
    │   → Group by permission groups
    │   └─ Return permissions
    │
    └─ Check specific permission key
        → Query OrgClientUserPermission.filter(key=permission_key, enabled=True)
```

#### 4.2. Permission Check Methods

**Method 1: Check từ Cached Permissions**
```python
# app/permission/services/compose_permission_service.py
get_org_client_user_permission_cache_and_grouping(generic_user_level, level)
    → Query OrgClientUserPermission (cached table)
    → Filter by module enabled
    → Return grouped permissions
```

**Method 2: Check Specific Permission**
```python
# Query trực tiếp từ cache
OrgClientUserPermission.objects.filter(
    object_id=user_id,
    key=permission_key,
    enabled=True
).exists()
```

---

### 5. PERMISSION MANAGEMENT - Admin Quản Lý Permissions

#### 5.1. Tạo/Update Custom Role
**Endpoint:** `POST/PUT /v1/clients/{client_id}/custom-roles/`

**Flow:**
```
Admin tạo CustomRole
    ↓
CustomRoleSerializer.create() hoặc update()
    ↓
    ├─ Create/Update CustomRole object
    ├─ Create CustomRoleAccessRule objects (link với AccessRule)
    └─ Sync custom roles to users (nếu cần)

    ↓
Sync permissions cho users có custom role này
    ↓
ComposePermissionService.sync_permission_of_user_client_org(affected_user_ids)
```

#### 5.2. Tạo/Update Access Rule
**Endpoint:** `POST/PUT /v1/clients/{client_id}/access-rules/`

**Flow:**
```
Admin tạo AccessRule
    ↓
AccessRuleSerializer.create() hoặc update()
    ↓
    ├─ Create/Update AccessRule object
    ├─ Create AccessRulePermission objects (link với Permission)
    └─ AccessRuleService.update_access_rule_of_client()

    ↓
Sync permissions cho users có custom roles chứa access rule này
    ↓
CustomRoleService.sync_access_rule_relate_custom_roles()
    ↓
    ├─ Get all custom roles chứa access rule này
    ├─ Get all users có custom roles này
    └─ ComposePermissionService.sync_permission_of_user_client_org()
```

#### 5.3. Assign Custom Role cho User
**Endpoint:** `POST /v1/clients/{client_id}/users/{user_id}/compose-permission/`

**Flow:**
```
Admin assign custom roles cho user
    ↓
ComposePermissionView.post()
    ↓
    ├─ Get user's current custom roles
    ├─ Get default roles (ADMIN/STAFF)
    ├─ Compose permissions từ roles
    ├─ Apply override permissions (nếu có)
    └─ Preview permissions (nếu type=PREVIEW)

    ↓
Nếu type=APPROVE:
    ├─ CustomRoleService.sync_custom_roles_of_org_client_users()
    │   → Save custom roles to OrgClientCustomRoleUser
    ├─ ComposePermissionService.save_overriding_permission()
    │   → Save override permissions
    └─ ComposePermissionService.save_composed_permission()
        → Save final permissions to OrgClientUserPermission (cache)
```

#### 5.4. Override Permissions cho User
**Endpoint:** `POST /v1/clients/{client_id}/users/{user_id}/compose-permission/`

**Flow:**
```
Admin override specific permissions cho user
    ↓
ComposePermissionView.post()
    ↓
permissions_groups trong request data
    ↓
ComposePermissionService.save_overriding_permission()
    ↓
    ├─ Delete existing OverridingOrgClientUserPermission
    ├─ Create new OverridingOrgClientUserPermission objects
    └─ Sync permissions để apply override
```

---

### 6. PERMISSION SYNC - Đồng Bộ Permissions

#### 6.1. Khi Nào Permission Được Sync?

**Trigger 1: User được tạo/join**
- `CreateOrgMemberEffectListener` → Sync org permissions
- `CreateWorkspaceMemberEffectListener` → Sync client permissions

**Trigger 2: Custom Role được update**
- CustomRoleSerializer.update() → Sync users có custom role này

**Trigger 3: Access Rule được update**
- AccessRuleSerializer.update() → Sync users có custom roles chứa access rule này

**Trigger 4: User role thay đổi**
- `OrgMemberPermissionEffectListener` → Sync permissions cho user

**Trigger 5: Manual sync**
- `ComposePermissionView.post()` → Admin manually sync permissions

#### 6.2. Sync Process
**File:** `app/permission/services/compose_permission_service.py:sync_permission_of_user_client_org()`

**Flow:**
```
sync_permission_of_user_client_org(affected_object_ids)
    ↓
For each user_id:
    ├─ Get OrganizationUserProxy hoặc ClientUserProxy
    ├─ Get custom roles của user
    ├─ Get default roles (ADMIN/STAFF)
    ├─ Compose access rules từ roles
    ├─ Get override permissions
    ├─ Compose final permissions
    └─ Save to OrgClientUserPermission (cache)
```

**Optimization:**
- `OrganizationPermissionManager.__sync()` sử dụng bulk operations
- Group users by role để giảm queries
- Batch size = 100 users per chunk
- Bulk create với batch_size=5000

---

### 7. PERMISSION CACHING - Cache Mechanism

#### 7.1. Cache Table: `OrgClientUserPermission`
**Purpose:** Cache final computed permissions để tránh tính toán lại mỗi lần check

**Structure:**
```python
OrgClientUserPermission:
    - object_id: ID của OrganizationUser/UserClient
    - content_type: Generic FK
    - key: Permission key
    - group: Permission group
    - module: Module name
    - enabled: True/False (ALLOW/DENY)
    - name: Permission name
```

#### 7.2. Cache Invalidation
**Khi nào cache bị invalidate:**
1. User's custom roles thay đổi
2. Custom role's access rules thay đổi
3. Access rule's permissions thay đổi
4. Override permissions thay đổi
5. User's role thay đổi

**Cách invalidate:**
- Delete old permissions: `OrgClientUserPermission.objects.filter(object_id=user_id).delete()`
- Re-compute và save lại: `save_composed_permission()`

#### 7.3. Cache Usage
**Khi check permissions:**
```python
# Query từ cache thay vì compute lại
permissions = OrgClientUserPermission.objects.filter(
    object_id=user_id,
    enabled=True
).values('key', 'group', 'module')
```

---

### 8. PERMISSION LEVELS - Multi-Level Permissions

#### 8.1. Organization Level
- Permissions áp dụng cho toàn bộ organization
- Stored in: `OrganizationUser` → `OrgClientUserPermission`
- Level: `ORG_LEVEL_KEY`

#### 8.2. Client Level
- Permissions áp dụng cho từng client/workspace
- Stored in: `UserClient` → `OrgClientUserPermission`
- Level: `CLIENT_LEVEL_KEY`
- Filtered by enabled modules của client

#### 8.3. Permission Inheritance
- Organization permissions không tự động inherit xuống client
- Mỗi level có permissions riêng
- User có thể có permissions khác nhau ở org và client level

---

### 9. MODULE-BASED PERMISSIONS

#### 9.1. Module Filtering
**File:** `app/core/context.py`, `app/core/services/app_confg.py`

**Flow:**
```
User request với JWT token
    ↓
PortalAppContextMiddleware.process_request()
    ↓
    ├─ Extract app_name từ JWT
    ├─ Get enabled modules cho app
    └─ Store in AppContext

    ↓
Permission check
    ↓
Filter permissions by enabled modules
    ↓
get_org_client_user_permission_cache_and_grouping()
    ↓
    ├─ Get all permissions từ cache
    └─ Filter by module__in=modules_enabled
```

#### 9.2. Module Configuration
- Mỗi client có enabled modules
- Permissions chỉ được check nếu module enabled
- Disabled modules → permissions tự động disabled

---

### 10. WORKFLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    INITIAL SETUP                             │
│  config_permission command → Permission objects              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              USER ONBOARDING                                 │
│  User joins Org/Client → Listener triggered                 │
│  → OrganizationPermissionManager                            │
│  → Compose permissions → Save to cache                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            PERMISSION COMPOSITION                            │
│  User Roles (Default + Custom)                               │
│  → Access Rules → Permissions                                │
│  → Apply Overrides → Final Permissions                       │
│  → Save to OrgClientUserPermission (cache)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            PERMISSION CHECKING                               │
│  API Request → Permission Check                              │
│  → Query OrgClientUserPermission (cache)                     │
│  → Filter by module → Check permission                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         PERMISSION MANAGEMENT                                │
│  Admin creates/updates CustomRole/AccessRule                 │
│  → Sync affected users                                       │
│  → Re-compose permissions → Update cache                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Key Insights

### Strengths
1. **Caching mechanism**: OrgClientUserPermission giúp check permissions nhanh
2. **Hierarchical model**: Support multi-level permissions (ORG + CLIENT)
3. **Flexible**: Support custom roles, access rules, và override permissions
4. **Observer pattern**: Auto-sync permissions khi có thay đổi

### Weaknesses (N+1 Problems)
1. **Permission composition**: N queries trong loops
2. **Sync process**: N queries cho mỗi user
3. **Missing prefetch**: Thiếu select_related/prefetch_related
4. **No in-memory cache**: Chỉ có DB cache, không có Redis cache

### Performance Bottlenecks
1. `compose_access_rules_from_custom_roles()`: N queries
2. `sync_permission_of_user_client_org()`: N queries per user
3. `get_overriding_permissions_groups()`: N queries cho permissions
4. Permission checks: Query DB mỗi lần (không có in-memory cache)

---

## 📊 Data Flow Summary

```
┌──────────────┐
│   Permission │ (Base permission definitions)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ AccessRule   │ (Rule chứa permissions với status)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ CustomRole   │ (Role chứa access rules)
└──────┬───────┘
       │
       ↓
┌─────────────────────────┐
│ OrgClientCustomRoleUser │ (User có custom roles)
└──────┬──────────────────┘
       │
       ↓
┌─────────────────────────┐
│ OrgClientUserPermission │ (Cached final permissions)
└─────────────────────────┘
```

---

## 🎯 Recommendations

1. **Fix N+1 queries**: Implement solutions trong `N1_QUERY_PROBLEMS_IN_PERMISSION_MANAGEMENT.md`
2. **Add Redis cache**: Cache permissions trong Redis để giảm DB queries
3. **Batch operations**: Optimize sync process với better batching
4. **Add indexes**: Database indexes cho frequently queried fields
5. **Monitoring**: Track permission check performance và cache hit rate



