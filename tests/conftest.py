"""Pytest configuration and fixtures for LinkedIn CV Generator tests."""
import pytest
from pathlib import Path


@pytest.fixture
def sample_profile_html():
    """Sample LinkedIn profile HTML for testing."""
    return """
    <html>
        <head><title>John Doe | LinkedIn</title></head>
        <body>
            <main class="scaffold-layout__main">
                <section>
                    <h1 class="text-heading-xlarge inline t-24">
                        <span aria-hidden="true">John Doe</span>
                    </h1>
                    <div class="text-body-medium break-words">
                        <span>Senior Software Engineer</span>
                    </div>
                    <span class="text-body-small inline t-black--light break-words">
                        San Francisco, California
                    </span>
                </section>
                
                <section id="about">
                    <div class="pv-shared-text-with-see-more">
                        <span aria-hidden="true">
                            Experienced software engineer with 10+ years in web development.
                        </span>
                    </div>
                </section>
            </main>
        </body>
    </html>
    """


@pytest.fixture
def sample_experience_html():
    """Sample experience section HTML for testing."""
    return """
    <html>
        <body>
            <main class="scaffold-layout__main">
                <ul class="pvs-list">
                    <li class="pvs-list__paged-list-item">
                        <div class="display-flex align-items-center">
                            <span aria-hidden="true">Senior Software Engineer</span>
                        </div>
                        <span class="t-14 t-normal">
                            <span aria-hidden="true">Acme Corp</span>
                        </span>
                        <span class="t-14 t-normal t-black--light">
                            <span aria-hidden="true">Jan 2020 - Present · 4 yrs</span>
                        </span>
                        <div class="pv-shared-text-with-see-more">
                            <span aria-hidden="true">
                                Leading development of microservices architecture.
                            </span>
                        </div>
                    </li>
                </ul>
            </main>
        </body>
    </html>
    """


@pytest.fixture
def sample_education_html():
    """Sample education section HTML for testing."""
    return """
    <html>
        <body>
            <main class="scaffold-layout__main">
                <ul class="pvs-list">
                    <li class="pvs-list__paged-list-item">
                        <div class="display-flex align-items-center">
                            <span aria-hidden="true">Stanford University</span>
                        </div>
                        <span class="t-14 t-normal">
                            <span aria-hidden="true">Bachelor of Science - BS, Computer Science</span>
                        </span>
                        <span class="t-14 t-normal t-black--light">
                            <span aria-hidden="true">2010 - 2014</span>
                        </span>
                    </li>
                </ul>
            </main>
        </body>
    </html>
    """


@pytest.fixture
def sample_skills_html():
    """Sample skills section HTML for testing."""
    return """
    <html>
        <body>
            <main class="scaffold-layout__main">
                <ul class="pvs-list">
                    <li class="pvs-list__paged-list-item">
                        <div class="display-flex align-items-center">
                            <span aria-hidden="true">Python</span>
                        </div>
                        <span class="t-14 t-black--light">
                            <span aria-hidden="true">45 endorsements</span>
                        </span>
                    </li>
                    <li class="pvs-list__paged-list-item">
                        <div class="display-flex align-items-center">
                            <span aria-hidden="true">JavaScript</span>
                        </div>
                        <span class="t-14 t-black--light">
                            <span aria-hidden="true">32 endorsements</span>
                        </span>
                    </li>
                </ul>
            </main>
        </body>
    </html>
    """


@pytest.fixture
def sample_certifications_html():
    """Sample certifications section HTML for testing."""
    return """
    <html>
        <body>
            <main class="scaffold-layout__main">
                <ul class="pvs-list">
                    <li class="pvs-list__paged-list-item">
                        <div class="display-flex align-items-center">
                            <span aria-hidden="true">AWS Certified Solutions Architect</span>
                        </div>
                        <span class="t-14 t-normal">
                            <span aria-hidden="true">Amazon Web Services</span>
                        </span>
                        <span class="t-14 t-normal t-black--light">
                            <span aria-hidden="true">Issued Jan 2024</span>
                        </span>
                    </li>
                </ul>
            </main>
        </body>
    </html>
    """


@pytest.fixture
def sample_profile_data():
    """Sample profile data dictionary for testing."""
    return {
        'username': 'john-doe',
        'name': 'John Doe',
        'headline': 'Senior Software Engineer',
        'location': 'San Francisco, California',
        'about': 'Experienced software engineer with 10+ years in web development.',
        'experience': [
            {
                'title': 'Senior Software Engineer',
                'company': 'Acme Corp',
                'duration': 'Jan 2020 - Present',
                'location': 'San Francisco, CA',
                'description': 'Leading development of microservices architecture.'
            }
        ],
        'education': [
            {
                'institution': 'Stanford University',
                'degree': 'Bachelor of Science',
                'field': 'Computer Science',
                'duration': '2010 - 2014'
            }
        ],
        'skills': [
            {'name': 'Python', 'endorsements': 45},
            {'name': 'JavaScript', 'endorsements': 32}
        ],
        'certifications': [],
        'languages': [],
        'volunteer': [],
        'projects': [],
        'publications': [],
        'honors': [],
        'courses': []
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for testing."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
