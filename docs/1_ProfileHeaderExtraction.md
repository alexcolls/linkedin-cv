# Task 2: Profile Header Extraction

## 🎯 Objective
Extract complete profile header information from LinkedIn HTML to display in PDF.

---

## 📋 What to Extract

### 1. **Profile Photo** 📸
- High-resolution profile image
- Fallback to placeholder if not available
- Target size: 120-150px circular

### 2. **Full Name** 👤
- User's full name
- Display prominently (32px font)

### 3. **Professional Headline** 💼
- Current role/title
- Company if mentioned
- Display: 18px font, secondary color

### 4. **Location** 📍
- City, State/Country
- Display with location icon

### 5. **Contact Information** (if public) 📧
- Email address
- Phone number
- Website/Portfolio URL
- LinkedIn profile URL

### 6. **Profile Stats** (if available) 📊
- Number of connections
- Number of followers

### 7. **About Section** 📝
- Full professional summary
- Preserve all paragraphs
- Maintain line breaks
- No character limits

---

## 🔧 Implementation

### Step 1: Update Parser - Multiple Selectors

**File: `src/scraper/parser.py`**

Add fallback selectors for each field:

```python
class ProfileParser:
    """Parses LinkedIn profile HTML to extract structured data."""
    
    # Modern LinkedIn selectors (2024)
    SELECTORS = {
        'name': [
            'h1.text-heading-xlarge',
            'h1[class*="top-card"]',
            '[data-generated-suggestion-target]',
            'div.pv-text-details__left-panel h1',
            'h1.inline.t-24',
        ],
        'headline': [
            'div.text-body-medium.break-words',
            'div[class*="headline"]',
            'div.pv-text-details__left-panel div.text-body-medium',
            'h2.mt1.t-18',
        ],
        'location': [
            'span.text-body-small.inline.t-black--light.break-words',
            'div.pv-text-details__left-panel span.text-body-small',
            'span.t-16.t-black.t-normal',
        ],
        'profile_photo': [
            'img.pv-top-card-profile-picture__image',
            'img[class*="profile-photo"]',
            'button img[data-ghost-classes]',
            'div.profile-photo-edit__preview img',
        ],
        'about': [
            'div.pv-shared-text-with-see-more span[aria-hidden="true"]',
            'section[data-section="summary"] span[aria-hidden="true"]',
            'div.pv-about__summary-text span',
            'div.inline-show-more-text span[aria-hidden="true"]',
        ],
        'contact': {
            'email': [
                'a[href^="mailto:"]',
                'section.pv-contact-info a[href^="mailto:"]',
            ],
            'phone': [
                'span.t-14.t-black.t-normal[class*="phone"]',
                'section.pv-contact-info span[class*="phone"]',
            ],
            'website': [
                'a.pv-contact-info__contact-link',
                'section.pv-contact-info a[href^="http"]',
            ],
        },
        'stats': {
            'connections': [
                'span.t-bold[class*="connection"]',
                'li.pv-top-card--list-bullet span.t-bold',
            ],
            'followers': [
                'span.t-bold[class*="follower"]',
            ],
        },
    }
```

### Step 2: Implement Extraction Methods

