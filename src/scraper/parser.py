"""LinkedIn profile HTML parser."""
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup


class ProfileParser:
    """Parses LinkedIn profile HTML to extract structured data."""

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
        """Extract profile name."""
        # Try multiple selectors
        selectors = [
            "h1.text-heading-xlarge",
            "h1.top-card-layout__title",
            "[data-generated-suggestion-target]",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None

    def _extract_headline(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract profile headline/title."""
        selectors = [
            "div.text-body-medium.break-words",
            "div.top-card-layout__headline",
            ".top-card__headline",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None

    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract location."""
        selectors = [
            "span.text-body-small.inline.t-black--light.break-words",
            "div.top-card__subline-item",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element and "location" in element.get_text().lower():
                return element.get_text(strip=True)
        return None

    def _extract_profile_picture(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract profile picture URL."""
        img = soup.find("img", {"class": re.compile(r".*profile.*photo.*")})
        if img and img.get("src"):
            return img["src"]
        return None

    def _extract_about(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract About/Summary section."""
        section = soup.find("section", {"id": re.compile(r".*about.*")})
        if section:
            content = section.find("div", {"class": re.compile(r".*display-flex.*")})
            if content:
                return content.get_text(strip=True)
        return None

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
