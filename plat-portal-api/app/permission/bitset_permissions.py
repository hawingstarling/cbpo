"""
Bitset Permission System
Implements Discord-style permission system using bitwise operations.

Each permission is assigned a unique bit position within its module.
Permissions are stored as integers (or strings for large values) and calculated using bitwise operations.

Structure:
- BITS_PER_SEGMENT = 64 (bits per segment)
- Each module has its own segment(s)
- PermissionBit = (module, segment, bit_value)
"""

from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

BITS_PER_SEGMENT = 64

# PermissionBit = Tuple[str, int, int]  # (module, segment, bit_value)
PermissionBit = Tuple[str, int, int]


def bit(module: str, segment: int, offset: int) -> PermissionBit:
    """
    Create a permission bit definition.
    
    Args:
        module: Module name (e.g., 'PF', 'DC', 'DS')
        segment: Segment index (0-based, each segment has 64 bits)
        offset: Bit offset within segment (0-63)
    
    Returns:
        Tuple of (module, segment, bit_value)
    
    Raises:
        ValueError: If offset >= 64
    """
    if offset >= BITS_PER_SEGMENT:
        raise ValueError(f"Offset must be < {BITS_PER_SEGMENT}, got {offset}")
    return (module, segment, 1 << offset)


class PermissionBitsetRegistry:
    """
    Registry for mapping permission keys to their bit positions.
    Maintains a mapping of all permissions to their bit values.
    """
    
    def __init__(self):
        self._permission_to_bit: Dict[str, PermissionBit] = {}
        self._bit_to_permission: Dict[PermissionBit, str] = {}
        self._module_segments: Dict[str, int] = defaultdict(int)  # Track max segment per module
        self._permission_info: Dict[str, Dict] = {}  # Store permission metadata
    
    def register_permission(
        self,
        permission_key: str,
        module: str,
        offset: Optional[int] = None,
        segment: Optional[int] = None,
        name: Optional[str] = None,
        group: Optional[str] = None
    ) -> PermissionBit:
        """
        Register a permission with its bit position.
        
        Args:
            permission_key: Unique permission key
            module: Module name
            offset: Bit offset (auto-assigned if None)
            segment: Segment index (auto-assigned if None)
            name: Permission name
            group: Permission group
        
        Returns:
            PermissionBit tuple
        """
        if permission_key in self._permission_to_bit:
            return self._permission_to_bit[permission_key]
        
        # Auto-assign segment and offset if not provided
        if segment is None:
            segment = self._module_segments[module]
        
        if offset is None:
            # Find next available offset in current segment
            used_offsets = set()
            for perm_key, (perm_module, perm_segment, bit_val) in self._permission_to_bit.items():
                if perm_module == module and perm_segment == segment:
                    # Calculate offset from bit value
                    used_offsets.add(bit_val.bit_length() - 1)
            
            offset = 0
            while offset in used_offsets and offset < BITS_PER_SEGMENT:
                offset += 1
            
            if offset >= BITS_PER_SEGMENT:
                # Move to next segment
                segment = self._module_segments[module] + 1
                offset = 0
        
        perm_bit = bit(module, segment, offset)
        self._permission_to_bit[permission_key] = perm_bit
        self._bit_to_permission[perm_bit] = permission_key
        
        if segment >= self._module_segments[module]:
            self._module_segments[module] = segment + 1
        
        # Store metadata
        self._permission_info[permission_key] = {
            'module': module,
            'name': name or permission_key,
            'group': group,
            'segment': segment,
            'offset': offset
        }
        
        return perm_bit
    
    def get_bit(self, permission_key: str) -> Optional[PermissionBit]:
        """Get bit value for a permission key."""
        return self._permission_to_bit.get(permission_key)
    
    def get_permission(self, perm_bit: PermissionBit) -> Optional[str]:
        """Get permission key for a bit value."""
        return self._bit_to_permission.get(perm_bit)
    
    def get_all_permissions(self) -> Dict[str, PermissionBit]:
        """Get all registered permissions."""
        return self._permission_to_bit.copy()
    
    def get_module_permissions(self, module: str) -> Dict[str, PermissionBit]:
        """Get all permissions for a specific module."""
        return {
            key: bit_val
            for key, bit_val in self._permission_to_bit.items()
            if bit_val[0] == module
        }
    
    def get_permission_info(self, permission_key: str) -> Optional[Dict]:
        """Get permission metadata."""
        return self._permission_info.get(permission_key)


