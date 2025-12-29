# Components

## Key Areas
- Administration pages (Brand, Top ASINs)
- Common components, mixins

## Top ASINs Components
- `ListTopASINs.vue` - Main list component with permission-based UI
- Permission checks: `hasPermission(permissions.topASINs.view/edit/delete/import/export)`
- Conditional rendering: Import/Export dropdowns, Manage actions column
- Method guards: Edit/Delete/Import/Export methods with permission validation

## Conventions
- File naming: PascalCase.vue for components
- Keep methods lean, use services and store
- Use PermissionsMixin for permission checks
