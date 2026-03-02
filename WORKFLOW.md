# Strom Frontend Workflow

This document outlines the development lifecycle for the Strom frontend.

## 1. Local Development
1. **Initial Setup**: Ensure you are in the `packages/frontend` directory.
   ```bash
   cd packages/frontend
   npm install
   ```
2. **Launch Dev Server**:
   ```bash
   npm run dev
   ```
   Open `localhost:3000` to view the application.
3. **Add shadcn/ui Components**:
   ```bash
   npx shadcn@latest add <component-name>
   ```

## 2. Code Quality & Consistency
- **Linting**:
  ```bash
  npm run lint
  ```
- **Type Checking**:
  ```bash
  npm run typecheck # (if configured, otherwise npm run build)
  ```
- **Build Verification**:
  ```bash
  npm run build
  ```

## 3. Deployment Workflow (Future)
- TBD: CI/CD integration for Vercel or custom Docker deployment.
- Current standalone Docker builds:
  ```bash
  cd packages/frontend
  docker build -t strom-frontend .
  ```

## 4. Workstream Status: Frontend
- [x] Project Scaffolding
- [x] Layout Shell & Sidebar
- [x] Responsive Mobile Bottom Nav
- [x] Dark Mode Implementation
- [x] Top Bar: Connection, Mode, Kill Switch
- [x] Shared Components Library (F8)
- [ ] Markets Page Implementation
- [ ] Trading Interface
- [ ] Real-time Data Integration