# Global registry instance
_registry = PermissionBitsetRegistry()


def get_registry() -> PermissionBitsetRegistry:
    """Get the global permission registry."""
    return _registry


class PermissionBitset:
    """
    Represents a set of permissions using bitwise operations.
    Similar to Discord's permission system with allow/deny bitsets.
    """
    
    def __init__(self, allow: int = 0, deny: int = 0, module: Optional[str] = None, processed_permissions: Optional[Set[str]] = None):
        """
        Initialize a permission bitset.
        
        Args:
            allow: Bitmask of allowed permissions
            deny: Bitmask of denied permissions
            module: Optional module name for module-specific bitsets
            processed_permissions: Set of permission keys that were actually processed
        """
        self.allow = allow
        self.deny = deny
        self.module = module
        self._processed_permissions = processed_permissions or set()
    
    def has_permission(self, permission_key: str) -> bool:
        """
        Check if a permission is allowed.
        
        Args:
            permission_key: Permission key to check
        
        Returns:
            True if permission is allowed, False otherwise
        """
        perm_bit = _registry.get_bit(permission_key)
        if not perm_bit:
            return False
        
        module, segment, bit_val = perm_bit
        
        # Check if denied
        if self.deny & bit_val == bit_val:
            return False
        
        # Check if allowed
        return self.allow & bit_val == bit_val
    
    def allow_permission(self, permission_key: str) -> 'PermissionBitset':
        """Add a permission to the allow set."""
        perm_bit = _registry.get_bit(permission_key)
        if perm_bit:
            _, _, bit_val = perm_bit
            self.allow |= bit_val
            # Remove from deny if present
            self.deny &= ~bit_val
        return self
    
    def deny_permission(self, permission_key: str) -> 'PermissionBitset':
        """Add a permission to the deny set."""
        perm_bit = _registry.get_bit(permission_key)
        if perm_bit:
            _, _, bit_val = perm_bit
            self.deny |= bit_val
            # Remove from allow if present
            self.allow &= ~bit_val
        return self
    
    def remove_permission(self, permission_key: str) -> 'PermissionBitset':
        """Remove a permission from both allow and deny sets."""
        perm_bit = _registry.get_bit(permission_key)
        if perm_bit:
            _, _, bit_val = perm_bit
            self.allow &= ~bit_val
            self.deny &= ~bit_val
        return self
    
    def combine(self, other: 'PermissionBitset') -> 'PermissionBitset':
        """
        Combine two permission bitsets.
        Similar to Discord's permission overwrite logic:
        - Deny takes precedence
        - Then allow is applied
        
        Args:
            other: Another PermissionBitset to combine with
        
        Returns:
            New PermissionBitset with combined permissions
        """
        # Start with base permissions
        result_allow = self.allow
        result_deny = self.deny
        
        # Apply deny first (deny overrides allow)
        result_deny |= other.deny
        result_allow &= ~other.deny
        
        # Then apply allow
        result_allow |= other.allow
        
        # Combine processed permissions sets
        combined_processed = self._processed_permissions | other._processed_permissions
        
        return PermissionBitset(
            allow=result_allow,
            deny=result_deny,
            module=self.module,
            processed_permissions=combined_processed
        )
    
    def to_dict(self) -> Dict[str, bool]:
        """
        Convert bitset to dictionary format compatible with current system.
        
        Returns:
            Dictionary mapping permission keys to enabled status
        """
        result = {}
        for perm_key, perm_bit in _registry.get_all_permissions().items():
            if self.module and perm_bit[0] != self.module:
                continue
            result[perm_key] = self.has_permission(perm_key)
        return result
    
    def to_list(self) -> List[Dict]:
        """
        Convert bitset to list format compatible with current API response.
        Only returns permissions that were actually processed (in _processed_permissions).
        Tries to get permission info from database first, falls back to registry metadata.
        
        Returns:
            List of permission dictionaries with status
        """
        from app.permission.config_static_varible.common import (
            STATUS_PERMISSION_ALLOW_KEY,
            STATUS_PERMISSION_DENY_KEY
        )
        from app.permission.models import Permission
        
        result = []
        # Only return permissions that were actually processed
        permissions_to_check = self._processed_permissions if self._processed_permissions else _registry.get_all_permissions().keys()
        
        for perm_key in permissions_to_check:
            perm_bit = _registry.get_bit(perm_key)
            if not perm_bit:
                continue
            
            if self.module and perm_bit[0] != self.module:
                continue
            
            # Try to get from database first
            try:
                perm_obj = Permission.objects.get(key=perm_key)
                perm_name = perm_obj.name
                perm_group = perm_obj.group
                perm_module = perm_obj.module
            except Permission.DoesNotExist:
                # Fall back to registry metadata
                info = _registry.get_permission_info(perm_key) or {}
                perm_name = info.get('name', perm_key)
                perm_group = info.get('group', '')
                perm_module = info.get('module', '')
            
            result.append({
                'key': perm_key,
                'name': perm_name,
                'group': perm_group,
                'module': perm_module,
                'status': STATUS_PERMISSION_ALLOW_KEY if self.has_permission(perm_key) else STATUS_PERMISSION_DENY_KEY
            })
        return result
    
    def __or__(self, other: 'PermissionBitset') -> 'PermissionBitset':
        """OR operation: combine permissions (union)."""
        return PermissionBitset(
            allow=self.allow | other.allow,
            deny=self.deny | other.deny,
            module=self.module,
            processed_permissions=self._processed_permissions | other._processed_permissions
        )
    
    def __and__(self, other: 'PermissionBitset') -> 'PermissionBitset':
        """AND operation: intersection of permissions."""
        return PermissionBitset(
            allow=self.allow & other.allow,
            deny=self.deny & other.deny,
            module=self.module,
            processed_permissions=self._processed_permissions & other._processed_permissions
        )
    
    def __repr__(self) -> str:
        return f"PermissionBitset(allow={self.allow}, deny={self.deny}, module={self.module})"


