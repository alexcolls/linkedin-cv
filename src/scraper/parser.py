"""LinkedIn profile HTML parser."""
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup


class ProfileParser:
    """Parses LinkedIn profile HTML to extract structured data."""
    
    # Modern LinkedIn selectors (2024) with fallbacks
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
            '.top-card__headline',
        ],
        'location': [
            'span.text-body-small.inline.t-black--light.break-words',
            'div.pv-text-details__left-panel span.text-body-small',
            'span.t-16.t-black.t-normal',
            'div.top-card__subline-item',
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

    def parse(self, html_content: str) -> Dict[str, Any]:
        """Parse LinkedIn profile HTML and extract all sections.

        Args:
            html_content: Raw HTML content from LinkedIn profile

        Returns:
            Dictionary containing all profile data
        """
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
            "experience": self._extract_experience(soup),
            "education": self._extract_education(soup),
            "skills": self._extract_skills(soup),
            "certifications": self._extract_certifications(soup),
            "languages": self._extract_languages(soup),
            "volunteer": self._extract_volunteer(soup),
            "projects": self._extract_projects(soup),
            "publications": self._extract_publications(soup),
            "honors": self._extract_honors(soup),
            "courses": self._extract_courses(soup),
        }

        # Count non-empty sections
        sections = [k for k, v in profile_data.items() if v and k not in ["username"]]
        profile_data["sections"] = sections

        return profile_data

    def _extract_username(self, soup: BeautifulSoup) -> str:
        """Extract LinkedIn username from profile."""
        # Try to extract from URL or meta tags
        canonical = soup.find("link", {"rel": "canonical"})
        if canonical and canonical.get("href"):
            url = canonical["href"]
            match = re.search(r"linkedin\.com/in/([^/]+)", url)
            if match:
                return match.group(1)
        return "linkedin-profile"

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
                    # Skip if it's just the location or connections
                    if text and 'connections' not in text.lower() and len(text) > 0:
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
                    # Validate it looks like a location (not too long, not connections)
                    if text and len(text) < 100 and 'connection' not in text.lower():
                        return text
            except Exception:
                continue
        return None

    def _extract_profile_picture(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract profile picture URL with fallbacks."""
        for selector in self.SELECTORS['profile_photo']:
            try:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    src = img['src']
                    # Prefer https URLs with profile indicator
                    if 'http' in src:
                        return src
            except Exception:
                continue
        return None

    def _extract_about(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract About/Summary section with full text and paragraph preservation."""
        for selector in self.SELECTORS['about']:
            try:
                element = soup.select_one(selector)
                if element:
                    # Get text preserving paragraphs and line breaks
                    text = element.get_text(separator='\n\n', strip=True)
                    if text and len(text) > 20:  # Ensure substantial content
                        return text
            except Exception:
                continue
        return None
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information (email, phone, website)."""
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
        """Extract profile statistics (connections, followers)."""
        stats = {}
        
        # Connections
        for selector in self.SELECTORS['stats']['connections']:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    # Extract number from text
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
                    # Extract number from text
                    numbers = re.findall(r'\d+[\d,]*', text)
                    if numbers:
                        stats['followers'] = numbers[0]
                        break
            except Exception:
                continue
        
        return stats

    def _extract_experience(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract work experience."""
        experiences = []
        section = soup.find("section", {"id": re.compile(r".*experience.*")})

        if section:
            items = section.find_all("li", {"class": re.compile(r".*profile.*")})
            for item in items:
                exp = {
                    "title": self._safe_extract(item, "div.t-bold"),
                    "company": self._safe_extract(item, "span.t-14.t-normal"),
                    "duration": self._safe_extract(item, "span.t-14.t-normal.t-black--light"),
                    "location": self._safe_extract(item, "span.t-14.t-normal"),
                    "description": self._safe_extract(item, "div.inline-show-more-text"),
                }
                if exp["title"] or exp["company"]:
                    experiences.append(exp)

        return experiences

    def _extract_education(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract education."""
        education = []
        section = soup.find("section", {"id": re.compile(r".*education.*")})

        if section:
            items = section.find_all("li", {"class": re.compile(r".*profile.*")})
            for item in items:
                edu = {
                    "institution": self._safe_extract(item, "div.t-bold"),
                    "degree": self._safe_extract(item, "span.t-14.t-normal"),
                    "field": self._safe_extract(item, "span.t-14.t-normal"),
                    "duration": self._safe_extract(item, "span.t-14.t-normal.t-black--light"),
                }
                if edu["institution"] or edu["degree"]:
                    education.append(edu)

        return education

    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract skills."""
        skills = []
        section = soup.find("section", {"id": re.compile(r".*skills.*")})

        if section:
            skill_elements = section.find_all("div", {"class": re.compile(r".*skill.*")})
            for element in skill_elements:
                skill = element.get_text(strip=True)
                if skill and len(skill) < 50:  # Filter out noise
                    skills.append(skill)

        return list(set(skills))  # Remove duplicates

    def _extract_certifications(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract certifications."""
        certifications = []
        section = soup.find("section", {"id": re.compile(r".*licenses.*|.*certifications.*")})

        if section:
            items = section.find_all("li")
            for item in items:
                cert = {
                    "name": self._safe_extract(item, "div.t-bold"),
                    "issuer": self._safe_extract(item, "span.t-14.t-normal"),
                    "date": self._safe_extract(item, "span.t-14.t-normal.t-black--light"),
                }
                if cert["name"]:
                    certifications.append(cert)

        return certifications

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

    def _extract_volunteer(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract volunteer experience."""
        volunteer = []
        section = soup.find("section", {"id": re.compile(r".*volunteer.*")})

        if section:
            items = section.find_all("li")
            for item in items:
                vol = {
                    "role": self._safe_extract(item, "div.t-bold"),
                    "organization": self._safe_extract(item, "span.t-14.t-normal"),
                    "duration": self._safe_extract(item, "span.t-14.t-normal.t-black--light"),
                }
                if vol["role"] or vol["organization"]:
                    volunteer.append(vol)

        return volunteer

    def _extract_projects(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract projects."""
        projects = []
        section = soup.find("section", {"id": re.compile(r".*projects.*")})

        if section:
            items = section.find_all("li")
            for item in items:
                proj = {
                    "name": self._safe_extract(item, "div.t-bold"),
                    "description": self._safe_extract(item, "div.inline-show-more-text"),
                    "date": self._safe_extract(item, "span.t-14.t-normal.t-black--light"),
                }
                if proj["name"]:
                    projects.append(proj)

        return projects

    def _extract_publications(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract publications."""
        publications = []
        section = soup.find("section", {"id": re.compile(r".*publications.*")})

        if section:
            items = section.find_all("li")
            for item in items:
                pub = {
                    "title": self._safe_extract(item, "div.t-bold"),
                    "publisher": self._safe_extract(item, "span.t-14.t-normal"),
                    "date": self._safe_extract(item, "span.t-14.t-normal.t-black--light"),
                }
                if pub["title"]:
                    publications.append(pub)

        return publications

    def _extract_honors(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract honors and awards."""
        honors = []
        section = soup.find("section", {"id": re.compile(r".*honors.*|.*awards.*")})

        if section:
            items = section.find_all("li")
            for item in items:
                honor = {
                    "title": self._safe_extract(item, "div.t-bold"),
                    "issuer": self._safe_extract(item, "span.t-14.t-normal"),
                    "date": self._safe_extract(item, "span.t-14.t-normal.t-black--light"),
                }
                if honor["title"]:
                    honors.append(honor)

        return honors

    def _extract_courses(self, soup: BeautifulSoup) -> List[str]:
        """Extract courses."""
        courses = []
        section = soup.find("section", {"id": re.compile(r".*courses.*")})

        if section:
            course_elements = section.find_all("li")
            for element in course_elements:
                course = element.get_text(strip=True)
                if course:
                    courses.append(course)

        return courses

    def _safe_extract(self, element, selector: str) -> Optional[str]:
        """Safely extract text from an element.

        Args:
            element: BeautifulSoup element
            selector: CSS selector

        Returns:
            Extracted text or None
        """
        try:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        except:
            pass
        return None
