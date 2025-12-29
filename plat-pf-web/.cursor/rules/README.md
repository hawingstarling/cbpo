# Cursor Rules for Plat-PF-Web Vue.js Project

## Overview
This directory contains Cursor AI rules specifically tailored for the Plat-PF-Web Vue.js project. The rules are organized to provide comprehensive guidance for Vue.js 2.6.10 development with CoreUI, Bootstrap Vue, and custom components.

## Directory Structure

### 01-core/ (4 files)
- **01-ai-workflow.mdc** - AI development workflow for Vue.js projects
- **02-security-principles.mdc** - Security patterns and best practices
- **03-code-quality.mdc** - Code quality standards for Vue.js
- **05-shell-command-permissions.mdc** - Shell command permissions

### 02-technical/ (12 files)
- **01-vue-patterns.mdc** - Vue.js 2.6.10 specific patterns and best practices
- **02-vuex-patterns.mdc** - Vuex 3.0.1 store patterns and state management
- **03-coreui-bootstrap.mdc** - CoreUI 2.1.9 and Bootstrap Vue 2.0.4 patterns
- **04-project-structure.mdc** - Project organization and file structure
- **05-api-standards.mdc** - API integration patterns with axios
- **06-ui-component-rules.mdc** - UI component development rules
- **07-routing-patterns.mdc** - Vue Router 3.0.3 patterns and navigation
- **08-form-validation.mdc** - Form validation with Vee-validate 3.3.7
- **09-testing-standards.mdc** - Testing patterns with Jest and Vue Test Utils
- **10-performance-optimization.mdc** - Performance optimization patterns
- **11-error-handling.mdc** - Error handling and user feedback patterns
- **12-accessibility.mdc** - Accessibility patterns for Vue.js components

## Key Features

### Vue.js 2.6.10 Patterns
- Single-file components with template, script, and style sections
- Options API patterns (data, computed, methods, watch, lifecycle hooks)
- Proper component lifecycle management
- Performance optimization techniques

### CoreUI & Bootstrap Vue Integration
- CoreUI 2.1.9 component patterns
- Bootstrap Vue 2.0.4 form elements and navigation
- SCSS styling with proper nesting and theming
- Icon systems (Font Awesome, Simple Line Icons)

### State Management
- Vuex 3.0.1 modular store architecture
- Namespaced modules for better organization
- Proper action/mutation/getter patterns
- Error handling and loading states

### API Integration
- Axios instances (pfAxios, dsAxios) with interceptors
- Authentication and token handling
- Error handling and retry patterns
- Loading state management

### Testing & Quality
- Jest and Vue Test Utils for component testing
- ESLint and Prettier for code quality
- Proper test coverage and organization
- Performance and accessibility testing

### Total Files: 16 rules (4 core + 12 technical)

## Usage

These rules are automatically applied by Cursor AI when working on the project. They provide:

1. **Development Guidance** - Best practices for Vue.js development
2. **Code Quality** - Standards for consistent, maintainable code
3. **Performance** - Optimization patterns and techniques
4. **Security** - Security patterns and best practices
5. **Accessibility** - Guidelines for accessible UI components

## Cross-References

Rules are interconnected with cross-references to ensure comprehensive coverage:
- Vue patterns reference project structure and UI components
- API standards reference security principles and error handling
- Testing standards reference code quality and Vue patterns
- Performance optimization references routing and API patterns

## Maintenance

Rules should be updated when:
- Project dependencies are updated
- New patterns are established
- Architecture changes are made
- New features require specific guidance

## Contributing

When adding new rules:
1. Follow the established naming conventions
2. Include proper cross-references
3. Use appropriate globs for file targeting
4. Provide clear, actionable guidance
5. Update this README with new rule descriptions
