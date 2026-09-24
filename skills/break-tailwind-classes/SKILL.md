---
name: break-tailwind-classes
description: Break long Tailwind class strings into logical multi-line groups, especially cva() base/variant class lists. Organize conditional className/cn() styling with condition && / !condition && (or default + override) instead of ternary class swaps. Use when writing or editing cva variants, long className strings, conditional cn() styling, or when the user asks to split/break/format Tailwind classes.
---

# Break Tailwind classes

## Where the classes live, first

Default: write class names inline in the `className`, inside `cn()`, and compose variants
with boolean `&&`. Do not move class strings into a constant, a `Record` lookup table, or
`cva()` unless the codebase already uses `cva()` for that layer.

`cva()` stays the pattern only where it is the house style, such as shadcn-based
primitives (`frontend/client/src/components/primitives/` in greenspark-aws). The rest of
this file then applies to those `cva()` strings. Everywhere else, apply the same grouping
rules to the `cn()` arguments instead: one argument per concern, one condition per
argument.

## Splitting a long string

When a Tailwind class string is long (especially `cva()` base or variant values), split it into a **string array** with one logical group per line. Do not leave a single giant one-liner.

## Rules

1. Prefer `cva([ '...', '...' ], { ... })` over `cva('...long...', { ... })`.
2. Group by concern — not arbitrary length wrapping:
   - layout / sizing / shape
   - typography
   - colors / borders / background
   - transitions / interaction defaults
   - pseudo / slotted (`file:`, `placeholder:`, `[&_svg]:`, etc.)
   - state: `hover:`, `focus-visible:`, `active:`, `disabled:`
   - a11y: `aria-invalid:`
   - theme: `dark:`
3. Keep related utilities on the same line (e.g. all `focus-visible:*` together).
4. Match nearby UI components in the same folder when a pattern already exists.
5. Variant size/color strings that stay short can remain single strings.

## Example

**Before:**
```ts
const inputVariants = cva(
  'w-full min-w-0 rounded-lg border border-input bg-transparent transition-colors outline-none file:inline-flex file:border-0 placeholder:text-subtle-foreground focus-visible:border-ring focus-visible:ring-3 disabled:opacity-50 aria-invalid:border-destructive dark:bg-input/30',
  { variants: { /* ... */ } },
);
```

**After:**
```ts
const inputVariants = cva(
  [
    'w-full min-w-0 rounded-lg border border-input bg-transparent',
    'transition-colors outline-none',
    'file:inline-flex file:border-0 file:bg-transparent file:font-medium file:text-foreground',
    'placeholder:text-subtle-foreground',
    'focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50',
    'disabled:pointer-events-none disabled:cursor-not-allowed disabled:bg-input/50 disabled:opacity-50',
    'aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20',
    'dark:bg-input/30 dark:disabled:bg-input/80 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40',
  ],
  { variants: { /* ... */ } },
);
```

## Conditional styling

Do **not** use ternaries for mutually exclusive class strings (`cond ? 'a' : 'b'`). Prefer boolean `&&` composition in `cn(...)`.

1. Explicit both sides when each branch owns a distinct look:
   - `cond && '…'`
   - `!cond && '…'`
2. Default + override when one look is the normal state: put the default classes in the base string, then `cond && '…'` so later `cn`/`twMerge` entries win.
3. Use additive conditionals for optional modifiers (`disabled && 'opacity-50'`).
4. Keep each conditional as its own `cn(...)` argument (one per line when there are several).

**Avoid:**
```ts
cn('base', open ? 'bg-primary/10 text-primary' : 'text-text-secondary hover:bg-text/5')
```

**Prefer (both sides explicit):**
```ts
cn(
  'base',
  open && 'bg-primary/10 text-primary',
  !open && 'text-text-secondary hover:bg-text/5 hover:text-text',
)
```

**Prefer (default + override)** when one look is the normal state:
```ts
cn(
  'base text-text-secondary hover:bg-text/5 hover:text-text',
  open && 'bg-primary/10 text-primary hover:bg-primary/10 hover:text-primary',
)
```

## Also apply to

- Long `cn(...)` / `className` literals when they hurt readability
- `cva` variant values that become long one-liners (outline/destructive/etc.) — split those the same way if needed
- Conditional `cn(...)` / `className` composition — rewrite ternary class swaps per Conditional styling above
