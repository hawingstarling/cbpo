# Architecture Documentation

## System Architecture
Frontend SPA (Vue 2) consuming PF APIs.

## Design Patterns
- Options API, Mixins, Vuex modules
- Permission-based UI rendering
- Route guards with permission checks

## Data Flow
User -> Components -> Vuex/Services -> API -> Backend

## Security Considerations
- Permission checks (PermissionsMixin)
- Backend authorization
- UI conditional rendering based on permissions
- Method-level permission guards

## Permission System
- Constants in `src/shared/utils.js` (convertedPermissions.topASINs)
- Route meta with permission requirements
- Component-level permission checks
- Navigation tab visibility control
