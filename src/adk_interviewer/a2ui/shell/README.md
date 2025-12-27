# A2UI Shell - AI Interviewer Customizations

These files are **backup copies** of the A2UI shell with our customizations.

> ⚠️ **Note:** TypeScript errors in these files are expected. They are reference copies 
> that require the A2UI npm environment (`@a2ui/lit`, `lit`, etc.) to compile.

## Files Included

- `index.html` - Google Sans font + M3 tokens + focus rings
- `app.ts` - 1024px layout + responsive padding
- `configs/interviewer.ts` - AI Interviewer branding
- `theme/default-theme.ts` - M3-compatible theming

## How to Use

Copy these files to the A2UI shell directory to apply customizations:

```bash
# After cloning google/a2ui repo
cp -r src/adk_interviewer/a2ui/shell/* a2ui-repo/samples/client/lit/shell/
```

## Dependencies

These files require running from within A2UI project:
- `@a2ui/lit` - A2UI component library
- `lit` - Lit web components
- `vite` - Build tool

## Customizations Applied

1. **Google Sans Font** - M3 Typography
2. **1024px Layout** - Wider content area
3. **M3 Color Tokens** - Semantic design tokens
4. **Smooth Scroll** - Better UX
5. **Focus Rings** - Accessibility
