# Task 6: Enhanced Languages Section Implementation Guide 🌐

## Overview
Enhance the Languages section to extract and display proficiency levels, making it more informative and professional.

**Status:** 🚧 IN PROGRESS  
**Priority:** HIGH  
**Estimated Time:** 30-45 minutes

---

## Current State

### Existing Implementation
- Basic language name extraction
- Simple list display
- LinkedIn blue badges
- No proficiency levels

### What's Missing
- Proficiency levels (Native, Professional, Limited, etc.)
- Structured data format
- Visual proficiency indicators
- Better styling

---

## 🎯 Goals

1. Extract language proficiency levels from LinkedIn HTML
2. Create structured language data: `{name: str, proficiency: str}`
3. Design professional template with proficiency indicators
4. Add visual elements (flags emoji, proficiency bars/badges)
5. Maintain backward compatibility

---

## 📋 Implementation Steps

### Step 1: Update Parser (parser.py)

#### Current Code:
```python
def _extract_languages(self, soup: BeautifulSoup) -> List[str]:
    """Extract languages."""
    languages = []
    section = soup.find("section", {"id": re.compile(r".*languages.*")})

    if section:
        lang_elements = section.find_all("div", {"class": re.compile(r".*language.*")})
        for element in lang_elements:
            lang = element.get_text(strip=True)
            if lang:
                languages.append(lang)

    return languages
```

#### Enhanced Code:
```python
def _extract_languages(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract languages with proficiency levels.
    
    Returns:
        List of dictionaries: {name: str, proficiency: str}
    """
    languages = []
    
    # Modern LinkedIn selectors for languages section
    section_selectors = [
        'section[id*="languages"]',
        'section[data-section="languages"]',
        'div#languages-section',
        'section.pv-profile-section.languages-section',
    ]
    
    section = None
    for selector in section_selectors:
        section = soup.select_one(selector)
        if section:
            break
    
    if not section:
        return languages
    
    # Find language items
    item_selectors = [
        'li.pvs-list__paged-list-item',
        'li.artdeco-list__item',
        'li[class*="language"]',
    ]
    
    items = []
    for selector in item_selectors:
        found_items = section.select(selector)
        if found_items:
            items = found_items
            break
    
    for item in items:
        lang_data = self._extract_single_language(item)
        if lang_data and lang_data.get('name'):
            languages.append(lang_data)
    
    # Fallback: Simple extraction
    if not languages:
        lang_elements = section.find_all("div", {"class": re.compile(r".*language.*")})
        for element in lang_elements:
            lang_name = element.get_text(strip=True)
            if lang_name and len(lang_name) < 100:
                languages.append({'name': lang_name, 'proficiency': 'Unknown'})
    
    return languages

def _extract_single_language(self, item) -> Optional[Dict[str, str]]:
    """Extract details from a single language item.
    
    Args:
        item: BeautifulSoup element containing language data
        
    Returns:
        Dictionary with language name and proficiency
    """
    lang = {}
    
    # Language Name
    name_selectors = [
        'div.display-flex.align-items-center span[aria-hidden="true"]',
        'h3 span[aria-hidden="true"]',
        'div.t-bold span',
        'span.pv-entity__language-name',
    ]
    
    for selector in name_selectors:
        name = self._safe_extract(item, selector)
        if name and len(name) > 0 and len(name) < 100:
            lang['name'] = name
            break
    
    # Proficiency Level
    proficiency_selectors = [
        'span.t-14.t-normal.t-black--light span[aria-hidden="true"]',
        'div.pv-entity__proficiency',
        'span[class*="proficiency"]',
    ]
    
    for selector in proficiency_selectors:
        proficiency = self._safe_extract(item, selector)
        if proficiency and len(proficiency) > 0:
            lang['proficiency'] = proficiency
            break
    
    # Default proficiency if not found
    if 'name' in lang and 'proficiency' not in lang:
        lang['proficiency'] = 'Professional working proficiency'
    
    return lang if lang else None
```

### Step 2: Update Template (cv_template.html)

#### Current Code:
```html
<!-- Languages Section -->
{% if languages and languages|length > 0 %}
<section class="section">
    <h2 class="section-title">Languages</h2>
    <div class="section-content">
        <div class="languages-list">
            {% for language in languages %}
            <div class="language-item">{{ language }}</div>
            {% endfor %}
        </div>
    </div>
</section>
{% endif %}
```

#### Enhanced Code:
```html
<!-- Languages Section -->
{% if languages and languages|length > 0 %}
<section class="section">
    <h2 class="section-title">Languages</h2>
    <div class="section-content">
        <div class="languages-grid">
            {% for language in languages %}
            <div class="language-item">
                {% if language is mapping %}
                <div class="language-header">
                    <span class="language-icon">🌐</span>
                    <span class="language-name">{{ language.name }}</span>
                </div>
                {% if language.proficiency %}
                <div class="language-proficiency">{{ language.proficiency }}</div>
                {% endif %}
                {% else %}
                <div class="language-header">
                    <span class="language-icon">🌐</span>
                    <span class="language-name">{{ language }}</span>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</section>
{% endif %}
```

### Step 3: Update CSS (style.css)

#### Enhanced Styles:
```css
/* Languages Section */
.languages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.language-item {
  background: var(--background-light);
  padding: var(--spacing-md);
  border-radius: 8px;
  border: 1px solid var(--border-light);
  transition: all 0.2s ease;
}

.language-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
}

.language-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.language-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.language-proficiency {
  font-size: 13px;
  color: var(--text-muted);
  font-style: italic;
  padding-left: 28px; /* Align with name */
}

/* Print optimization */
@media print {
  .language-item {
    break-inside: avoid;
  }
}
```

---

## 🎨 Design Features

### Proficiency Levels (LinkedIn Standard)
- Native or bilingual proficiency
- Full professional proficiency
- Professional working proficiency
- Limited working proficiency
- Elementary proficiency

### Visual Elements
- 🌐 Globe icon for each language
- Card-based layout
- Responsive grid (auto-fill)
- Hover effects (for web view)
- Professional typography

---

## ✅ Testing Checklist

- [ ] Parser extracts language names correctly
- [ ] Parser extracts proficiency levels
- [ ] Backward compatibility with string format
- [ ] Template handles both dict and string formats
- [ ] CSS renders correctly on PDF
- [ ] Grid layout is responsive
- [ ] Tests updated and passing

---

## 📝 Implementation Notes

### Backward Compatibility
- Template checks `language is mapping` before accessing dict keys
- Falls back to simple string display if old format
- Parser provides default proficiency if not found

### Edge Cases
- Languages without proficiency levels
- Empty languages section
- Malformed HTML
- Very long language names

---

## 🚀 Next Steps After Task 6

After completing languages, proceed with:
1. **Task 7:** Enhanced Certifications with badges and expiry dates
2. **Task 8:** Volunteer Experience with details
3. **Task 9:** Projects with descriptions and links
4. **Task 10:** Publications with citations

---

**Estimated Completion:** 30-45 minutes  
**Files to Modify:** 3 (parser.py, cv_template.html, style.css)  
**Commits:** 1 feature commit
