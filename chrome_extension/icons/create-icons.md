# Extension Icons

To create the extension icons, you'll need to create these files:

- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels) 
- `icon128.png` (128x128 pixels)

## Quick Icon Creation

You can use any image editor or online tool to create a simple icon with:

1. **Background**: Blue gradient (#0066cc to #004499)
2. **Symbol**: White "AI" text or a simple data/chart icon
3. **Style**: Modern, clean design

### Online Tools:
- Canva.com
- Figma.com
- GIMP (free)
- Photoshop

### Simple SVG Icon Code:
```svg
<svg width="128" height="128" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0066cc"/>
      <stop offset="100%" style="stop-color:#004499"/>
    </linearGradient>
  </defs>
  <rect width="128" height="128" rx="20" fill="url(#grad)"/>
  <text x="64" y="70" font-family="Arial, sans-serif" font-size="36" font-weight="bold" text-anchor="middle" fill="white">AI</text>
  <circle cx="32" cy="40" r="3" fill="white"/>
  <circle cx="64" cy="35" r="3" fill="white"/>
  <circle cx="96" cy="40" r="3" fill="white"/>
</svg>
```

Convert this SVG to PNG at different sizes using any SVG to PNG converter.
