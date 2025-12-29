# Permission Management - Workflow Chi Tiết & Giải Thích Từng File

## 📋 Mục Lục
1. [Tổng Quan Kiến Trúc](#tổng-quan-kiến-trúc)
2. [Workflow Tổng Thể](#workflow-tổng-thể)
3. [Chi Tiết Từng File](#chi-tiết-từng-file)
4. [Ví Dụ Minh Họa](#ví-dụ-minh-họa)

---

## 🏗️ Tổng Quan Kiến Trúc

### Cấu Trúc Thư Mục
```
app/permission/
├── config_static_varible/      # Static configs, constants
├── models.py                   # Database models
├── services/                    # Business logic
├── sub_views/                  # API views
├── sub_serializers/            # Request/Response serializers
├── management/commands/        # Django management commands
└── exceptions.py               # Custom exceptions
```

### Kiến Trúc Data Model
```
Permission (Base)
    ↓
AccessRulePermission (Link Permission với AccessRule)
    ↓
AccessRule (Rule chứa nhiều permissions)
    ↓
CustomRoleAccessRule (Link AccessRule với CustomRole)
    ↓
CustomRole (Role chứa nhiều access rules)
    ↓
OrgClientCustomRoleUser (User có custom roles)
    ↓
OrgClientUserPermission (Cached final permissions)
```

---

## 🔄 Workflow Tổng Thể

### Phase 1: Initial Setup
```
1. Config Permissions từ static files
2. Run command: config_permission → Tạo Permission objects
3. Run command: config_access_rule → Tạo AccessRule objects
4. Run command: config_custom_role → Tạo CustomRole objects
```

### Phase 2: User Onboarding
```
1. User join Organization/Client
2. Listener triggered → Auto sync permissions
3. Get default role (ADMIN/STAFF) based on user.role.key
4. Compose permissions → Save to cache
```

### Phase 3: Permission Composition
```
1. Collect user's roles (default + custom)
2. Get access rules from roles
3. Get permissions from access rules
4. Apply override permissions
5. Save final permissions to cache
```

### Phase 4: Permission Checking
```
1. API request → Permission check
2. Query from OrgClientUserPermission (cache)
3. Filter by enabled modules
4. Check specific permission
```

---

## 📁 Chi Tiết Từng File

### 1. `config_static_varible/common.py` - Constants & Enums

**Mục đích:** Định nghĩa tất cả constants, enums, và helper functions dùng chung trong permission system.

#### 1.1. Level Constants
```python
ORG_LEVEL_KEY = "ORGANIZATION"      # Permission level cho Organization
CLIENT_LEVEL_KEY = "CLIENT"         # Permission level cho Client/Workspace

LEVEL_ENUM = (
    (ORG_LEVEL_KEY, "Organization"),
    (CLIENT_LEVEL_KEY, "Client"),
)
```

**Tại sao cần:**
- Phân biệt permissions ở Organization level vs Client level
- User có thể có permissions khác nhau ở 2 levels
- Giúp filter và query permissions đúng level

**Ví dụ sử dụng:**
```python
# Khi sync permissions cho user ở client level
level = CLIENT_LEVEL_KEY
permissions = Permission.objects.filter(level=level)

# Khi check permissions, cần biết đang check ở level nào
if level == CLIENT_LEVEL_KEY:
    # Filter by client's enabled modules
    permissions = permissions.filter(module__in=enabled_modules)
```

#### 1.2. Role Constants
```python
ROLE_CUSTOM_KEY = "CUSTOM"          # Custom role do user tạo
ROLE_ADMIN_KEY = "ADMIN"            # Default admin role
ROLE_MANAGER_KEY = "MANAGER"        # Default manager role
ROLE_STAFF_KEY = "STAFF"            # Default staff role

CUSTOM_ROLE_ACCESS_RULE_ENUM = (
    (ROLE_CUSTOM_KEY, "Custom"),
    (ROLE_ADMIN_KEY, "Admin default"),
    (ROLE_MANAGER_KEY, "Manager default"),
    (ROLE_STAFF_KEY, "Staff default"),
)
```

**Tại sao cần:**
- System có 3 default roles: ADMIN, MANAGER, STAFF
- Mỗi user tự động có default role dựa trên `user.role.key`
- Custom roles do admin tạo để customize permissions

**Ví dụ sử dụng:**
```python
# Khi user join, tự động assign default role
if user.role.key in ["OWNER", "ADMIN"]:
    default_role = CustomRole.objects.get(key=ROLE_ADMIN_KEY, level=level)
else:
    default_role = CustomRole.objects.get(key=ROLE_STAFF_KEY, level=level)
```

#### 1.3. Permission Status Constants
```python
STATUS_PERMISSION_DENY_KEY = "DENY"        # Permission bị deny
STATUS_PERMISSION_ALLOW_KEY = "ALLOW"      # Permission được allow
STATUS_PERMISSION_INHERIT_KEY = "INHERIT"  # Kế thừa từ parent

STATUS_PERMISSION_ENUM = (
    (STATUS_PERMISSION_DENY_KEY, "Deny"),
    (STATUS_PERMISSION_ALLOW_KEY, "Allow"),
    (STATUS_PERMISSION_INHERIT_KEY, "Inherit"),
)
```

**Tại sao cần:**
- **ALLOW**: User có permission này
- **DENY**: User không có permission này
- **INHERIT**: Kế thừa từ role khác (sẽ convert thành DENY nếu không có parent)

**Ví dụ sử dụng:**
```python
# Trong AccessRulePermission
AccessRulePermission(
    access_rule=access_rule,
    permission=permission,
    status=STATUS_PERMISSION_ALLOW_KEY  # Allow permission này trong rule
)

# Khi compose permissions
if permission_status == STATUS_PERMISSION_INHERIT_KEY:
    # Tìm trong các roles khác
    # Nếu không tìm thấy → convert thành DENY
    final_status = STATUS_PERMISSION_DENY_KEY
```

#### 1.4. Module Constants
```python
MODULE_ENUM = (
    (MODULE_PF_KEY, MODULE_PF_NAME),      # Precise Financial
    (MODULE_DC_KEY, MODULE_DC_NAME),      # Data Central
    (MODULE_DS_KEY, MODULE_DS_NAME),     # Data Sources
    # ... các modules khác
)

MODULE_DICT = {item[0]: item[1] for item in MODULE_ENUM}
```

**Tại sao cần:**
- Mỗi client có thể enable/disable modules
- Permissions chỉ có hiệu lực nếu module enabled
- Giúp filter permissions theo module

**Ví dụ sử dụng:**
```python
# Khi check permissions, filter by enabled modules
enabled_modules = AppContext.instance().module_enabled(client_id)
permissions = OrgClientUserPermission.objects.filter(
    object_id=user_id,
    module__in=enabled_modules,
    enabled=True
)
```

#### 1.5. Helper Functions
```python
def get_all_permissions_groups_from_module_config(
    module_config: dict,
    priority_config_dict: dict = None,
    priority_status_for_left: str = STATUS_PERMISSION_ALLOW_KEY,
):
    """
    Convert module config thành permissions groups với status
    
    Args:
        module_config: Config của module (từ permissions_groups/client/pf/precise_financial.py)
        priority_config_dict: Dict override status cho specific permissions
        priority_status_for_left: Default status cho permissions không có trong priority_config_dict
    
    Returns:
        Dict: {group_key: [{"key": perm_key, "status": "ALLOW/DENY"}, ...]}
    """
```

**Tại sao cần:**
- Module config định nghĩa permissions theo groups
- Function này convert sang format dùng cho AccessRule
- Cho phép override status cho specific permissions

**Ví dụ sử dụng:**
```python
# Trong config_access_rule_client.py
access_rule_config = {
    "name": "PF Sale Full Access",
    "permissions_groups": get_all_permissions_groups_from_module_config(
        module_config=permission_module_pf_config,
        priority_config_dict={
            SALE_VIEW_ALL: STATUS_PERMISSION_ALLOW_KEY,
            SALE_EDIT: STATUS_PERMISSION_ALLOW_KEY,
        },
        priority_status_for_left=STATUS_PERMISSION_DENY_KEY,  # Các permissions khác = DENY
    )
}
```

---

### 2. `config_static_varible/config.py` - Main Config

**Mục đích:** Tổng hợp tất cả module configs thành một dict duy nhất.

```python
PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL = {
    **permission_module_pf_config,      # Precise Financial
    **permission_module_ds_config,      # Data Sources
    **permission_module_dc_config,      # Data Central
    **permission_module_ra_config,      # Report Application
    **permission_module_map_watcher_config,  # Map Watcher
    **permission_module_mt_config,      # Matrix
    **permission_module_tr_config,      # Transit
    **permission_module_skuflex_config,  # SKUFlex
    **permission_module_sa_config,      # System Admin
}
```

**Tại sao cần:**
- Centralized config: Tất cả permissions được định nghĩa ở đây
- Dùng cho command `config_permission` để tạo Permission objects
- Dùng cho việc generate AccessRule configs

**Ví dụ sử dụng:**
```python
# Trong config_permission command
for group_key in PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL.keys():
    group_config = PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL[group_key]
    module = group_config["module"]
    
    for permission in group_config["permissions"]:
        Permission.objects.create(
            key=permission["key"],
            name=permission["name"],
            group=group_key,
            module=module,
            level=CLIENT_LEVEL_KEY
        )
```

---

### 3. `models.py` - Database Models

#### 3.1. `Permission` Model
```python
class Permission(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    key = models.CharField(max_length=50, choices=PERMISSION_ENUM, unique=True)
    name = models.CharField(max_length=100)
    module = models.CharField(max_length=50, choices=MODULE_ENUM)
    group = models.CharField(max_length=50, choices=GROUP_PERMISSION_ENUM)
    level = models.CharField(max_length=50, choices=LEVEL_ENUM)
```

**Tại sao cần:**
- Base permission definition trong system
- Mỗi permission có: key (unique), name, module, group, level
- Dùng làm reference cho AccessRulePermission

**Ví dụ:**
```python
Permission(
    key="SALE_VIEW_ALL",
    name="View All Sales",
    module="PF",
    group="SALE_GROUP",
    level="CLIENT"
)
```

#### 3.2. `AccessRule` Model
```python
class AccessRule(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    key = models.CharField(max_length=50, choices=CUSTOM_ROLE_ACCESS_RULE_ENUM)
    name = models.CharField(max_length=100, null=True)
    level = models.CharField(max_length=50, choices=LEVEL_ENUM)
    content_type = models.ForeignKey(ContentType, null=True)  # Generic FK
    object_id = models.UUIDField(null=True)  # ID của Organization/Client
    content_object = GenericForeignKey("content_type", "object_id")
    type_created = models.CharField(choices=CUSTOM_TYPE_CREATED_ENUM)  # SYSTEM or USER
    owner = models.ForeignKey(User, null=True)
    module = models.CharField(max_length=50, null=True)
```

**Tại sao cần:**
- AccessRule là container chứa nhiều permissions với status
- Có thể là system default (type_created=SYSTEM) hoặc user-created
- Generic FK cho phép link với Organization hoặc Client

**Ví dụ:**
```python
# System default access rule
AccessRule(
    key="PF_SALE_FULL",
    name="PF Sale Full Access",
    level="CLIENT",
    type_created="SYSTEM",
    module="PF"
)

# User-created access rule
AccessRule(
    key="CUSTOM",
    name="My Custom Rule",
    level="CLIENT",
    content_object=client,  # Belongs to specific client
    type_created="USER",
    owner=admin_user
)
```

#### 3.3. `AccessRulePermission` Model
```python
class AccessRulePermission(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    access_rule = models.ForeignKey(AccessRule, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_PERMISSION_ENUM,
        default=STATUS_PERMISSION_ALLOW_KEY
    )
```

**Tại sao cần:**
- Link AccessRule với Permission
- Status cho biết permission này trong rule là ALLOW/DENY/INHERIT
- Một AccessRule có thể chứa nhiều AccessRulePermission

**Ví dụ:**
```python
# AccessRule "PF_SALE_FULL" chứa permission "SALE_VIEW_ALL" với status ALLOW
AccessRulePermission(
    access_rule=pf_sale_full_rule,
    permission=sale_view_all_permission,
    status="ALLOW"
)

# AccessRule "PF_SALE_READ_ONLY" chứa permission "SALE_EDIT" với status DENY
AccessRulePermission(
    access_rule=pf_sale_readonly_rule,
    permission=sale_edit_permission,
    status="DENY"
)
```

#### 3.4. `CustomRole` Model
```python
class CustomRole(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    key = models.CharField(max_length=10, choices=CUSTOM_ROLE_ACCESS_RULE_ENUM)
    name = models.CharField(max_length=100, null=True)
    level = models.CharField(max_length=50, choices=LEVEL_ENUM)
    content_type = models.ForeignKey(ContentType, null=True)  # Generic FK
    object_id = models.UUIDField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    type_created = models.CharField(choices=CUSTOM_TYPE_CREATED_ENUM)
```

**Tại sao cần:**
- CustomRole là container chứa nhiều AccessRules
- Có thể là system default (ADMIN, STAFF) hoặc user-created
- Generic FK cho phép link với Organization hoặc Client

**Ví dụ:**
```python
# System default role
CustomRole(
    key="ADMIN",
    name="Admin default",
    level="CLIENT",
    type_created="SYSTEM"
)

# User-created role
CustomRole(
    key="CUSTOM",
    name="Sales Manager",
    level="CLIENT",
    content_object=client,
    owner=admin_user,
    type_created="USER"
)
```

#### 3.5. `CustomRoleAccessRule` Model
```python
class CustomRoleAccessRule(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    custom_role = models.ForeignKey(CustomRole, on_delete=models.CASCADE)
    access_rule = models.ForeignKey(AccessRule, on_delete=models.CASCADE)
    priority = models.IntegerField()
```

**Tại sao cần:**
- Link CustomRole với AccessRule
- Priority quyết định thứ tự merge permissions (priority thấp hơn = merge trước)
- Một CustomRole có thể chứa nhiều AccessRules với priority khác nhau

**Ví dụ:**
```python
# CustomRole "Sales Manager" có 2 access rules
CustomRoleAccessRule(
    custom_role=sales_manager_role,
    access_rule=pf_sale_full_rule,
    priority=1  # Merge trước
)

CustomRoleAccessRule(
    custom_role=sales_manager_role,
    access_rule=pf_readonly_rule,
    priority=2  # Merge sau (override permissions từ priority 1)
)
```

#### 3.6. `OrgClientCustomRoleUser` Model
```python
class OrgClientCustomRoleUser(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    content_type = models.ForeignKey(ContentType)  # Generic FK
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")  # OrganizationUser or UserClient
    custom_role = models.ForeignKey(CustomRole, on_delete=models.CASCADE)
    priority = models.IntegerField()
```

**Tại sao cần:**
- Link User (OrganizationUser/UserClient) với CustomRole
- Priority quyết định thứ tự merge permissions từ các roles
- User có thể có nhiều custom roles

**Ví dụ:**
```python
# User có 2 custom roles
OrgClientCustomRoleUser(
    content_object=user_client,  # UserClient object
    custom_role=sales_manager_role,
    priority=1
)

OrgClientCustomRoleUser(
    content_object=user_client,
    custom_role=report_viewer_role,
    priority=2  # Merge sau
)
```

#### 3.7. `OrgClientUserPermission` Model (Cache Table)
```python
class OrgClientUserPermission(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    content_type = models.ForeignKey(ContentType)  # Generic FK
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")  # OrganizationUser or UserClient
    module = models.CharField(max_length=50, choices=MODULE_ENUM)
    group = models.CharField(max_length=50, choices=GROUP_PERMISSION_ENUM)
    key = models.CharField(max_length=50, choices=PERMISSION_ENUM)
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)  # True = ALLOW, False = DENY
```

**Tại sao cần:**
- **Cache table**: Lưu final computed permissions để tránh tính toán lại mỗi lần check
- Khi check permission, query từ đây thay vì compose lại từ roles
- enabled=True → ALLOW, enabled=False → DENY

**Ví dụ:**
```python
# Final permissions của user sau khi compose
OrgClientUserPermission(
    content_object=user_client,
    key="SALE_VIEW_ALL",
    group="SALE_GROUP",
    module="PF",
    enabled=True  # User có permission này
)

OrgClientUserPermission(
    content_object=user_client,
    key="SALE_EDIT",
    group="SALE_GROUP",
    module="PF",
    enabled=False  # User không có permission này
)
```

#### 3.8. `OverridingOrgClientUserPermission` Model
```python
class OverridingOrgClientUserPermission(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_PERMISSION_ENUM)
    content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
```

**Tại sao cần:**
- Override permissions: Admin có thể override specific permissions cho user
- Priority cao nhất: Override permissions được apply sau cùng
- Cho phép fine-grained control: Grant/deny specific permissions không phụ thuộc vào roles

**Ví dụ:**
```python
# Admin override permission cho user
OverridingOrgClientUserPermission(
    content_object=user_client,
    permission=sale_delete_permission,
    status="ALLOW"  # Override: Grant permission này dù role không có
)
```

---

### 4. `services/compose_permission_service.py` - Core Permission Logic

**Mục đích:** Service chính để compose (tính toán) permissions từ roles và access rules.

#### 4.1. `compose_access_rules_from_custom_roles()`
```python
@staticmethod
def compose_access_rules_from_custom_roles(role_ids: [str]) -> [AccessRule]:
    """
    Lấy tất cả AccessRules từ list CustomRole IDs
    
    Args:
        role_ids: List CustomRole IDs
    
    Returns:
        List AccessRule objects
    """
    query_set = []
    for role_id in role_ids:
        acc_rule_ids = (
            CustomRoleAccessRule.objects.filter(custom_role_id=role_id)
            .values("access_rule").order_by("priority")
        )
        access_rules = AccessRule.objects.filter(pk__in=acc_rule_ids)
        query_set.extend(access_rules)
    return query_set
```

**Tại sao cần:**
- User có nhiều CustomRoles → Mỗi role có nhiều AccessRules
- Function này collect tất cả AccessRules từ các roles
- Order by priority để merge đúng thứ tự

**Ví dụ:**
```python
# User có 2 roles: [sales_manager_role_id, report_viewer_role_id]
role_ids = [sales_manager_role_id, report_viewer_role_id]

# sales_manager_role có access rules: [pf_sale_full, pf_readonly] (priority 1, 2)
# report_viewer_role có access rules: [pf_readonly] (priority 1)

access_rules = compose_access_rules_from_custom_roles(role_ids)
# Returns: [pf_sale_full, pf_readonly (from sales_manager), pf_readonly (from report_viewer)]
```

#### 4.2. `compose_permission_from_access_rules()`
```python
@staticmethod
def compose_permission_from_access_rules(
    query_set: [AccessRule], 
    overriding_permissions_groups=None
) -> [dict]:
    """
    Compose permissions từ list AccessRules
    
    Args:
        query_set: List AccessRule objects
        overriding_permissions_groups: Override permissions (priority cao nhất)
    
    Returns:
        List dict: [{"key": perm_key, "name": perm_name, "group": group, "module": module, "status": "ALLOW/DENY"}, ...]
    """
```

**Tại sao cần:**
- Mỗi AccessRule chứa nhiều AccessRulePermission
- Function này merge tất cả permissions từ các AccessRules
- Apply override permissions (priority cao nhất)
- Handle INHERIT status → convert thành DENY nếu không có parent

**Ví dụ:**
```python
# AccessRule 1: pf_sale_full
#   - SALE_VIEW_ALL: ALLOW
#   - SALE_EDIT: ALLOW
#   - SALE_DELETE: ALLOW

# AccessRule 2: pf_readonly (priority cao hơn)
#   - SALE_VIEW_ALL: ALLOW
#   - SALE_EDIT: DENY
#   - SALE_DELETE: DENY

# Override permissions:
#   - SALE_DELETE: ALLOW

# Result:
permissions = [
    {"key": "SALE_VIEW_ALL", "status": "ALLOW"},  # From rule 1, rule 2 không override
    {"key": "SALE_EDIT", "status": "DENY"},        # Rule 2 override rule 1
    {"key": "SALE_DELETE", "status": "ALLOW"}     # Override permission (priority cao nhất)
]
```

#### 4.3. `save_composed_permission()`
```python
@staticmethod
def save_composed_permission(permission, object_reference: UserClient or OrganizationUser):
    """
    Save composed permissions vào cache table
    
    Args:
        permission: List dict permissions từ compose_permission_from_access_rules()
        object_reference: OrganizationUser hoặc UserClient object
    """
    res = [
        OrgClientUserPermission(
            key=per["key"],
            module=per["module"],
            name=per["name"],
            group=per["group"],
            enabled=True if per["status"] == STATUS_PERMISSION_ALLOW_KEY else False,
            content_object=object_reference,
        ) for per in permission
    ]
    bulk_sync(
        new_models=res,
        filters=Q(object_id=object_reference.id),
        fields=["module", "module_name", "group", "key", "name", "enabled"],
        key_fields=("group", "key"),
    )
```

**Tại sao cần:**
- Save final permissions vào cache table để check nhanh
- Bulk sync để update/insert hiệu quả
- enabled=True → ALLOW, enabled=False → DENY

**Ví dụ:**
```python
permissions = [
    {"key": "SALE_VIEW_ALL", "status": "ALLOW", "module": "PF", "group": "SALE_GROUP"},
    {"key": "SALE_EDIT", "status": "DENY", "module": "PF", "group": "SALE_GROUP"},
]

save_composed_permission(permissions, user_client)

# Tạo/update records trong OrgClientUserPermission:
# - SALE_VIEW_ALL: enabled=True
# - SALE_EDIT: enabled=False
```

#### 4.4. `sync_permission_of_user_client_org()`
```python
@staticmethod
def sync_permission_of_user_client_org(affected_object_ids: [str]):
    """
    Sync permissions cho list users
    
    Args:
        affected_object_ids: List OrganizationUser/UserClient IDs
    """
    for object_id in affected_object_ids:
        # Get user object
        try:
            object_ref = OrganizationUserProxy.objects.get(pk=object_id)
            level = ORG_LEVEL_KEY
        except:
            object_ref = ClientUserProxy.objects.get(pk=object_id)
            level = CLIENT_LEVEL_KEY
        
        # Get roles
        roles = object_ref.custom_roles.values("custom_role").order_by("priority")
        role_ids = [str(item["custom_role"]) for item in roles]
        default_role_ids = CustomRoleService.get_default_role_ids(object_ref, level)
        composed_role_ids = [*role_ids, *default_role_ids]
        
        # Compose permissions
        access_rule_query_set = compose_access_rules_from_custom_roles(composed_role_ids)
        overriding_permissions_groups = get_overriding_permissions_groups(object_id)
        res = compose_permission_from_access_rules(access_rule_query_set, overriding_permissions_groups)
        
        # Save to cache
        save_composed_permission(res, object_ref)
```

**Tại sao cần:**
- Sync permissions khi có thay đổi (role thay đổi, access rule update, etc.)
- Re-compute permissions từ roles → Save to cache
- Được gọi từ listeners hoặc manual sync

**Ví dụ:**
```python
# Khi admin update AccessRule "pf_sale_full"
# → Sync tất cả users có custom roles chứa access rule này

affected_user_ids = ["user1_id", "user2_id", "user3_id"]
sync_permission_of_user_client_org(affected_user_ids)

# For each user:
# 1. Get roles
# 2. Get access rules from roles
# 3. Compose permissions
# 4. Save to cache
```

---

### 5. `services/organization.py` - Bulk Permission Management

**Mục đích:** Quản lý permissions cho nhiều users cùng lúc (bulk operations).

#### 5.1. `OrganizationPermissionManager` Class
```python
class OrganizationPermissionManager:
    def __init__(self, organization_id: str):
        self.organization_id = organization_id
    
    def run_with_user_client(self, client_ids: List[str], user_ids: List[str]):
        """Grant permissions cho UserClient"""
    
    def run_with_org_user(self, user_ids: List[str]):
        """Grant permissions cho OrganizationUser"""
    
    def run(self):
        """Grant permissions cho toàn bộ organization"""
```

**Tại sao cần:**
- Khi có nhiều users cần sync permissions cùng lúc
- Optimize bằng cách group users by role → Giảm queries
- Bulk operations thay vì sync từng user

**Ví dụ:**
```python
# Khi client mới được tạo → Auto assign permissions cho admin/owner users
permission_manager = OrganizationPermissionManager(organization_id)
permission_manager.run_with_user_client(
    client_ids=[new_client_id],
    user_ids=[admin1_id, admin2_id, owner_id]
)

# Process:
# 1. Get all users with same role
# 2. Get default role for that role key
# 3. Bulk compose permissions
# 4. Bulk save to cache
```

---

### 6. `sub_views/compose_final_permission_view.py` - API Endpoint

**Mục đích:** API endpoint để admin assign custom roles và override permissions cho user.

#### 6.1. `ComposePermissionView` Class
```python
class ComposePermissionView(OrgClientBaseView, APIView):
    permission_classes = (IsAdminOrOwnerForActionRoleAndRule,)
    
    def get(self, request, *args, **kwargs):
        """Get current permissions của user"""
    
    def post(self, request, *args, **kwargs):
        """Assign roles và override permissions cho user"""
```

**Tại sao cần:**
- Admin UI cần endpoint để manage user permissions
- Preview permissions trước khi approve
- Save roles và override permissions

**Ví dụ request:**
```json
POST /v1/clients/{client_id}/users/{user_id}/compose-permission/
{
    "type": "APPROVE",  // hoặc "PREVIEW"
    "roles": [
        {"id": "role1_id", "priority": 1},
        {"id": "role2_id", "priority": 2}
    ],
    "permissions_groups": [
        {
            "group": {"key": "SALE_GROUP"},
            "module": {"key": "PF"},
            "permissions": [
                {"key": "SALE_DELETE", "status": "ALLOW"}  // Override
            ]
        }
    ]
}
```

**Flow:**
```
1. Validate roles (check exists, check priority)
2. Get default roles
3. Compose permissions từ roles
4. Apply override permissions
5. If type=APPROVE:
   - Save custom roles to OrgClientCustomRoleUser
   - Save override permissions to OverridingOrgClientUserPermission
   - Save final permissions to OrgClientUserPermission
6. Return grouped permissions
```

---

## 🎯 Ví Dụ Minh Họa Workflow

### Scenario: User Join Client và Được Assign Custom Role

#### Step 1: User Join Client
```python
# User "john@example.com" join Client "client_123"
user_client = UserClient.objects.create(
    user=john_user,
    client=client_123,
    role=staff_role  # role.key = "STAFF"
)

# Listener triggered
CreateWorkspaceMemberEffectListener.run(
    user_id=john_user.id,
    organization_id=org.id,
    client_id=client_123.id
)
```

#### Step 2: Auto Sync Permissions
```python
# OrganizationPermissionManager.run_with_user_client()
permission_manager = OrganizationPermissionManager(org.id)
permission_manager.run_with_user_client(
    client_ids=[client_123.id],
    user_ids=[john_user.id]
)

# Process:
# 1. Get user_client với role
user_client = UserClient.objects.get(user=john_user, client=client_123)

# 2. Get default role (STAFF)
default_role = CustomRole.objects.get(key="STAFF", level="CLIENT")

# 3. Get custom roles (chưa có)
custom_roles = user_client.custom_roles.all()  # Empty

# 4. Compose roles
role_ids = [default_role.id]  # Chỉ có default role

# 5. Get access rules from default role
access_rules = compose_access_rules_from_custom_roles(role_ids)
# Returns: [AccessRule "STAFF_DEFAULT"] (system default)

# 6. Compose permissions
permissions = compose_permission_from_access_rules(access_rules)
# Returns: [
#   {"key": "SALE_VIEW_ALL", "status": "ALLOW", ...},
#   {"key": "SALE_EDIT", "status": "DENY", ...},
#   ...
# ]

# 7. Save to cache
save_composed_permission(permissions, user_client)
# Creates records in OrgClientUserPermission
```

#### Step 3: Admin Assign Custom Role
```python
# Admin assign custom role "Sales Manager" cho john
POST /v1/clients/client_123/users/john_id/compose-permission/
{
    "type": "APPROVE",
    "roles": [
        {"id": "sales_manager_role_id", "priority": 1}
    ]
}

# Process:
# 1. Validate roles
# 2. Get default role (STAFF)
default_role_ids = [staff_default_role.id]

# 3. Compose roles
role_ids = [sales_manager_role_id, staff_default_role.id]

# 4. Get access rules
access_rules = compose_access_rules_from_custom_roles(role_ids)
# Returns: [
#   AccessRule "PF_SALE_FULL" (from sales_manager_role, priority=1),
#   AccessRule "STAFF_DEFAULT" (from default role)
# ]

# 5. Compose permissions (merge theo priority)
permissions = compose_permission_from_access_rules(access_rules)
# PF_SALE_FULL có: SALE_VIEW_ALL=ALLOW, SALE_EDIT=ALLOW, SALE_DELETE=ALLOW
# STAFF_DEFAULT có: SALE_VIEW_ALL=ALLOW, SALE_EDIT=DENY, SALE_DELETE=DENY
# Result: SALE_VIEW_ALL=ALLOW, SALE_EDIT=ALLOW (from PF_SALE_FULL), SALE_DELETE=ALLOW

# 6. Save
save_composed_permission(permissions, user_client)
# Update OrgClientUserPermission records
```

#### Step 4: Permission Check
```python
# User john request API
GET /v1/clients/client_123/sales/

# Permission check
permission_checker.has_permission(request, view)
    → get_generic_obj_user_current()
        → ClientUserProxy.objects.get(user=john, client=client_123)
    
    → Check permission
        → OrgClientUserPermission.objects.filter(
            object_id=user_client.id,
            key="SALE_VIEW_ALL",
            enabled=True
        ).exists()  # True → Allow request
```

---

## 📊 Summary

### Key Components
1. **Config Files**: Định nghĩa permissions, access rules, custom roles
2. **Models**: Database structure cho permissions system
3. **Services**: Business logic để compose và sync permissions
4. **Views**: API endpoints để manage permissions
5. **Listeners**: Auto-sync permissions khi có thay đổi

### Workflow Summary
```
1. Setup: Config permissions → Create Permission objects
2. User Join: Auto assign default role → Compose permissions → Save to cache
3. Admin Assign: Assign custom roles → Re-compose permissions → Update cache
4. Permission Check: Query from cache → Filter by module → Check permission
```

### Key Concepts
- **Permission**: Base permission definition
- **AccessRule**: Container chứa permissions với status
- **CustomRole**: Container chứa access rules
- **Cache**: OrgClientUserPermission lưu final permissions để check nhanh
- **Override**: Fine-grained control cho specific permissions



