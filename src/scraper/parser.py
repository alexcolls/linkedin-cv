"""LinkedIn profile HTML parser."""
import json
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup


class ProfileParser:
    """Parses LinkedIn profile HTML to extract structured data."""
    
    def __init__(self, debug: bool = False):
        """Initialize the parser.
        
        Args:
            debug: Enable debug output
        """
        self.debug = debug
    
    # Modern LinkedIn selectors (2024) with fallbacks
    SELECTORS = {
        'name': [
            'h1.text-heading-xlarge',
            'h1.text-heading-xlarge.inline.t-24',  # New pattern from analysis
            'h1[class*="top-card"]',
            '[data-generated-suggestion-target]',
            'div.pv-text-details__left-panel h1',
            'h1.inline.t-24',
        ],
        'headline': [
            'div.text-body-medium.break-words',
            'div.text-body-medium',  # Simplified pattern
            'div[class*="headline"]',
            'div.pv-text-details__left-panel div.text-body-medium',
            'h2.mt1.t-18',
            '.top-card__headline',
        ],
        'location': [
            'span.text-body-small.inline.t-black--light.break-words',
            'span.text-body-small',  # Simplified pattern
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
            'section#about div.pv-shared-text-with-see-more span[aria-hidden="true"]',  # More specific
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

        # Always extract HTML data first
        profile_data = {
            "username": self._extract_username(soup),
            "name": self._extract_name(soup),
            "headline": self._extract_headline(soup),
            "location": self._extract_location(soup),
            "profile_picture_url": self._extract_profile_picture(soup),
            "about": self._extract_about(soup),
            "contact_info": self._extract_contact_info(soup),
            "stats": self._extract_stats(soup),
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
        
        # Try to extract from JSON-LD for additional/missing data
        json_ld_data = self._extract_json_ld(soup)
        if json_ld_data:
            # Merge JSON-LD data, but don't overwrite existing HTML data
            json_ld_profile = self._parse_json_ld(json_ld_data, soup)
            for key, value in json_ld_profile.items():
                # Only use JSON-LD data if HTML extraction didn't find anything
                if not profile_data.get(key) and value:
                    profile_data[key] = value

        # Count non-empty sections
        sections = [k for k, v in profile_data.items() if v and k not in ["username"]]
        profile_data["sections"] = sections

        return profile_data

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract JSON-LD structured data from LinkedIn public profiles."""
        try:
            # Find script tag with JSON-LD data
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                if script.string:
                    data = json.loads(script.string)
                    # Look for the Person schema
                    if isinstance(data, dict) and data.get('@type') == 'Person':
                        return data
                    # Check if it's in a @graph array
                    if isinstance(data, dict) and '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and item.get('@type') == 'Person':
                                return item
        except Exception as e:
            print(f"[DEBUG] Error extracting JSON-LD: {e}")
        return None

    def _parse_json_ld(self, json_data: Dict, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse profile data from JSON-LD structured data."""
        # Extract username from URL
        username = "linkedin-profile"
        if 'sameAs' in json_data:
            match = re.search(r"linkedin\.com/in/([^/]+)", json_data['sameAs'])
            if match:
                username = match.group(1)
        
        # Extract profile picture from JSON-LD
        profile_pic = None
        if 'image' in json_data and isinstance(json_data['image'], dict):
            profile_pic = json_data['image'].get('contentUrl')
        
        return {
            "username": username,
            "name": json_data.get('name', 'Name Not Found'),
            "headline": json_data.get('jobTitle', [None])[0] if isinstance(json_data.get('jobTitle'), list) else json_data.get('jobTitle'),
            "location": self._parse_json_ld_location(json_data.get('address', {})),
            "profile_picture_url": profile_pic,
            "about": json_data.get('disambiguatingDescription', None),
            "contact_info": {},  # Not typically in public JSON-LD
            "stats": self._parse_json_ld_stats(json_data),
            "experience": self._parse_json_ld_experience(json_data.get('worksFor', [])),
            "education": self._parse_json_ld_education(json_data.get('alumniOf', [])),
            "skills": [],  # Not typically in JSON-LD
            "certifications": [],  # Not typically in JSON-LD
            "languages": self._parse_json_ld_languages(json_data.get('knowsLanguage', [])),
            "volunteer": [],  # Not typically in JSON-LD
            "projects": [],  # Not typically in JSON-LD
            "publications": [],  # Not typically in JSON-LD
            "honors": json_data.get('awards', []),
            "courses": [],  # Not typically in JSON-LD
        }
    
    def _parse_json_ld_location(self, address: Dict) -> Optional[str]:
        """Parse location from JSON-LD address object."""
        if not address:
            return None
        parts = []
        if 'addressLocality' in address:
            parts.append(address['addressLocality'])
        if 'addressRegion' in address:
            parts.append(address['addressRegion'])
        if 'addressCountry' in address:
            parts.append(address['addressCountry'])
        return ', '.join(parts) if parts else None
    
    def _parse_json_ld_stats(self, json_data: Dict) -> Dict[str, str]:
        """Parse stats from JSON-LD."""
        stats = {}
        if 'interactionStatistic' in json_data:
            stat = json_data['interactionStatistic']
            if isinstance(stat, dict) and 'userInteractionCount' in stat:
                stats['followers'] = str(stat['userInteractionCount'])
        return stats
    
    def _parse_json_ld_experience(self, works_for: List) -> List[Dict]:
        """Parse experience from JSON-LD worksFor array."""
        if not works_for:
            return []
        
        experiences = []
        for work in works_for:
            if not isinstance(work, dict):
                continue
            
            # Extract the organization and role information
            org_name = work.get('name', '')
            member = work.get('member', {})
            
            if not isinstance(member, dict):
                member = {}
            
            # Parse job title and company from the organization name
            # LinkedIn often combines them like "Senior Engineer at Company"
            title = org_name
            company = None
            
            if ' at ' in org_name:
                parts = org_name.split(' at ', 1)
                title = parts[0].strip()
                company = parts[1].strip()
            elif org_name:
                # Sometimes it's just the company name
                company = org_name
                title = member.get('roleName', 'Position')
            
            # Clean up description
            description = member.get('description', '')
            if description:
                # Remove masking asterisks that LinkedIn sometimes adds
                description = description.replace('*', '')
            
            experience = {
                'title': title,
                'company': company or org_name or 'Company',
                'employment_type': member.get('employmentType'),
                'duration': self._parse_json_ld_duration(member),
                'location': work.get('location') or member.get('location'),
                'description': description if description else None,
                'skills': [],
            }
            experiences.append(experience)
        
        return experiences
    
    def _parse_json_ld_duration(self, member: Dict) -> Optional[str]:
        """Parse duration from member object."""
        start = member.get('startDate')
        end = member.get('endDate')
        
        if not start:
            return None
        
        if end:
            return f"{start} - {end}"
        else:
            return f"{start} - Present"
    
    def _parse_json_ld_education(self, alumni_of: List) -> List[Dict]:
        """Parse education from JSON-LD alumniOf array."""
        if not alumni_of:
            return []
        
        education_list = []
        for edu in alumni_of:
            if not isinstance(edu, dict):
                continue
            
            member = edu.get('member', {})
            if not isinstance(member, dict):
                member = {}
            
            education = {
                'institution': edu.get('name', 'Institution'),
                'degree': None,
                'field': None,
                'duration': self._parse_json_ld_duration(member),
                'grade': None,
                'activities': None,
                'description': None,
            }
            education_list.append(education)
        
        return education_list
    
    def _parse_json_ld_languages(self, languages: List) -> List[Dict]:
        """Parse languages from JSON-LD knowsLanguage array."""
        if not languages:
            return []
        
        language_list = []
        for lang in languages:
            if isinstance(lang, dict):
                language_list.append({
                    'name': lang.get('name', 'Language'),
                    'proficiency': None,  # Not in JSON-LD
                })
            elif isinstance(lang, str):
                language_list.append({
                    'name': lang,
                    'proficiency': None,
                })
        
        return language_list

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

    def _extract_experience(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract work experience with full details including nested roles.
        
        Handles:
        - Single positions
        - Nested positions (multiple roles at same company)
        - Full job descriptions
        - Skills, media attachments
        """
        experiences = []
        
        # Find the experience section
        section = None
        section_selectors = [
            'section#experience',
            'section[id="experience"]',
            'section[data-section="experience"]',
        ]
        
        for selector in section_selectors:
            section = soup.select_one(selector)
            if section:
                if self.debug:
                    print(f"[DEBUG] Found experience section with selector: {selector}")
                break
        
        # If not found, try finding the anchor div and get its parent section
        if not section:
            anchor = soup.select_one('div[id="experience"]')
            if anchor and anchor.parent and anchor.parent.name == 'section':
                section = anchor.parent
                if self.debug:
                    print("[DEBUG] Found experience section via anchor div parent")
        
        if not section:
            if self.debug:
                print("[DEBUG] No experience section found")
            return experiences
        
        # Find experience list containers - LinkedIn uses different structures
        list_containers = section.select('ul, div.pvs-list__container')
        
        for container in list_containers:
            # Get all direct list items (these could be single positions or grouped positions)
            items = container.select(':scope > li')
            
            for item in items:
                # Check if this is a grouped position (multiple roles at same company)
                # Look for nested list inside
                nested_list = item.select_one('ul')
                
                # LinkedIn now uses nested UL for descriptions too, so we need to check
                # if it's actually a grouped experience or just a single role with nested content
                is_truly_grouped = False
                if nested_list:
                    # Check if nested items have role titles (indicates multiple roles)
                    nested_items = nested_list.select(':scope > li')
                    for nested_item in nested_items:
                        # Look for role title indicators
                        title_elem = nested_item.select_one('div.display-flex.align-items-center span[aria-hidden="true"]')
                        if title_elem and len(title_elem.get_text(strip=True)) > 0 and len(title_elem.get_text(strip=True)) < 200:
                            is_truly_grouped = True
                            break
                
                if is_truly_grouped:
                    # This is a company with multiple positions
                    exp = self._extract_grouped_experience(item)
                    if exp:
                        experiences.append(exp)
                else:
                    # This is a single position
                    exp = self._extract_single_experience(item)
                    if exp and exp.get("title"):
                        experiences.append(exp)
        
        return experiences
    
    def _extract_grouped_experience(self, item) -> Optional[Dict[str, Any]]:
        """Extract a grouped experience (multiple roles at same company).
        
        Args:
            item: BeautifulSoup element containing grouped experience data
            
        Returns:
            Dictionary with company info and nested roles
        """
        exp = {}
        
        # Extract company information from the parent item
        company_elem = item.select_one('div.display-flex span[aria-hidden="true"]')
        if company_elem:
            exp["company"] = company_elem.get_text(strip=True)
        
        # Extract total duration at company
        duration_elem = item.select_one('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
        if duration_elem:
            exp["total_duration"] = duration_elem.get_text(strip=True)
        
        # Extract company location if available
        location_elem = item.select_one('span.t-14.t-normal.t-black--light:nth-of-type(2) span[aria-hidden="true"]')
        if location_elem:
            exp["location"] = location_elem.get_text(strip=True)
        
        # Extract nested positions
        roles = []
        nested_items = item.select('ul > li')
        
        for nested_item in nested_items:
            role = {}
            
            # Extract role title
            title_elem = nested_item.select_one('div.display-flex span[aria-hidden="true"]')
            if title_elem:
                role["title"] = title_elem.get_text(strip=True)
            
            # Extract employment type
            emp_type_elem = nested_item.select_one('span.t-14.t-normal span[aria-hidden="true"]')
            if emp_type_elem:
                text = emp_type_elem.get_text(strip=True)
                if any(t in text for t in ['Full-time', 'Part-time', 'Contract', 'Freelance', 'Internship']):
                    role["employment_type"] = text
            
            # Extract role duration
            duration_spans = nested_item.select('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')
            for span in duration_spans:
                text = span.get_text(strip=True)
                if any(marker in text for marker in ['-', 'Present', 'mo', 'yr']):
                    role["duration"] = text
                    break
            
            # Extract role location
            location_spans = nested_item.select('span.t-14.t-normal.t-black--light')
            for span in location_spans:
                text = span.get_text(strip=True)
                if text and text != role.get("duration") and '·' not in text:
                    role["location"] = text
                    break
            
            # Extract role description
            desc_elem = nested_item.select_one('div.pv-shared-text-with-see-more span[aria-hidden="true"]')
            if not desc_elem:
                desc_elem = nested_item.select_one('div.inline-show-more-text span[aria-hidden="true"]')
            if desc_elem:
                role["description"] = desc_elem.get_text(separator='\n', strip=True)
            
            # Extract skills if present
            skills_elem = nested_item.select_one('span.t-14.t-normal:contains("Skills:")')
            if skills_elem:
                skills_text = skills_elem.get_text(strip=True)
                if 'Skills:' in skills_text:
                    skills_list = skills_text.split('Skills:')[1].strip().split('·')
                    role["skills"] = [s.strip() for s in skills_list if s.strip()]
            
            if role.get("title"):
                roles.append(role)
        
        if roles:
            exp["roles"] = roles
            exp["is_grouped"] = True
            return exp
        
        return None
    
    def _extract_single_experience(self, item) -> Optional[Dict[str, str]]:
        """Extract details from a single experience item.
        
        Args:
            item: BeautifulSoup element containing experience data
            
        Returns:
            Dictionary with experience details or None
        """
        exp = {}
        
        # Job Title - try multiple selectors (updated 2024)
        title_selectors = [
            'div.display-flex.align-items-center span[aria-hidden="true"]',
            'div.display-flex span[aria-hidden="true"]',  # Simplified
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
        
        # If not found, try finding the anchor div and get its parent section
        if not section:
            anchor = soup.select_one('div[id="education"]')
            if anchor and anchor.parent and anchor.parent.name == 'section':
                section = anchor.parent
        
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

    def _extract_skills(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract skills with endorsements and categories.
        
        Returns:
            List of dictionaries containing skill name and endorsement count
        """
        skills = []
        
        # Modern LinkedIn selectors for skills section
        section_selectors = [
            'section[id*="skills"]',
            'section[data-section="skills"]',
            'div#skills-section',
            'section.pv-profile-section.pv-skill-categories-section',
        ]
        
        section = None
        for selector in section_selectors:
            section = soup.select_one(selector)
            if section:
                break
        
        # If not found, try finding the anchor div and get its parent section
        if not section:
            anchor = soup.select_one('div[id="skills"]')
            if anchor and anchor.parent and anchor.parent.name == 'section':
                section = anchor.parent
        
        if not section:
            return skills
        
        # Try extracting skills with endorsements (detailed view)
        skill_items = section.select('div.pv-skill-category-entity, li.pvs-list__paged-list-item')
        
        if skill_items:
            for item in skill_items:
                skill_data = self._extract_single_skill(item)
                if skill_data and skill_data.get('name'):
                    skills.append(skill_data)
        else:
            # Fallback: Simple skill extraction
            skill_elements = section.find_all("div", {"class": re.compile(r".*skill.*")})
            for element in skill_elements:
                skill_name = element.get_text(strip=True)
                if skill_name and len(skill_name) < 100:  # Filter out noise
                    # Check if not already added
                    if not any(s.get('name') == skill_name for s in skills):
                        skills.append({'name': skill_name, 'endorsements': 0})
        
        # Remove duplicates by name while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            skill_name = skill.get('name', '').lower()
            if skill_name and skill_name not in seen:
                seen.add(skill_name)
                unique_skills.append(skill)
        
        return unique_skills
    
    def _extract_single_skill(self, item) -> Optional[Dict[str, Any]]:
        """Extract details from a single skill item.
        
        Args:
            item: BeautifulSoup element containing skill data
            
        Returns:
            Dictionary with skill name and endorsement count
        """
        skill = {}
        
        # Skill Name
        name_selectors = [
            'div.display-flex.align-items-center span[aria-hidden="true"]',
            'span.pv-skill-category-entity__name',
            'div.t-bold span',
            'p.pv-skill-category-entity__name',
        ]
        
        for selector in name_selectors:
            name = self._safe_extract(item, selector)
            if name and len(name) > 0 and len(name) < 100:
                skill['name'] = name
                break
        
        # Endorsement Count
        endorsement_selectors = [
            'span.t-14.t-black--light span[aria-hidden="true"]',
            'span.pv-skill-category-entity__endorsement-count',
            'button span.t-bold',
        ]
        
        for selector in endorsement_selectors:
            try:
                element = item.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    # Extract number from endorsement text
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        skill['endorsements'] = int(numbers[0])
                        break
            except Exception:
                continue
        
        # If no endorsements found, default to 0
        if 'endorsements' not in skill and 'name' in skill:
            skill['endorsements'] = 0
        
        return skill if skill else None

    def _extract_certifications(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract certifications with detailed information.
        
        Extracts:
        - Certificate name
        - Issuing organization
        - Issue date and expiry date
        - Credential ID
        - Credential URL
        """
        certifications = []
        
        # Modern LinkedIn selectors for certifications section
        section_selectors = [
            'section[id*="licenses"]',
            'section[id*="certifications"]',
            'section[data-section="certifications"]',
            'div#certifications-section',
        ]
        
        section = None
        for selector in section_selectors:
            section = soup.select_one(selector)
            if section:
                break
        
        # If not found, try finding the anchor div and get its parent section
        if not section:
            for anchor_id in ['licenses', 'certifications', 'licenses_and_certifications']:
                anchor = soup.select_one(f'div[id="{anchor_id}"]')
                if anchor and anchor.parent and anchor.parent.name == 'section':
                    section = anchor.parent
                    break
        
        if not section:
            return certifications
        
        # Find certification items
        item_selectors = [
            'li.pvs-list__paged-list-item',
            'li.artdeco-list__item',
            'li[class*="certification"]',
        ]
        
        items = []
        for selector in item_selectors:
            found_items = section.select(selector)
            if found_items:
                items = found_items
                break
        
        for item in items:
            cert_data = self._extract_single_certification(item)
            if cert_data and cert_data.get('name'):
                certifications.append(cert_data)
        
        return certifications
    
    def _extract_single_certification(self, item) -> Optional[Dict[str, str]]:
        """Extract details from a single certification item.
        
        Args:
            item: BeautifulSoup element containing certification data
            
        Returns:
            Dictionary with certification details
        """
        cert = {}
        
        # Certificate Name
        name_selectors = [
            'div.display-flex.align-items-center span[aria-hidden="true"]',
            'h3 span[aria-hidden="true"]',
            'div.t-bold span',
            'div.pv-certifications__summary-info h3',
        ]
        
        for selector in name_selectors:
            name = self._safe_extract(item, selector)
            if name and len(name) > 0:
                cert['name'] = name
                break
        
        # Issuing Organization
        issuer_selectors = [
            'span.t-14.t-normal span[aria-hidden="true"]',
            'div.pv-certifications__summary-info p',
            'span[class*="issuer"]',
        ]
        
        for selector in issuer_selectors:
            issuer = self._safe_extract(item, selector)
            if issuer and len(issuer) > 0 and issuer != cert.get('name'):
                cert['issuer'] = issuer
                break
        
        # Date (Issue and Expiry)
        date_selectors = [
            'span.t-14.t-normal.t-black--light span[aria-hidden="true"]',
            'div.pv-certifications__summary-info span.t-14',
            'span[class*="date"]',
        ]
        
        for selector in date_selectors:
            date = self._safe_extract(item, selector)
            if date and len(date) > 0:
                cert['date'] = date
                break
        
        # Credential ID
        credential_selectors = [
            'div[class*="credential"] span[aria-hidden="true"]',
            'span[class*="credential-id"]',
        ]
        
        for selector in credential_selectors:
            credential = self._safe_extract(item, selector)
            if credential and 'credential' in credential.lower():
                # Extract just the ID part
                parts = credential.split(':', 1)
                if len(parts) > 1:
                    cert['credential_id'] = parts[1].strip()
                else:
                    cert['credential_id'] = credential
                break
        
        # Credential URL
        url_selectors = [
            'a[href*="credential"]',
            'a[class*="certification-url"]',
        ]
        
        for selector in url_selectors:
            try:
                link = item.select_one(selector)
                if link and link.get('href'):
                    cert['url'] = link['href']
                    break
            except Exception:
                continue
        
        return cert if cert else None

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
                    languages.append({'name': lang_name, 'proficiency': 'Professional working proficiency'})
        
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

    def _extract_volunteer(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract volunteer experience with comprehensive details.
        
        Extracts:
        - Role/position
        - Organization
        - Duration
        - Cause (e.g., Education, Environment)
        - Description
        """
        volunteer = []
        
        # Modern LinkedIn selectors for volunteer section
        section_selectors = [
            'section[id*="volunteer"]',
            'section[data-section="volunteering"]',
            'div#volunteering-section',
        ]
        
        section = None
        for selector in section_selectors:
            section = soup.select_one(selector)
            if section:
                break
        
        if not section:
            return volunteer
        
        # Find volunteer items
        item_selectors = [
            'li.pvs-list__paged-list-item',
            'li.artdeco-list__item',
            'li[class*="volunteer"]',
        ]
        
        items = []
        for selector in item_selectors:
            found_items = section.select(selector)
            if found_items:
                items = found_items
                break
        
        for item in items:
            vol_data = self._extract_single_volunteer(item)
            if vol_data and (vol_data.get('role') or vol_data.get('organization')):
                volunteer.append(vol_data)
        
        return volunteer
    
    def _extract_single_volunteer(self, item) -> Optional[Dict[str, str]]:
        """Extract details from a single volunteer item.
        
        Args:
            item: BeautifulSoup element containing volunteer data
            
        Returns:
            Dictionary with volunteer details
        """
        vol = {}
        
        # Role/Position
        role_selectors = [
            'div.display-flex.align-items-center span[aria-hidden="true"]',
            'h3 span[aria-hidden="true"]',
            'div.t-bold span',
        ]
        
        for selector in role_selectors:
            role = self._safe_extract(item, selector)
            if role and len(role) > 0:
                vol['role'] = role
                break
        
        # Organization
        org_selectors = [
            'span.t-14.t-normal span[aria-hidden="true"]',
            'div[class*="organization"]',
        ]
        
        for selector in org_selectors:
            org = self._safe_extract(item, selector)
            if org and len(org) > 0 and org != vol.get('role'):
                vol['organization'] = org
                break
        
        # Duration
        duration_selectors = [
            'span.t-14.t-normal.t-black--light span[aria-hidden="true"]',
            'span[class*="date-range"]',
        ]
        
        for selector in duration_selectors:
            duration = self._safe_extract(item, selector)
            if duration and len(duration) > 0:
                vol['duration'] = duration
                break
        
        # Cause (e.g., Education, Environment)
        cause_selectors = [
            'span[class*="cause"]',
            'div[class*="cause"] span[aria-hidden="true"]',
        ]
        
        for selector in cause_selectors:
            cause = self._safe_extract(item, selector)
            if cause and 'cause' in cause.lower():
                vol['cause'] = cause.replace('Cause:', '').strip()
                break
        
        # Description
        desc_selectors = [
            'div.pv-shared-text-with-see-more span[aria-hidden="true"]',
            'div.inline-show-more-text span[aria-hidden="true"]',
        ]
        
        for selector in desc_selectors:
            try:
                element = item.select_one(selector)
                if element:
                    desc = element.get_text(separator='\n', strip=True)
                    if desc and len(desc) > 10:
                        vol['description'] = desc
                        break
            except Exception:
                continue
        
        return vol if vol else None

    def _extract_projects(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract projects with enhanced details."""
        projects = []
        section_selectors = [
            'section[id*="projects"]',
            'section[data-section="projects"]',
        ]
        
        section = None
        for selector in section_selectors:
            section = soup.select_one(selector)
            if section:
                break
        
        if not section:
            return projects
        
        items = section.select('li.pvs-list__paged-list-item, li.artdeco-list__item, li')
        for item in items:
            # Name
            name = self._safe_extract(item, 'div.display-flex span[aria-hidden="true"]') or \
                   self._safe_extract(item, 'h3 span[aria-hidden="true"]') or \
                   self._safe_extract(item, 'div.t-bold')
            
            if name:
                proj = {'name': name}
                
                # Description with full text
                desc_elem = item.select_one('div.pv-shared-text-with-see-more span[aria-hidden="true"]') or \
                           item.select_one('div.inline-show-more-text')
                if desc_elem:
                    proj['description'] = desc_elem.get_text(separator='\n', strip=True)
                
                # Date
                date = self._safe_extract(item, 'span.t-14.t-normal.t-black--light span[aria-hidden="true"]') or \
                       self._safe_extract(item, 'span.t-14.t-normal.t-black--light')
                if date:
                    proj['date'] = date
                
                # URL
                link = item.select_one('a[href]')
                if link and link.get('href') and 'http' in link.get('href', ''):
                    proj['url'] = link['href']
                
                projects.append(proj)
        
        return projects

    def _extract_publications(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract publications with enhanced details."""
        publications = []
        section_selectors = [
            'section[id*="publications"]',
            'section[data-section="publications"]',
        ]
        
        section = None
        for selector in section_selectors:
            section = soup.select_one(selector)
            if section:
                break
        
        if not section:
            return publications
        
        items = section.select('li.pvs-list__paged-list-item, li.artdeco-list__item, li')
        for item in items:
            # Title
            title = self._safe_extract(item, 'div.display-flex span[aria-hidden="true"]') or \
                   self._safe_extract(item, 'h3 span[aria-hidden="true"]') or \
                   self._safe_extract(item, 'div.t-bold')
            
            if title:
                pub = {'title': title}
                
                # Publisher
                publisher = self._safe_extract(item, 'span.t-14.t-normal span[aria-hidden="true"]') or \
                           self._safe_extract(item, 'span.t-14.t-normal')
                if publisher and publisher != title:
                    pub['publisher'] = publisher
                
                # Date
                date = self._safe_extract(item, 'span.t-14.t-normal.t-black--light span[aria-hidden="true"]') or \
                       self._safe_extract(item, 'span.t-14.t-normal.t-black--light')
                if date:
                    pub['date'] = date
                
                # Description
                desc_elem = item.select_one('div.pv-shared-text-with-see-more span[aria-hidden="true"]')
                if desc_elem:
                    pub['description'] = desc_elem.get_text(separator='\n', strip=True)
                
                publications.append(pub)
        
        return publications

    def _extract_honors(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract honors and awards with enhanced details."""
        honors = []
        section_selectors = [
            'section[id*="honors"]',
            'section[id*="awards"]',
            'section[data-section="honors"]',
        ]
        
        section = None
        for selector in section_selectors:
            section = soup.select_one(selector)
            if section:
                break
        
        if not section:
            return honors
        
        items = section.select('li.pvs-list__paged-list-item, li.artdeco-list__item, li')
        for item in items:
            # Title
            title = self._safe_extract(item, 'div.display-flex span[aria-hidden="true"]') or \
                   self._safe_extract(item, 'h3 span[aria-hidden="true"]') or \
                   self._safe_extract(item, 'div.t-bold')
            
            if title:
                honor = {'title': title}
                
                # Issuer
                issuer = self._safe_extract(item, 'span.t-14.t-normal span[aria-hidden="true"]') or \
                        self._safe_extract(item, 'span.t-14.t-normal')
                if issuer and issuer != title:
                    honor['issuer'] = issuer
                
                # Date
                date = self._safe_extract(item, 'span.t-14.t-normal.t-black--light span[aria-hidden="true"]') or \
                       self._safe_extract(item, 'span.t-14.t-normal.t-black--light')
                if date:
                    honor['date'] = date
                
                # Description
                desc_elem = item.select_one('div.pv-shared-text-with-see-more span[aria-hidden="true"]')
                if desc_elem:
                    honor['description'] = desc_elem.get_text(separator='\n', strip=True)
                
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
