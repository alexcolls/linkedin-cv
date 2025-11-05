# CV Template Guide

The LinkedIn CV Generator includes four professionally designed templates, each with unique styling and layout to suit different professional contexts.

## Available Themes

### 1. 🎨 Modern Professional (Default)

**Best for**: Tech professionals, designers, modern industries

**Features**:
- Two-column layout with gradient header
- Timeline visualization for experience
- Progress bars for skills
- SVG icons throughout
- Clean, contemporary design

**Colors**:
- Primary: Deep Blue (`#2563eb`)
- Accent: Gold (`#f59e0b`)

**Typography**: Inter + Poppins (sans-serif, modern)

**Usage**:
```bash
poetry run python -m src.cli --theme modern https://linkedin.com/in/username
```

---

### 2. ✨ Creative Bold

**Best for**: Creative professionals, marketers, startups

**Features**:
- Asymmetric three-column layout
- Vibrant gradient backgrounds
- Gradient skill badges
- Bold uppercase typography
- Organic shape borders for profile photo
- Card-based sections

**Colors**:
- Primary: Purple (`#7c3aed`)
- Secondary: Pink (`#ec4899`)
- Accent: Green (`#10b981`)

**Typography**: Montserrat + Raleway (bold, dynamic)

**Usage**:
```bash
poetry run python -m src.cli --theme creative https://linkedin.com/in/username
```

---

### 3. 👔 Executive Elegant

**Best for**: Senior executives, finance, legal, traditional industries

**Features**:
- Traditional single-column centered layout
- Elegant decorative dividers
- Serif typography for sophisticated look
- Text-indented professional summary
- Formal contact bar
- Refined spacing and white space

**Colors**:
- Primary: Navy (`#1e3a8a`)
- Secondary: Burgundy (`#881337`)
- Accent: Gold (`#b45309`)

**Typography**: Playfair Display + Source Serif Pro (serif, refined)

**Usage**:
```bash
poetry run python -m src.cli --theme executive https://linkedin.com/in/username
```

---

### 4. 📘 Classic

**Best for**: General professional use, traditional format

**Features**:
- Original single-column design
- LinkedIn-inspired styling
- Clean, professional layout
- Conservative color scheme
- Maximum compatibility

**Colors**:
- Primary: LinkedIn Blue (`#0a66c2`)
- Accent: Green

**Typography**: Segoe UI + Helvetica Neue

**Usage**:
```bash
poetry run python -m src.cli --theme classic https://linkedin.com/in/username
```

---

## Theme Selection

### Command Line

```bash
# Using default theme (modern)
poetry run python -m src.cli https://linkedin.com/in/username

# Specifying a theme
poetry run python -m src.cli --theme creative https://linkedin.com/in/username
poetry run python -m src.cli --theme executive https://linkedin.com/in/username
poetry run python -m src.cli --theme classic https://linkedin.com/in/username

# List all available themes
poetry run python -m src.cli --list-themes
```

### Interactive Menu

```bash
./run.sh
# Select option 1: Generate CV PDF
# Theme selection will be prompted
```

---

## Color Customization

All themes support custom color overrides for branding or personal preference.

### Override Primary Color

```bash
poetry run python -m src.cli --theme modern \
  --color-primary "#FF5733" \
  https://linkedin.com/in/username
```

### Override Accent Color

```bash
poetry run python -m src.cli --theme modern \
  --color-accent "#C70039" \
  https://linkedin.com/in/username
```

### Override Both Colors

```bash
poetry run python -m src.cli --theme executive \
  --color-primary "#2C3E50" \
  --color-accent "#E74C3C" \
  https://linkedin.com/in/username
```

### Color Format

- Must be in hexadecimal format: `#RRGGBB`
- Both uppercase and lowercase accepted
- Leading `#` is required

---

## QR Code Integration

All templates include optional QR codes linking to your LinkedIn profile.

### Enable/Disable QR Codes

```bash
# Enable QR code (default)
poetry run python -m src.cli --add-qr-code https://linkedin.com/in/username

# Disable QR code
poetry run python -m src.cli --no-qr-code https://linkedin.com/in/username
```

### QR Code Features

- Automatically generated from LinkedIn profile URL
- High error correction for reliability
- Optimized size (70-80px) for scanning
- Theme-specific styling:
  - **Modern**: White container with shadow on gradient background
  - **Creative**: Vibrant gradient background
  - **Executive**: Formal border with divider line
  - **Classic**: Simple footer placement

---

## Template Comparison

| Feature | Modern | Creative | Executive | Classic |
|---------|--------|----------|-----------|---------|
| **Layout** | Two-column | Three-column | Single-column | Single-column |
| **Header Style** | Gradient | Bold Color Block | Centered Elegant | Simple |
| **Typography** | Sans-serif | Bold Sans-serif | Serif | Sans-serif |
| **Skill Display** | Progress Bars | Gradient Badges | Grid List | Simple List |
| **Experience** | Timeline | Cards | Traditional | List |
| **Best For** | Tech/Modern | Creative/Startup | Executive/Traditional | General |
| **Visual Impact** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Professional** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Print Friendly** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## Template Structure

Each template consists of:

```
src/pdf/templates/{theme}/
├── cv_template.html    # HTML structure with Jinja2 variables
└── style.css           # Theme-specific CSS styling
```

### Template Variables

All templates use the following Jinja2 variables from profile data:

