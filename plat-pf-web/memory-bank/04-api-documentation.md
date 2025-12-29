# API Documentation

## Standards
- Axios services in src/services
- pfAxios/dsAxios with auth headers

## Permission Constants
```javascript
// src/shared/utils.js
export const convertedPermissions = {
  topASINs: {
    view: 'PF_TOP_ASINs_VIEW',
    edit: 'PF_TOP_ASINs_EDIT', 
    delete: 'PF_TOP_ASINs_DELETE',
    import: 'PF_TOP_ASINs_IMPORT',
    export: 'PF_TOP_ASINs_EXPORT'
  }
}
```

## Error Handling
- Toast + graceful fallbacks
- Permission validation with user feedback
