# Strom Frontend Development Rules

## Tech Stack
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4 (with JIT)
- **UI Components**: shadcn/ui (Radix UI based)
- **Icons**: Lucide React
- **Theming**: next-themes (Dark mode by default)
- **Testing**: Vitest + React Testing Library

## Architectural Guidelines
1. **App Router**: Follow Next.js 14 App Router conventions. Use `src/app` for routes.
2. **Components**:
   - Keep components small and focused.
   - Use `src/components/ui` for primitive shadcn components.
   - Use `src/components/shared` for reusable, generic components.
3. **Client vs Server Components**:
   - Use Server Components by default.
   - Use `"use client"` only when necessary (interactivity, hooks).
4. **Layout Shell**: All pages must be wrapped in `LayoutShell` to ensure consistent sidebar/topbar.
5. **Responsiveness**:
   - Mobile first.
   - Sidebar collapses to icons on tablets.
   - Sidebar hidden on mobile, replaced by `BottomNav`.
6. **Aesthetics**:
   - Premium look: Use backdrop blurs (`backdrop-blur`), subtle borders (`border-border/50`), and glassmorphism.
   - Color Palette: Slate/Zinc based with Primary (Indigo/Blue) accents.
   - Animations: Use `animate-in`, `fade-in`, `slide-in` for page transitions.

## Shared Components Registry
- **DataTable**: Built on `@tanstack/react-table`. Supports sorting, filtering, and pagination.
- **MetricCard**: Displays value with trend (up/down) and indicator colors.
- **AssetClassBadge**: Colored pill labels (Equity=Green, Crypto=Purple).
- **StatusBadge**: Pulse-dot status indicators (Success, Warning, Error).
- **LoadingSpinner**: Standardized Loader2 with accessibility labels.
- **ConfirmDialog**: Reusable AlertDialog for destructive or critical actions.
- **ErrorBoundary**: Graceful failure UI for component crashes.

## Testing Guidelines
1. **Unit Tests**: Every shared component must have a corresponding `.test.tsx` file in `src/tests/shared`.
2. **Coverage**: Test for rendering, interactivity (clicks, inputs), and ARIA compliance.
3. **Command**: Run `npm run test` to execute all tests.

## Naming Conventions
- Components: PascalCase (e.g., `TopBar.tsx`)
- Hooks: camelCase starting with `use` (e.g., `useSocket.ts`)
- Config/Utils: kebab-case or camelCase.

## Performance
- Optimize images using `next/image`.
- Minimize client-side bundles.
- Use `lucide-react` sparingly or ensure tree-shaking is working.
