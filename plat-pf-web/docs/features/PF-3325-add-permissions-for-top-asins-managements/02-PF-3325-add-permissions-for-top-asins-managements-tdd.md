# Top ASINs Permissions - Technical Design Document

## Overview
This document outlines the technical implementation for adding granular permission controls to the Top ASINs functionality, including navigation access control and action management restrictions.

## Architecture Design

### Permission System Integration
```
Frontend (Vue.js) ←→ Vuex Store ←→ Backend API ←→ Permission Service
     ↓
Navigation Guards ←→ Route Protection ←→ Component Rendering
```

### Core Components Affected
1. **Navigation System**: Brand Management navigation menu
2. **Top ASINs Components**: ListTopASINs.vue, related components
3. **Permission System**: Existing permission infrastructure
4. **Routing System**: Route guards and navigation

## Technical Implementation

### 1. Permission Constants
**File**: `src/shared/utils.js`
```javascript
// Add to convertedPermissions object
topASINs: {
  view: 'PF_TOP_ASINs_VIEW',
  edit: 'PF_TOP_ASINs_EDIT', 
  delete: 'PF_TOP_ASINs_DELETE',
  import: 'PF_TOP_ASINs_IMPORT',
  export: 'PF_TOP_ASINs_EXPORT'
}
```

### 2. Navigation Control Implementation
**File**: `src/_nav.js` (or navigation configuration)
```javascript
// Conditional navigation item rendering
{
  name: 'Top ASINs',
  url: '/administration/top-asins',
  icon: 'icon-list',
  // Add permission check
  permission: 'PF_TOP_ASINs_VIEW'
}
```

### 3. Route Protection
**File**: `src/router/_routerConfig.js`
```javascript
{
  path: 'top-asins/',
  meta: {
    label: 'Top ASINs',
    permissions: [permissions.topASINs.view], // Already implemented
    reloadPermissions: true
  },
  // ... existing config
}
```

### 4. Component Permission Logic
**File**: `src/components/pages/administration/topASINs/ListTopASINs.vue`

#### View Permission Check
```javascript
// In computed properties
hasViewPermission() {
  return this.hasPermission(this.permissions.topASINs.view)
}

// In template
<template v-if="hasViewPermission">
  <!-- Top ASINs content -->
</template>
```

#### Action Manage Logic
```javascript
// Computed property for action manage visibility
showActionManage() {
  return this.hasPermission(this.permissions.topASINs.edit) || 
         this.hasPermission(this.permissions.topASINs.delete)
}

// Individual action checks
canEdit() {
  return this.hasPermission(this.permissions.topASINs.edit)
}

canDelete() {
  return this.hasPermission(this.permissions.topASINs.delete)
}
```

### 5. Navigation Menu Updates
**File**: Brand Management navigation component
```javascript
// Filter navigation items based on permissions
filteredNavItems() {
  return this.navItems.filter(item => {
    if (item.permission) {
      return this.hasPermission(item.permission)
    }
    return true
  })
}
```

## Data Flow

### 1. Permission Loading
```
User Login → Backend Permission Service → Frontend Permission Store → Component Rendering
```

### 2. Navigation Rendering
```
Permission Check → Navigation Filter → Menu Rendering → User Interface
```

### 3. Action Management
```
Permission Check → Action Visibility → User Interaction → Backend Validation
```

## Security Considerations

### Frontend Security
- All permission checks use existing `hasPermission` mixin
- No client-side permission bypassing
- Consistent permission validation across components

### Backend Security
- Permission validation on all API endpoints
- Server-side permission checks for all operations
- Proper error handling for unauthorized access

## Performance Considerations

### Optimization Strategies
1. **Permission Caching**: Permissions loaded once per session
2. **Conditional Rendering**: Use `v-if` for efficient DOM updates
3. **Lazy Loading**: Navigation items loaded based on permissions

### Memory Management
- Permissions stored in Vuex store
- No unnecessary permission checks
- Efficient component re-rendering

## Error Handling

### Permission Denied Scenarios
1. **Navigation Access**: Redirect to unauthorized page
2. **Component Access**: Show permission denied message
3. **Action Access**: Disable/hide unauthorized actions

### User Experience
- Clear error messages for permission issues
- Smooth navigation transitions
- Consistent permission feedback

## Testing Strategy

### Unit Tests
- Permission check functions
- Navigation filtering logic
- Component rendering with different permission states

### Integration Tests
- End-to-end permission flow
- Navigation behavior with different user roles
- Action management with various permission combinations

### Manual Testing
- Different user permission scenarios
- Navigation menu behavior
- Action button visibility and functionality

## Dependencies

### Existing Systems
- Current permission infrastructure
- Vue.js routing system
- Vuex state management
- CoreUI navigation components

### New Dependencies
- None (uses existing permission system)

## Implementation Phases

### Phase 1: Core Permission Integration
- Add permission constants
- Update route protection
- Implement basic permission checks

### Phase 2: Navigation Control
- Update navigation menu
- Implement tab hiding logic
- Test navigation behavior

### Phase 3: Action Management
- Implement action manage logic
- Update component rendering
- Test action visibility

### Phase 4: Testing & Refinement
- Comprehensive testing
- Performance optimization
- User experience refinement

## Cross-References
- Vue patterns: `02-technical/01-vue-patterns.mdc`
- Vuex patterns: `02-technical/02-vuex-patterns.mdc`
- Routing patterns: `02-technical/07-routing-patterns.mdc`
- Security principles: `01-core/02-security-principles.mdc`
- UI component rules: `02-technical/06-ui-component-rules.mdc`
