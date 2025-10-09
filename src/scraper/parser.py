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
        """Extract work experience with full details.
        
        Extracts comprehensive job information including:
        - Job title and company
        - Employment type (Full-time, Part-time, etc.)
        - Duration and location
        - Full job description with proper text formatting
        - Skills used in each role
        - Media/attachments if present
        """
        experiences = []
        
        # Modern LinkedIn selectors for experience section
        section_selectors = [
            'section[id*="experience"]',
            'section[data-section="experience"]',
            'div#experience-section',
            'section.pv-profile-section.experience-section',
        ]
        
        section = None
        for selector in section_selectors:
            section = soup.select_one(selector)
            if section:
                break
        
        if not section:
            return experiences
        
        # Find all experience items with multiple selector patterns
        item_selectors = [
            'li.pvs-list__paged-list-item',
            'li.artdeco-list__item',
            'li[class*="profile"]',
            'div.pv-entity__position-group-pager',
            'li.pv-entity__position-group-pager',
        ]
        
        items = []
        for selector in item_selectors:
            found_items = section.select(selector)
            if found_items:
                items = found_items
                break
        
        for item in items:
            exp = self._extract_single_experience(item)
            if exp and (exp.get("title") or exp.get("company")):
                experiences.append(exp)
        
        return experiences
    
    def _extract_single_experience(self, item) -> Optional[Dict[str, str]]:
        """Extract details from a single experience item.
        
        Args:
            item: BeautifulSoup element containing experience data
            
        Returns:
            Dictionary with experience details or None
        """
        exp = {}
        
        # Job Title - try multiple selectors
        title_selectors = [
            'div.display-flex.align-items-center span[aria-hidden="true"]',
            'div[class*="entity-result__title"] span[aria-hidden="true"]',
            'div.t-bold span',
            'h3 span[aria-hidden="true"]',
            'div.mr1.t-bold span',
            '.pv-entity__role-details-container div.t-bold',
        ]
        
        for selector in title_selectors:
            title = self._safe_extract(item, selector)
            if title and len(title) > 0:
                exp["title"] = title
                break
        
        # Company Name - try multiple selectors
        company_selectors = [
            'span.t-14.t-normal span[aria-hidden="true"]',
            'div.pv-entity__secondary-title',
            'span.pv-entity__secondary-title',
            'div[class*="company-name"]',
            'a[data-control-name*="background_details_company"]',
        ]
        
        for selector in company_selectors:
            company = self._safe_extract(item, selector)
            if company and len(company) > 0 and company != exp.get("title"):
                exp["company"] = company
                break
        
        # Employment Type (Full-time, Part-time, Contract, etc.)
        employment_type_selectors = [
            'span.t-14.t-normal.t-black--light span[aria-hidden="true"]',
            'span.pv-entity__secondary-title',
        ]
        
        for selector in employment_type_selectors:
            elements = item.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                # Check if it matches employment type patterns
                if any(emp_type in text for emp_type in [
                    'Full-time', 'Part-time', 'Contract', 'Freelance', 
                    'Internship', 'Self-employed', 'Seasonal'
                ]):
                    exp["employment_type"] = text
                    break
            if "employment_type" in exp:
                break
        
        # Duration - try multiple selectors
        duration_selectors = [
            'span.t-14.t-normal.t-black--light span[aria-hidden="true"]',
            'span.pv-entity__date-range span:nth-child(2)',
            'div.pv-entity__date-range span',
            'span[class*="date-range"]',
        ]
        
        for selector in duration_selectors:
            duration = self._safe_extract(item, selector)
            if duration and ('-' in duration or 'Present' in duration or 'yr' in duration or 'mo' in duration):
                exp["duration"] = duration
                break
        
        # Location
        location_selectors = [
            'span.t-14.t-normal.t-black--light span.visually-hidden',
            'span.pv-entity__location span:nth-child(2)',
            'div.pv-entity__location span',
        ]
        
        for selector in location_selectors:
            location = self._safe_extract(item, selector)
            if location and location != exp.get("duration"):
                exp["location"] = location
                break
        
        # Job Description - CRITICAL: Extract full text with paragraph preservation
        description_selectors = [
            'div.pv-shared-text-with-see-more span[aria-hidden="true"]',
            'div.inline-show-more-text span[aria-hidden="true"]',
            'div[class*="show-more-less"] span[aria-hidden="true"]',
            'div.pv-entity__description',
            'div[class*="description"]',
        ]
        
        for selector in description_selectors:
            try:
                element = item.select_one(selector)
                if element:
                    # Preserve paragraphs and line breaks
                    description = element.get_text(separator='\n', strip=True)
                    if description and len(description) > 10:
                        exp["description"] = description
                        break
            except Exception:
                continue
        
        # Skills - extract skills mentioned for this role
        skills_selectors = [
            'div[class*="skill"] span[aria-hidden="true"]',
            'div.pv-skill-category-entity__name span',
        ]
        
        skills = []
        for selector in skills_selectors:
            skill_elements = item.select(selector)
            for skill_elem in skill_elements:
                skill = skill_elem.get_text(strip=True)
                if skill and len(skill) < 50:
                    skills.append(skill)
        
        if skills:
            exp["skills"] = skills
        
        return exp if exp else None

    def _extract_education(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract education with comprehensive details.
        
        Extracts full education information including:
        - Institution name and logo
        - Degree type and field of study
        - Duration (start and end dates)
        - Grade/GPA if available
        - Activities and societies
        - Description
        """
        education = []
        
        # Modern LinkedIn selectors for education section
        section_selectors = [
            'section[id*="education"]',
            'section[data-section="education"]',
            'div#education-section',
            'section.pv-profile-section.education-section',
        ]
        
        section = None
        for selector in section_selectors:
            section = soup.select_one(selector)
            if section:
                break
        
        if not section:
            return education
        
        # Find all education items
        item_selectors = [
            'li.pvs-list__paged-list-item',
            'li.artdeco-list__item',
            'li[class*="profile"]',
            'div.pv-education-entity',
        ]
        
        items = []
        for selector in item_selectors:
            found_items = section.select(selector)
            if found_items:
                items = found_items
                break
        
        for item in items:
            edu = self._extract_single_education(item)
            if edu and (edu.get("institution") or edu.get("degree")):
                education.append(edu)
        
        return education
    
    def _extract_single_education(self, item) -> Optional[Dict[str, str]]:
        """Extract details from a single education item.
        
        Args:
            item: BeautifulSoup element containing education data
            
        Returns:
            Dictionary with education details or None
        """
        edu = {}
        
        # Institution Name
        institution_selectors = [
            'div.display-flex.align-items-center span[aria-hidden="true"]',
            'h3 span[aria-hidden="true"]',
            'div.t-bold span',
            'div.pv-entity__school-name',
        ]
        
        for selector in institution_selectors:
            institution = self._safe_extract(item, selector)
            if institution and len(institution) > 0:
                edu["institution"] = institution
                break
        
        # Degree and Field of Study
        degree_selectors = [
            'span.t-14.t-normal span[aria-hidden="true"]',
            'div.pv-entity__degree-name span',
            'p.pv-entity__secondary-title',
        ]
        
        degree_text = None
        for selector in degree_selectors:
            degree_text = self._safe_extract(item, selector)
            if degree_text and len(degree_text) > 0:
                # Try to split degree and field if in one string
                if ',' in degree_text:
                    parts = degree_text.split(',', 1)
                    edu["degree"] = parts[0].strip()
                    if len(parts) > 1:
                        edu["field"] = parts[1].strip()
                else:
                    edu["degree"] = degree_text
                break
        
        # Field of Study (if not already extracted)
        if "field" not in edu:
            field_selectors = [
                'span.t-14.t-normal span[aria-hidden="true"]',
                'div.pv-entity__fos span',
                'p.pv-entity__fos',
            ]
            
            for selector in field_selectors:
                elements = item.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and text != edu.get("degree") and text != edu.get("institution"):
                        edu["field"] = text
                        break
                if "field" in edu:
                    break
        
        # Duration
        duration_selectors = [
            'span.t-14.t-normal.t-black--light span[aria-hidden="true"]',
            'span.pv-entity__dates span:nth-child(2)',
            'div.pv-entity__dates span',
        ]
        
        for selector in duration_selectors:
            duration = self._safe_extract(item, selector)
            if duration and ('-' in duration or 'Present' in duration or len(duration) >= 4):
                edu["duration"] = duration
                break
        
        # Grade/GPA
        grade_selectors = [
            'span[class*="grade"]',
            'div.pv-entity__grade span',
        ]
        
        for selector in grade_selectors:
            grade = self._safe_extract(item, selector)
            if grade:
                edu["grade"] = grade
                break
        
        # Activities and Societies
        activities_selectors = [
            'div.pv-entity__extra-details span',
            'div[class*="activities"] span[aria-hidden="true"]',
        ]
        
        for selector in activities_selectors:
            activities = self._safe_extract(item, selector)
            if activities and len(activities) > 5:
                edu["activities"] = activities
                break
        
        # Description
        description_selectors = [
            'div.pv-shared-text-with-see-more span[aria-hidden="true"]',
            'div.inline-show-more-text span[aria-hidden="true"]',
            'div.pv-entity__description',
        ]
        
        for selector in description_selectors:
            try:
                element = item.select_one(selector)
                if element:
                    description = element.get_text(separator='\n', strip=True)
                    if description and len(description) > 10:
                        edu["description"] = description
                        break
            except Exception:
                continue
        
        return edu if edu else None

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