def from_permission_list(permissions: List[Dict]) -> PermissionBitset:
    """
    Create a PermissionBitset from a list of permission dictionaries.
    
    Args:
        permissions: List of permission dicts with 'key' and 'status' fields
    
    Returns:
        PermissionBitset instance with tracked permissions
    """
    from app.permission.config_static_varible.common import (
        STATUS_PERMISSION_ALLOW_KEY,
        STATUS_PERMISSION_DENY_KEY
    )
    
    allow = 0
    deny = 0
    processed_permissions = set()  # Track which permissions were processed
    
    for perm in permissions:
        perm_key = perm.get('key')
        status = perm.get('status')
        
        if not perm_key:
            continue
        
        perm_bit = _registry.get_bit(perm_key)
        if not perm_bit:
            continue
        
        processed_permissions.add(perm_key)
        _, _, bit_val = perm_bit
        
        if status == STATUS_PERMISSION_ALLOW_KEY:
            allow |= bit_val
        elif status == STATUS_PERMISSION_DENY_KEY:
            deny |= bit_val
    
    bitset = PermissionBitset(allow=allow, deny=deny)
    # Store processed permissions for later retrieval
    bitset._processed_permissions = processed_permissions
    return bitset


def to_permission_list(bitset: PermissionBitset, module: Optional[str] = None) -> List[Dict]:
    """
    Convert a PermissionBitset to a list of permission dictionaries.
    
    Args:
        bitset: PermissionBitset to convert
        module: Optional module filter (if provided, creates a new bitset filtered by module)
    
    Returns:
        List of permission dictionaries
    """
    if module:
        # Filter by module if specified
        filtered_bitset = PermissionBitset(allow=bitset.allow, deny=bitset.deny, module=module)
        return filtered_bitset.to_list()
    return bitset.to_list()


def initialize_permission_registry():
    """
    Initialize the permission registry by loading all permissions from config.
    This should be called once at startup.
    """
    from app.permission.config_static_varible.config import PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL
    
    for group_key, group_config in PERMISSIONS_GROUPS_CONFIG_CLIENT_LEVEL.items():
        module = group_config.get('module', '')
        permissions = group_config.get('permissions', [])
        
        for perm in permissions:
            perm_key = perm.get('key')
            perm_name = perm.get('name', perm_key)
            
            if perm_key:
                _registry.register_permission(
                    permission_key=perm_key,
                    module=module,
                    name=perm_name,
                    group=group_key
                )

