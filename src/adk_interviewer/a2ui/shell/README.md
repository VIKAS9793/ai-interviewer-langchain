# A2UI Shell - AI Interviewer Customizations

These files are preserved copies of the A2UI shell with our customizations.

## Files Included

- `index.html` - Google Sans font + M3 tokens + focus rings
- `app.ts` - 1024px layout + responsive padding
- `configs/interviewer.ts` - AI Interviewer branding
- `theme/default-theme.ts` - M3-compatible theming

## How to Use

These files should be copied to the A2UI shell directory:

```bash
# Copy to a2ui-repo (after cloning google/a2ui)
cp -r src/adk_interviewer/a2ui/shell/* a2ui-repo/samples/client/lit/shell/
```

## Dependencies

Requires A2UI shell with npm packages:
- `@a2ui/lit`
- `lit`
- `vite`

## Customizations Applied

1. **Google Sans Font** - M3 Typography
2. **1024px Layout** - Wider content area
3. **M3 Color Tokens** - Semantic design tokens
4. **Smooth Scroll** - Better UX
5. **Focus Rings** - Accessibility
