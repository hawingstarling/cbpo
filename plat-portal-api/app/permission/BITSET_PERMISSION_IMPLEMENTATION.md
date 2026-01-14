# Bitset Permission System Implementation

## Tổng Quan

Hệ thống permission đã được implement lại sử dụng **bitset/bitwise operations** tương tự như Discord's permission system. Tất cả tính toán permission đều sử dụng bitwise operations (OR, AND, NOT) để đảm bảo hiệu suất cao và dễ mở rộng.

## Kiến Trúc

### Core Components

1. **`bitset_permissions.py`**: Module chính chứa:
   - `PermissionBitsetRegistry`: Registry để map permission keys với bit positions
   - `PermissionBitset`: Class đại diện cho một set permissions sử dụng bitwise operations
   - Helper functions: `from_permission_list()`, `to_permission_list()`, `initialize_permission_registry()`

2. **Cấu trúc Bitset**:
   - `BITS_PER_SEGMENT = 64`: Mỗi segment có 64 bits
   - Mỗi module có thể có nhiều segments
   - Mỗi permission được assign một unique bit position trong module của nó

### Bitwise Operations

Tất cả operations đều sử dụng bitwise:

```python
# Allow permission: OR operation
allow |= bit_value

# Deny permission: OR operation + remove from allow
deny |= bit_value
allow &= ~bit_value

# Check permission: AND operation
has_permission = (allow & bit_value) == bit_value and (deny & bit_value) != bit_value

# Combine bitsets: Similar to Discord's overwrite logic
# 1. Apply deny first (deny overrides allow)
result_deny |= other.deny
result_allow &= ~other.deny
# 2. Then apply allow
result_allow |= other.allow
```

## Workflow

### 1. Initialization

Khi app khởi động, `PermissionConfig.ready()` sẽ gọi `initialize_permission_registry()`:
- Load tất cả permissions từ `PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL`
- Map mỗi permission key với một unique bit position
- Store metadata (name, group, module, segment, offset)

### 2. Permission Composition

Khi compose permissions từ access rules:

1. **Collect permissions**: Lấy tất cả permissions từ access rules
2. **Create bitset**: Convert permissions thành `PermissionBitset` sử dụng `from_permission_list()`
   - Allow permissions → set bits trong `allow` mask
   - Deny permissions → set bits trong `deny` mask
3. **Combine bitsets**: Sử dụng `combine()` method với logic:
   - Deny takes precedence (deny overrides allow)
   - Then apply allow
4. **Apply overrides**: Overriding permissions được combine sau cùng (highest priority)
5. **Convert back**: Convert bitset về list format sử dụng `to_permission_list()`

### 3. Permission Checking

Để check một permission:

```python
bitset = PermissionBitset(allow=..., deny=...)
has_perm = bitset.has_permission("permission_key")
```

Logic:
```python
def has_permission(self, permission_key: str) -> bool:
    perm_bit = registry.get_bit(permission_key)
    if not perm_bit:
        return False
    
    module, segment, bit_val = perm_bit
    
    # Check if denied
    if self.deny & bit_val == bit_val:
        return False
    
    # Check if allowed
    return self.allow & bit_val == bit_val
```

## Backward Compatibility

### Database Models
- **Không thay đổi**: Tất cả models giữ nguyên
- `OrgClientUserPermission` vẫn lưu permissions dạng individual records
- `OverridingOrgClientUserPermission` vẫn hoạt động như cũ

### API Response Format
- **Không thay đổi**: Response format giữ nguyên
- Vẫn trả về list permissions với status (ALLOW/DENY)
- Vẫn group theo module và group

### Internal Logic
- **Thay đổi**: Logic tính toán permission sử dụng bitset
- Kết quả cuối cùng vẫn giống như trước (backward compatible)

## Benefits

1. **Performance**: Bitwise operations rất nhanh, O(1) cho mỗi operation
2. **Scalability**: Có thể mở rộng lên nhiều segments nếu cần
3. **Memory**: Bitset compact hơn so với lưu nhiều records
4. **Consistency**: Logic rõ ràng, dễ debug và maintain
5. **Flexibility**: Dễ dàng thêm permissions mới mà không cần migration

## Example Usage

```python
from app.permission.bitset_permissions import (
    PermissionBitset,
    from_permission_list,
    to_permission_list
)

# Create bitset from permission list
permissions = [
    {"key": "SALE_VIEW_ALL", "status": "ALLOW"},
    {"key": "SALE_EDIT", "status": "DENY"},
]
bitset = from_permission_list(permissions)

# Check permission
has_view = bitset.has_permission("SALE_VIEW_ALL")  # True
has_edit = bitset.has_permission("SALE_EDIT")  # False

# Combine with another bitset
other_bitset = PermissionBitset()
other_bitset.allow_permission("SALE_IMPORT")
combined = bitset.combine(other_bitset)

# Convert back to list
result = to_permission_list(combined)
```

## Files Modified

1. **`app/permission/bitset_permissions.py`** (NEW): Core bitset implementation
2. **`app/permission/services/compose_permission_service.py`**: Updated `compose_permission_from_access_rules()` to use bitset
3. **`app/permission/apps.py`**: Added registry initialization in `ready()`

## Notes

- Registry được initialize một lần khi app start
- Permissions được auto-assign bit positions theo thứ tự trong config
- Nếu một permission không có trong registry, nó sẽ bị skip (không crash)
- Inherit permissions được handle riêng và default thành DENY nếu không được set






