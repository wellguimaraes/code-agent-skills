---
name: tailwind-properly
description: Write Tailwind styling inline in the component — className inside cn() with boolean && composition — never cva(), constants, or lookup tables. Break long class strings into logical multi-line groups and use condition && / !condition && (or default + override) instead of ternary class swaps. Use when writing or editing component styling, long className strings, conditional cn() styling, or when the user asks to split/break/format Tailwind classes or inline/remove cva.
---

# Tailwind properly

## Where the classes live

Write class names inline in the component's `className`, inside `cn()`, and compose
variants with boolean `&&`. Do not move class strings into a constant, a `Record`
lookup table, or `cva()`. No `cva()` anywhere — including layers that already use it.
When editing a component that uses `cva()`, inline its base/variant strings into the
component's `cn()` instead of extending the variant map.

## Splitting a long string

When a Tailwind class string is long, split it into a **string array** with one logical
group per line. Do not leave a single giant one-liner.

## Rules

1. Prefer `cn([ '...', '...' ], …)` over `cn('…long…', …)` for the base classes.
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
5. Short strings can remain single strings.

## Example

**Before (`cva()` one-liner + variant map):**
```ts
const inputVariants = cva(
  'w-full min-w-0 rounded-lg border border-input bg-transparent transition-colors outline-none file:inline-flex file:border-0 placeholder:text-subtle-foreground focus-visible:border-ring focus-visible:ring-3 disabled:opacity-50 dark:bg-input/30',
  {
    variants: {
      size: { sm: 'h-8 px-3 text-sm', lg: 'h-12 px-5 text-lg' },
    },
  },
);

// …then: className={inputVariants({ size })}
```

**After (inline):**
```tsx
<input
  className={cn(
    [
      'w-full min-w-0 rounded-lg border border-input bg-transparent',
      'transition-colors outline-none',
      'file:inline-flex file:border-0 file:bg-transparent file:font-medium file:text-foreground',
      'placeholder:text-subtle-foreground',
      'focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50',
      'disabled:pointer-events-none disabled:cursor-not-allowed disabled:bg-input/50 disabled:opacity-50',
      'dark:bg-input/30 dark:disabled:bg-input/80',
    ],
    size === 'sm' && 'h-8 px-3 text-sm',
    size === 'lg' && 'h-12 px-5 text-lg',
  )}
/>
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
- `cva()` definitions in components you edit — inline them per *Where the classes live*
- Conditional `cn(...)` / `className` composition — rewrite ternary class swaps per Conditional styling above