**Personal Information**:
- `name` - Full name
- `headline` - Professional headline
- `location` - Geographic location
- `profile_image_data` - Base64 encoded profile picture
- `linkedin_url` - LinkedIn profile URL
- `qr_code` - QR code data URI (optional)

**Contact Information**:
- `email` - Email address
- `phone` - Phone number
- `website` - Personal website

**Professional Data**:
- `about` - Professional summary
- `experience` - List of work experiences
- `education` - List of educational background
- `skills` - List of skills
- `certifications` - List of certifications
- `projects` - List of projects
- `volunteer` - Volunteer experience
- `languages` - Languages spoken

---

## Creating Custom Templates

To create your own template:

1. Create a new directory in `src/pdf/templates/`:
   ```bash
   mkdir src/pdf/templates/mytheme
   ```

2. Create HTML template (`cv_template.html`):
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <meta charset="UTF-8">
       <title>{{ name }} - CV</title>
   </head>
   <body>
       <h1>{{ name }}</h1>
       <p>{{ headline }}</p>
       <!-- Add more sections using Jinja2 variables -->
   </body>
   </html>
   ```

3. Create stylesheet (`style.css`):
   ```css
   body {
       font-family: Arial, sans-serif;
       color: #333;
   }
   h1 {
       color: var(--primary-color, #000);
   }
   ```

4. Use the custom template:
   ```bash
   poetry run python -m src.cli --theme mytheme https://linkedin.com/in/username
   ```

### Color Variables

Templates can use CSS variables for color customization:

- `--primary-color` - Main brand color
- `--accent-color` - Secondary highlight color
- `--primary-dark` - Darker shade of primary
- `--primary-light` - Lighter shade of primary
- `--text-primary` - Main text color
- `--text-secondary` - Secondary text color
- `--background-white` - Background color

---

## Troubleshooting

### Template Not Found

```
Error: Invalid theme: 'mytheme'. Available themes: modern, creative, executive, classic
```

**Solution**: Use `--list-themes` to see available options or check spelling.

### Colors Not Applied

**Issue**: Custom colors not showing up in PDF.

**Solutions**:
1. Verify hex format includes `#` prefix
2. Check that template uses CSS variables (`var(--primary-color)`)
3. Ensure colors are valid 6-digit hex codes

### QR Code Not Appearing

**Issue**: QR code section missing from PDF.

**Solutions**:
1. Verify `--add-qr-code` flag is set (enabled by default)
2. Check that a valid LinkedIn URL was provided
3. Ensure `qrcode` package is installed: `poetry install`

### Layout Issues

**Issue**: Content overlapping or misaligned.

**Solutions**:
1. Try a different theme suited to your content volume
2. Very long text may require layout adjustments
3. Check for special characters in profile data

---

## Best Practices

### Theme Selection

1. **Match your industry**: 
   - Tech → Modern
   - Creative → Creative
   - Finance/Legal → Executive
   - General → Classic

2. **Consider the recipient**:
   - Startup → Creative or Modern
   - Corporation → Executive or Classic
   - Creative agency → Creative
   - Tech company → Modern

3. **Content volume**:
   - Extensive experience → Modern (two-column fits more)
   - Concise profile → Executive (single-column, elegant)
   - Mixed content → Creative (three-column layout)

### Color Customization

1. **Brand alignment**: Use company colors for internal applications
2. **Readability**: Ensure sufficient contrast (dark text on light background)
3. **Professional tone**: Avoid overly bright or neon colors
4. **Consistency**: Use complementary colors that work together

### QR Codes

1. **When to include**:
   - ✅ Digital submission (PDF via email/portal)
   - ✅ Print copies for networking events
   - ✅ Portfolio presentations

2. **When to exclude**:
   - ❌ ATS (Applicant Tracking Systems) - may cause parsing issues
   - ❌ Plain text resume requirements
   - ❌ When specifically instructed not to include

---

## Examples

### Example 1: Tech Startup Application

```bash
poetry run python -m src.cli \
  --theme creative \
  --color-primary "#5851DB" \
  --color-accent "#01FF89" \
  --add-qr-code \
  https://linkedin.com/in/username
```

### Example 2: Financial Services Role

```bash
poetry run python -m src.cli \
  --theme executive \
  --color-primary "#1e3a8a" \
  --no-qr-code \
  https://linkedin.com/in/username
```

### Example 3: General Professional Use

```bash
poetry run python -m src.cli \
  --theme modern \
  https://linkedin.com/in/username
```

### Example 4: Creative Portfolio

```bash
poetry run python -m src.cli \
  --theme creative \
  --add-qr-code \
  https://linkedin.com/in/username
```

---

## Template Development

### Testing Templates

Test your template with sample data:

```bash
# Generate with test profile
poetry run pytest tests/test_template_manager.py -v

# Visual inspection
poetry run python -m src.cli --theme yourtheme test-profile
```

### Template Guidelines

1. **Responsive design**: Consider different content volumes
2. **Print optimization**: Use `@media print` for printer-friendly styles
3. **Page breaks**: Use `page-break-inside: avoid` for sections
4. **Font loading**: Use web-safe fonts or embed fonts
5. **Color variables**: Support CSS variable overrides

---

## Support

For issues or questions about templates:

1. Check this documentation
2. Review existing templates in `src/pdf/templates/`
3. Open an issue on GitHub with template name and issue description

---

**Last Updated**: v0.6.0  
**Templates**: 4 (Modern, Creative, Executive, Classic)  
**Customization**: Colors, QR codes, Layout
