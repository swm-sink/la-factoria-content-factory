---
name: /component-gen
description: "Generate Python components for . following team conventions"
usage: /component-gen [component-name] [--type functional|class|page] [--with-tests] [--with-styles]
category: web-dev
tools: Write, Read, Edit
---

# Component Generator for .

I'll help you generate **Python** components following your team's conventions and best practices for **.**.

## Component Types

### Functional Components
Modern Python components:
```bash
# SECURITY: Component name 'Button' validated → 'src/components/Button/' ✅
/component-gen Button --type functional

# SECURITY: Component name 'UserCard' validated → 'src/components/UserCard/' ✅ 
/component-gen UserCard --with-hooks
```

### Page Components
Full page layouts:
```bash
/component-gen Dashboard --type page
/component-gen ProfilePage --with-routing
```

### Shared Components
Reusable UI elements:
```bash
/component-gen Modal --shared
/component-gen DataTable --with-props
```

## Framework Support

### For React Projects
```bash
/component-gen Header --react --typescript
```
- Functional components with hooks
- TypeScript interfaces
- Styled-components or CSS modules
- React Testing Library tests

### For Vue Projects
```bash
/component-gen NavigationBar --vue --composition-api
```
- Composition API by default
- Single File Components
- Scoped styles
- Vue Test Utils

### For Angular Projects
```bash
/component-gen UserList --angular --standalone
```
- Standalone components
- TypeScript strict mode
- Angular Material integration
- Jasmine/Karma tests

## Generation Options

### With Tests
Generate pytest tests:
```bash
/component-gen ProductCard --with-tests
```
- Unit tests
- Integration tests
- Accessibility tests
- Snapshot tests

### With Styles
Include styling setup:
```bash
/component-gen Hero --with-styles
```
- CSS modules
- Styled-components
- SCSS/SASS
- Tailwind classes

### With State Management
Connect to state:
```bash
/component-gen TodoList --with-state
```
- Redux/Zustand/Pinia
- Context API
- Local state hooks

## Team Conventions

Following small team standards:
- File naming: [ComponentName].[ext]
- Folder structure: features/components/
- Export patterns: named/default
- Props validation: TypeScript/PropTypes

## Accessibility Features

For users users:
- ARIA labels
- Keyboard navigation
- Screen reader support
- Focus management

## Performance Optimization

For balanced requirements:
- Lazy loading setup
- Memo optimization
- Bundle splitting
- Virtual scrolling

## Component Structure

Generated with:
```
ComponentName/
├── index.ts                 # Barrel export
├── ComponentName.tsx        # Component logic
├── ComponentName.styles.ts  # Styled components
├── ComponentName.test.tsx   # Tests
├── ComponentName.stories.tsx # Storybook
└── types.ts                # TypeScript types
```

## Integration

### With [INSERT_API_STYLE]
Data fetching setup:
- API hooks
- Loading states
- Error handling
- Data caching

### With GitHub Actions
CI/CD ready:
- Test coverage
- Linting passes
- Build optimization
- Documentation

## Examples

### Basic Component
```bash
/component-gen Avatar
```

### Full-Featured Component
```bash
/component-gen DataGrid \
  --with-tests \
  --with-styles \
  --with-storybook \
  --with-docs
```

### Domain Component
```bash
/component-gen backendWidget \
  --with-api \
  --with-state
```

---

What component would you like to generate for .?