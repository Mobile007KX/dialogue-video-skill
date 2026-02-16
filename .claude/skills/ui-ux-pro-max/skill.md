# UI/UX Pro Max - Design Intelligence

Searchable database of UI styles, color palettes, font pairings, chart types, product recommendations, UX guidelines, and stack-specific best practices.

## When to Use This Skill

Automatically activate when user requests UI/UX work:
- Design, build, create, implement UI
- Review, fix, improve existing UI
- Choose colors, fonts, layouts
- Questions about UI best practices

## Prerequisites

Python 3.x is required. Check with:

```bash
python3 --version
```

If not installed:
- **macOS**: `brew install python3`
- **Ubuntu/Debian**: `sudo apt update && sudo apt install python3`
- **Windows**: `winget install Python.Python.3.12`

## How to Use This Skill

### Step 1: Analyze User Requirements

Extract key information:
- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page, news/media
- **Style keywords**: minimal, playful, professional, elegant, dark mode
- **Industry**: healthcare, fintech, gaming, education, news, beauty
- **Stack**: React, Vue, Next.js, or default to `html-tailwind`

### Step 2: Search Relevant Domains

Use the search script multiple times to gather comprehensive information:

```bash
python3 .claude/skills/ui-ux-pro-max/data/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**Recommended search order:**

1. **Product** - Style recommendations for product type
2. **Style** - Detailed style guide (colors, effects, frameworks)
3. **Typography** - Font pairings with Google Fonts imports
4. **Color** - Color palette (Primary, Secondary, CTA, Background, Text, Border)
5. **Landing** - Page structure (if landing page)
6. **Chart** - Chart recommendations (if dashboard/analytics)
7. **UX** - Best practices and anti-patterns
8. **Stack** - Stack-specific guidelines (default: html-tailwind)

### Available Domains

| Domain | Use For | Example Keywords |
|--------|---------|------------------|
| `product` | Product type recommendations | SaaS, e-commerce, portfolio, healthcare, beauty, news |
| `style` | UI styles, colors, effects | glassmorphism, minimalism, dark mode, brutalism, flat |
| `typography` | Font pairings, Google Fonts | elegant, playful, professional, modern, bold |
| `color` | Color palettes by product type | saas, ecommerce, healthcare, beauty, fintech, news |
| `landing` | Page structure, CTA strategies | hero, hero-centric, testimonial, pricing, social-proof |
| `chart` | Chart types, library recommendations | trend, comparison, timeline, funnel, pie |
| `ux` | Best practices, anti-patterns | animation, accessibility, z-index, loading, contrast |
| `prompt` | AI prompts, CSS keywords | (style name) |

### Stack Guidelines

If user doesn't specify a stack, **default to `html-tailwind`**.

```bash
python3 .claude/skills/ui-ux-pro-max/data/scripts/search.py "<keyword>" --stack html-tailwind
```

Available stacks: `html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`

## Example Workflow

**User request:** "优化政论时评的手机竖屏UI设计"

**You should:**

```bash
# 1. Search product type
python3 .claude/skills/ui-ux-pro-max/data/scripts/search.py "news media political commentary" --domain product

# 2. Search style
python3 .claude/skills/ui-ux-pro-max/data/scripts/search.py "professional modern flat design" --domain style

# 3. Search typography for Chinese
python3 .claude/skills/ui-ux-pro-max/data/scripts/search.py "professional bold modern chinese" --domain typography

# 4. Search color palette
python3 .claude/skills/ui-ux-pro-max/data/scripts/search.py "news media professional" --domain color

# 5. Search UX guidelines
python3 .claude/skills/ui-ux-pro-max/data/scripts/search.py "mobile vertical typography readability contrast" --domain ux

# 6. Search stack guidelines
python3 .claude/skills/ui-ux-pro-max/data/scripts/search.py "html tailwind responsive" --stack html-tailwind
```

**Then:** Synthesize all search results and implement the design.

## Tips for Better Results

1. **Be specific with keywords** - "news media professional" > "app"
2. **Search multiple times** - Different keywords reveal different insights
3. **Combine domains** - Style + Typography + Color = Complete design system
4. **Always check UX** - Search "animation", "z-index", "accessibility", "contrast" for common issues
5. **Use stack flag** - Get implementation-specific best practices
6. **Iterate** - If first search doesn't match, try different keywords

## Common Rules for Professional UI

### Icons & Visual Elements
- ❌ No emoji icons - Use SVG icons (Heroicons, Lucide, Simple Icons)
- ✅ Stable hover states - Use color/opacity transitions, not scale
- ✅ Correct brand logos - Research official SVG from Simple Icons
- ✅ Consistent icon sizing - Use fixed viewBox (24x24) with w-6 h-6

### Interaction & Cursor
- ✅ Add `cursor-pointer` to all clickable/hoverable elements
- ✅ Provide visual feedback on hover (color, shadow, border)
- ✅ Use `transition-colors duration-200` for smooth transitions

### Light/Dark Mode Contrast
- ✅ Light mode glass cards: `bg-white/80` or higher opacity
- ✅ Light mode text: `#0F172A` (slate-900) for body text
- ✅ Muted text: `#475569` (slate-600) minimum
- ✅ Borders: `border-gray-200` in light mode

### Layout & Spacing
- ✅ Floating navbar: Add `top-4 left-4 right-4` spacing
- ✅ Content padding: Account for fixed navbar height
- ✅ Consistent max-width: Use same `max-w-6xl` or `max-w-7xl`

## Pre-Delivery Checklist

Before delivering UI code, verify:

### Visual Quality
- [ ] No emojis used as icons
- [ ] All icons from consistent icon set
- [ ] Brand logos are correct
- [ ] Hover states don't cause layout shift

### Interaction
- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide clear visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation

### Light/Dark Mode
- [ ] Light mode text has sufficient contrast (4.5:1 minimum)
- [ ] Glass/transparent elements visible in light mode
- [ ] Borders visible in both modes
- [ ] Test both modes before delivery

### Layout
- [ ] Floating elements have proper spacing from edges
- [ ] No content hidden behind fixed navbars
- [ ] Responsive at 320px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile

### Accessibility
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator
- [ ] `prefers-reduced-motion` respected