```python
def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
    """Extract profile name with multiple fallbacks."""
    for selector in self.SELECTORS['name']:
        try:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        except Exception:
            continue
    return "Name Not Found"

def _extract_headline(self, soup: BeautifulSoup) -> Optional[str]:
    """Extract professional headline."""
    for selector in self.SELECTORS['headline']:
        try:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Skip if it's just the location
                if text and 'connections' not in text.lower():
                    return text
        except Exception:
            continue
    return None

def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
    """Extract location with validation."""
    for selector in self.SELECTORS['location']:
        try:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Validate it looks like a location
                if text and len(text) < 100:
                    return text
        except Exception:
            continue
    return None

def _extract_profile_picture(self, soup: BeautifulSoup) -> Optional[str]:
    """Extract profile picture URL."""
    for selector in self.SELECTORS['profile_photo']:
        try:
            img = soup.select_one(selector)
            if img and img.get('src'):
                src = img['src']
                # Prefer higher resolution
                if 'https' in src and 'profile' in src.lower():
                    return src
        except Exception:
            continue
    return None

def _extract_about(self, soup: BeautifulSoup) -> Optional[str]:
    """Extract About/Summary section with full text."""
    for selector in self.SELECTORS['about']:
        try:
            element = soup.select_one(selector)
            if element:
                # Get text preserving paragraphs
                text = element.get_text(separator='\n\n', strip=True)
                if text and len(text) > 20:  # Ensure substantial content
                    return text
        except Exception:
            continue
    return None

def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
    """Extract contact information."""
    contact = {}
    
    # Email
    for selector in self.SELECTORS['contact']['email']:
        try:
            element = soup.select_one(selector)
            if element and element.get('href'):
                email = element['href'].replace('mailto:', '')
                if '@' in email:
                    contact['email'] = email
                    break
        except Exception:
            continue
    
    # Phone
    for selector in self.SELECTORS['contact']['phone']:
        try:
            element = soup.select_one(selector)
            if element:
                phone = element.get_text(strip=True)
                if phone:
                    contact['phone'] = phone
                    break
        except Exception:
            continue
    
    # Website
    for selector in self.SELECTORS['contact']['website']:
        try:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href', '')
                if href and 'linkedin.com' not in href:
                    contact['website'] = href
                    break
            if 'website' in contact:
                break
        except Exception:
            continue
    
    return contact

def _extract_stats(self, soup: BeautifulSoup) -> Dict[str, str]:
    """Extract profile statistics."""
    stats = {}
    
    # Connections
    for selector in self.SELECTORS['stats']['connections']:
        try:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Extract number
                import re
                numbers = re.findall(r'\d+[\d,]*', text)
                if numbers:
                    stats['connections'] = numbers[0]
                    break
        except Exception:
            continue
    
    # Followers
    for selector in self.SELECTORS['stats']['followers']:
        try:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                import re
                numbers = re.findall(r'\d+[\d,]*', text)
                if numbers:
                    stats['followers'] = numbers[0]
                    break
        except Exception:
            continue
    
    return stats
```

### Step 3: Update parse() Method

```python
def parse(self, html_content: str) -> Dict[str, Any]:
    """Parse LinkedIn profile HTML and extract all sections."""
    soup = BeautifulSoup(html_content, "lxml")
    
    profile_data = {
        "username": self._extract_username(soup),
        "name": self._extract_name(soup),
        "headline": self._extract_headline(soup),
        "location": self._extract_location(soup),
        "profile_picture_url": self._extract_profile_picture(soup),
        "about": self._extract_about(soup),
        "contact_info": self._extract_contact_info(soup),  # NEW
        "stats": self._extract_stats(soup),                # NEW
        # ... rest of sections
    }
    
    return profile_data
```

---

## 📄 Update PDF Template

**File: `src/pdf/templates/cv_template.html`**

Enhance header section:

```html
<!-- Header Section -->
<header class="header">
    {% if profile_image_data %}
    <div class="profile-photo">
        <img src="{{ profile_image_data }}" alt="{{ name }}">
    </div>
    {% endif %}
    
    <div class="header-content">
        {% if name %}
        <h1 class="name">{{ name }}</h1>
        {% endif %}
        
        {% if headline %}
        <div class="headline">{{ headline }}</div>
        {% endif %}
        
        {% if location %}
        <div class="location">📍 {{ location }}</div>
        {% endif %}
        
        {% if stats %}
        <div class="stats">
            {% if stats.connections %}
            <span class="stat-item">🔗 {{ stats.connections }} connections</span>
            {% endif %}
            {% if stats.followers %}
            <span class="stat-item">👥 {{ stats.followers }} followers</span>
            {% endif %}
        </div>
        {% endif %}
        
        {% if contact_info %}
        <div class="contact-info">
            {% if contact_info.email %}
            <div class="contact-item">
                <span class="contact-icon">📧</span>
                <span>{{ contact_info.email }}</span>
            </div>
            {% endif %}
            {% if contact_info.phone %}
            <div class="contact-item">
                <span class="contact-icon">📱</span>
                <span>{{ contact_info.phone }}</span>
            </div>
            {% endif %}
            {% if contact_info.website %}
            <div class="contact-item">
                <span class="contact-icon">🌐</span>
                <span>{{ contact_info.website }}</span>
            </div>
            {% endif %}
        </div>
        {% endif %}
    </div>
</header>
```

