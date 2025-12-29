# Top ASINs Permissions - Implementation Tasks

## Phase 1: Core Permission Integration (2-3 hours)

### Task 1.1: Add Permission Constants
**File**: `src/shared/utils.js`
**Effort**: 15 minutes
**Dependencies**: None

**Acceptance Criteria:**
- [ ] Add `topASINs` object to `convertedPermissions`
- [ ] Include all 5 permission constants (view, edit, delete, import, export)
- [ ] Follow existing naming convention
- [ ] Test permission constants are accessible

**Implementation:**
```javascript
topASINs: {
  view: 'PF_TOP_ASINs_VIEW',
  edit: 'PF_TOP_ASINs_EDIT',
  delete: 'PF_TOP_ASINs_DELETE',
  import: 'PF_TOP_ASINs_IMPORT',
  export: 'PF_TOP_ASINs_EXPORT'
}
```

### Task 1.2: Update Route Protection
**File**: `src/router/_routerConfig.js`
**Effort**: 10 minutes
**Dependencies**: Task 1.1

**Acceptance Criteria:**
- [ ] Verify route already has `permissions: [permissions.topASINs.view]`
- [ ] Test route protection works correctly
- [ ] Ensure unauthorized users are redirected

**Implementation:**
- Verify existing route configuration
- Test with different permission states

### Task 1.3: Implement Basic Permission Checks
**File**: `src/components/pages/administration/topASINs/ListTopASINs.vue`
**Effort**: 30 minutes
**Dependencies**: Task 1.1

**Acceptance Criteria:**
- [ ] Add permission checks to import/export dropdowns
- [ ] Add permission checks to edit/delete buttons
- [ ] Add permission checks to action methods
- [ ] Test all permission scenarios

**Implementation:**
```vue
<!-- Import dropdown -->
<b-dropdown v-if="hasPermission(permissions.topASINs.import)" ...>

<!-- Export dropdown -->
<b-dropdown v-if="hasPermission(permissions.topASINs.export)" ...>

<!-- Edit button -->
<button v-if="hasPermission(permissions.topASINs.edit)" ...>

<!-- Delete button -->
<button v-if="hasPermission(permissions.topASINs.delete)" ...>
```

## Phase 2: Navigation Control (1-2 hours)

### Task 2.1: Update Navigation Menu
**File**: `src/_nav.js` (or navigation configuration)
**Effort**: 45 minutes
**Dependencies**: Task 1.1

**Acceptance Criteria:**
- [ ] Add permission check to Top ASINs navigation item
- [ ] Implement conditional rendering logic
- [ ] Test navigation menu with different permissions
- [ ] Ensure smooth navigation experience

**Implementation:**
```javascript
// Find Top ASINs navigation item and add permission
{
  name: 'Top ASINs',
  url: '/administration/top-asins',
  icon: 'icon-list',
  permission: 'PF_TOP_ASINs_VIEW' // Add this line
}
```

### Task 2.2: Implement Navigation Filtering
**File**: Navigation component (Brand Management)
**Effort**: 30 minutes
**Dependencies**: Task 2.1

**Acceptance Criteria:**
- [ ] Create navigation filtering logic
- [ ] Hide Top ASINs tab when view permission is false
- [ ] Test navigation behavior with different user roles
- [ ] Ensure no broken navigation links

**Implementation:**
```javascript
// In navigation component
computed: {
  filteredNavItems() {
    return this.navItems.filter(item => {
      if (item.permission) {
        return this.hasPermission(item.permission)
      }
      return true
    })
  }
}
```

## Phase 3: Action Management (1-2 hours)

### Task 3.1: Implement Action Manage Logic
**File**: `src/components/pages/administration/topASINs/ListTopASINs.vue`
**Effort**: 45 minutes
**Dependencies**: Task 1.3

**Acceptance Criteria:**
- [ ] Add computed property for action manage visibility
- [ ] Implement logic: show if either edit OR delete permission is true
- [ ] Hide action manage when both edit AND delete are false
- [ ] Test all permission combinations

**Implementation:**
```javascript
computed: {
  showActionManage() {
    return this.hasPermission(this.permissions.topASINs.edit) || 
           this.hasPermission(this.permissions.topASINs.delete)
  }
}
```

### Task 3.2: Update Action Manage UI
**File**: `src/components/pages/administration/topASINs/ListTopASINs.vue`
**Effort**: 30 minutes
**Dependencies**: Task 3.1

**Acceptance Criteria:**
- [ ] Add `v-if="showActionManage"` to action manage elements
- [ ] Ensure individual actions respect their permissions
- [ ] Test action visibility with different permission states
- [ ] Maintain UI consistency

**Implementation:**
```vue
<!-- Action manage dropdown -->
<b-dropdown v-if="showActionManage" ...>
  <b-dropdown-item v-if="hasPermission(permissions.topASINs.edit)" ...>
  <b-dropdown-item v-if="hasPermission(permissions.topASINs.delete)" ...>
</b-dropdown>
```

## Phase 4: Testing & Refinement (1-2 hours)

### Task 4.1: Comprehensive Testing
**Effort**: 60 minutes
**Dependencies**: All previous tasks

**Acceptance Criteria:**
- [ ] Test all permission combinations
- [ ] Test navigation behavior
- [ ] Test action visibility
- [ ] Test error handling
- [ ] Verify no broken functionality

**Test Scenarios:**
1. **No permissions**: Should hide everything
2. **View only**: Should show page but no actions
3. **Edit only**: Should show edit actions, hide delete
4. **Delete only**: Should show delete actions, hide edit
5. **All permissions**: Should show everything

### Task 4.2: Performance Optimization
**Effort**: 30 minutes
**Dependencies**: Task 4.1

**Acceptance Criteria:**
- [ ] Optimize permission checks
- [ ] Ensure efficient DOM updates
- [ ] Test performance with large datasets
- [ ] Verify smooth user experience

### Task 4.3: User Experience Refinement
**Effort**: 30 minutes
**Dependencies**: Task 4.2

**Acceptance Criteria:**
- [ ] Smooth transitions when permissions change
- [ ] Clear visual indicators for disabled actions
- [ ] Consistent permission feedback
- [ ] No broken layouts

## Implementation Summary

### Total Effort: 5-8 hours
- **Phase 1**: 2-3 hours (Core permissions)
- **Phase 2**: 1-2 hours (Navigation)
- **Phase 3**: 1-2 hours (Action management)
- **Phase 4**: 1-2 hours (Testing & refinement)

### Critical Path
1. Add permission constants (Task 1.1)
2. Update navigation menu (Task 2.1)
3. Implement action manage logic (Task 3.1)
4. Comprehensive testing (Task 4.1)

### Risk Mitigation
- Test each phase thoroughly before proceeding
- Maintain existing functionality during implementation
- Use existing permission patterns for consistency
- Backup current implementation before changes

### Success Criteria
- All permission scenarios work correctly
- Navigation menu responds to permission changes
- Action management respects permission logic
- No broken functionality or UI issues
- Smooth user experience across all permission states