---

## 🎨 Update CSS Styling

**File: `src/pdf/templates/style.css`**

Add styles for new elements:

```css
/* Stats display */
.stats {
    margin-top: 8px;
    display: flex;
    gap: 16px;
    font-size: 13px;
    color: var(--text-muted);
}

.stat-item {
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

/* Contact info grid */
.contact-info {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-light);
}

.contact-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--text-secondary);
}

.contact-icon {
    font-size: 14px;
}

/* About section enhancement */
.about-text {
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-secondary);
    text-align: justify;
    white-space: pre-wrap;  /* Preserve line breaks */
}
```

---

## ✅ Testing

### Test Script

```bash
# Create test script
cat > test_header.py << 'EOF'
from pathlib import Path
from src.scraper.parser import ProfileParser

# Load your LinkedIn HTML
html = Path('linkedin-profile.html').read_text()

# Parse
parser = ProfileParser()
data = parser.parse(html)

# Check header data
print("=== Profile Header ===")
print(f"Name: {data.get('name')}")
print(f"Headline: {data.get('headline')}")
print(f"Location: {data.get('location')}")
print(f"Photo URL: {data.get('profile_picture_url')}")
print(f"About (first 100 chars): {data.get('about', '')[:100]}...")
print(f"Contact: {data.get('contact_info')}")
print(f"Stats: {data.get('stats')}")
EOF

poetry run python test_header.py
```

### Verify Output

```bash
# Generate PDF
poetry run python -m src.cli --html-file linkedin-profile.html

# Open and check
xdg-open output/*.pdf
```

### What to Check ✅

- [ ] Name appears large and bold
- [ ] Profile photo shows (circular, 120px)
- [ ] Headline displays correctly
- [ ] Location with icon
- [ ] Contact info (if available)
- [ ] Stats display (connections/followers)
- [ ] About section shows full text with paragraphs
- [ ] No data is truncated

---

## 🐛 Troubleshooting

### Issue: Name not found
**Solution:** Check which selector works in browser console:
```javascript
document.querySelector('h1.text-heading-xlarge')
```

### Issue: About text truncated
**Solution:** Use `get_text(separator='\n\n')` to preserve paragraphs

### Issue: Profile photo not loading
**Solution:** Check if URL is valid, use placeholder if needed

---

## 📝 Completion Checklist

- [ ] Added SELECTORS dictionary with fallbacks
- [ ] Implemented _extract_name() with multiple selectors
- [ ] Implemented _extract_headline()
- [ ] Implemented _extract_location()
- [ ] Implemented _extract_profile_picture()
- [ ] Implemented _extract_about() with paragraph preservation
- [ ] Implemented _extract_contact_info()
- [ ] Implemented _extract_stats()
- [ ] Updated parse() method to include new fields
- [ ] Enhanced HTML template with new sections
- [ ] Added CSS for stats and contact display
- [ ] Tested with real LinkedIn HTML
- [ ] Verified PDF output
- [ ] All header data appears correctly

---

## ➡️ Next Steps

Once header extraction is complete and verified:
1. Commit changes
2. Move to **Task 3: Experience Extraction** (most critical!)
3. Document in `2_ExperienceExtraction.md`

---

**Status: 🔄 In Progress**

**Goal: Extract complete profile header with all available information for professional PDF display.**
