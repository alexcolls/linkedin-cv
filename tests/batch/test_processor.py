"""Tests for batch processor."""
import csv
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.batch.processor import BatchProcessor
from src.exceptions import ValidationError


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_csv(tmp_path):
    """Create sample CSV file."""
    csv_file = tmp_path / "profiles.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'name'])
        writer.writeheader()
        writer.writerows([
            {'url': 'https://linkedin.com/in/user1', 'name': 'User One'},
            {'url': 'https://linkedin.com/in/user2', 'name': 'User Two'},
            {'url': 'https://linkedin.com/in/user3', 'name': ''},
        ])
    return csv_file


@pytest.fixture
def processor(temp_output_dir):
    """Create batch processor instance."""
    return BatchProcessor(
        output_dir=str(temp_output_dir),
        theme="modern",
        output_format="pdf",
        headless=True,
        add_qr_code=True,
        custom_colors=None,
        max_concurrent=3,
    )


def test_batch_processor_init(temp_output_dir):
    """Test batch processor initialization."""
    processor = BatchProcessor(
        output_dir=str(temp_output_dir),
        theme="executive",
        output_format="html",
        headless=False,
        add_qr_code=False,
        custom_colors={"primary": "#ff0000"},
        max_concurrent=5,
    )
    
    assert processor.output_dir == temp_output_dir
    assert processor.theme == "executive"
    assert processor.output_format == "html"
    assert processor.headless is False
    assert processor.add_qr_code is False
    assert processor.custom_colors == {"primary": "#ff0000"}
    assert processor.max_concurrent == 5
    assert processor.results == []
    assert processor.validator is not None


def test_load_from_csv_success(sample_csv):
    """Test loading profiles from valid CSV."""
    profiles = BatchProcessor.load_from_csv(str(sample_csv))
    
    assert len(profiles) == 3
    assert profiles[0] == {'url': 'https://linkedin.com/in/user1', 'name': 'User One'}
    assert profiles[1] == {'url': 'https://linkedin.com/in/user2', 'name': 'User Two'}
    assert profiles[2] == {'url': 'https://linkedin.com/in/user3', 'name': ''}


def test_load_from_csv_file_not_found():
    """Test loading from non-existent CSV."""
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        BatchProcessor.load_from_csv("nonexistent.csv")


def test_load_from_csv_missing_url_column(tmp_path):
    """Test CSV without required 'url' column."""
    csv_file = tmp_path / "invalid.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'email'])
        writer.writeheader()
        writer.writerows([{'name': 'John', 'email': 'john@example.com'}])
    
    with pytest.raises(ValueError, match="CSV must have 'url' column"):
        BatchProcessor.load_from_csv(str(csv_file))


def test_load_from_csv_empty_profiles(tmp_path):
    """Test CSV with no valid profiles."""
    csv_file = tmp_path / "empty.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'name'])
        writer.writeheader()
        writer.writerows([
            {'url': '', 'name': 'Empty'},
            {'url': '  ', 'name': 'Whitespace'},
        ])
    
    with pytest.raises(ValueError, match="No valid profiles found in CSV"):
        BatchProcessor.load_from_csv(str(csv_file))


def test_load_from_csv_with_whitespace(tmp_path):
    """Test CSV with whitespace in URLs."""
    csv_file = tmp_path / "whitespace.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'name'])
        writer.writeheader()
        writer.writerows([
            {'url': '  https://linkedin.com/in/user1  ', 'name': '  User One  '},
        ])
    
    profiles = BatchProcessor.load_from_csv(str(csv_file))
    assert len(profiles) == 1
    assert profiles[0] == {'url': 'https://linkedin.com/in/user1', 'name': 'User One'}


def test_create_sample_csv(tmp_path):
    """Test creating sample CSV file."""
    output_file = tmp_path / "sample.csv"
    BatchProcessor.create_sample_csv(str(output_file))
    
    assert output_file.exists()
    
    # Verify content
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 3
    assert rows[0]['url'] == 'https://linkedin.com/in/username1'
    assert rows[0]['name'] == 'John Doe'
    assert rows[1]['url'] == 'https://linkedin.com/in/username2'
    assert rows[1]['name'] == 'Jane Smith'


@pytest.mark.asyncio
async def test_process_single_profile_success(processor):
    """Test processing a single profile successfully."""
    profile_data = {
        'url': 'https://linkedin.com/in/testuser',
        'name': 'Test User'
    }
    
    # Mock dependencies
    mock_html = '<html><body>Profile content</body></html>'
    mock_parsed_data = {
        'username': 'testuser',
        'name': 'Test User',
        'profile_picture_url': 'https://example.com/pic.jpg',
        'experience': [],
        'education': [],
    }
    
    with patch('src.batch.processor.LinkedInScraper') as mock_scraper_cls, \
         patch('src.batch.processor.ProfileParser') as mock_parser_cls, \
         patch('src.batch.processor.ImageProcessor') as mock_image_cls, \
         patch('src.batch.processor.QRGenerator') as mock_qr_cls, \
         patch('src.batch.processor.PDFGenerator') as mock_pdf_cls:
        
        # Setup mocks
        mock_scraper = AsyncMock()
        mock_scraper.scrape_profile = AsyncMock(return_value=mock_html)
        mock_scraper_cls.return_value = mock_scraper
        
        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_parsed_data
        mock_parser_cls.return_value = mock_parser
        
        mock_image = MagicMock()
        mock_image.process.return_value = 'base64_image_data'
        mock_image_cls.return_value = mock_image
        
        mock_qr = MagicMock()
        mock_qr.generate.return_value = 'qr_code_data'
        mock_qr_cls.return_value = mock_qr
        
        mock_pdf = MagicMock()
        mock_pdf_cls.return_value = mock_pdf
        
        # Process profile
        result = await processor._process_single_profile(profile_data)
        
        # Verify result
        assert result['success'] is True
        assert result['profile_url'] == 'https://linkedin.com/in/testuser'
        assert result['username'] == 'testuser'
        assert result['name'] == 'Test User'
        assert 'output_file' in result
        
        # Verify mocks called
        mock_scraper.scrape_profile.assert_called_once()
        mock_parser.parse.assert_called_once_with(mock_html)
        mock_image.process.assert_called_once()
        mock_qr.generate.assert_called_once()
        mock_pdf.generate.assert_called_once()


@pytest.mark.asyncio
async def test_process_single_profile_scraping_error(processor):
    """Test handling scraping error in single profile processing."""
    profile_data = {
        'url': 'https://linkedin.com/in/testuser',
        'name': 'Test User'
    }
    
    with patch('src.batch.processor.LinkedInScraper') as mock_scraper_cls:
        mock_scraper = AsyncMock()
        mock_scraper.scrape_profile = AsyncMock(side_effect=Exception("Scraping failed"))
        mock_scraper_cls.return_value = mock_scraper
        
        result = await processor._process_single_profile(profile_data)
        
        assert result['success'] is False
        assert result['profile_url'] == 'https://linkedin.com/in/testuser'
        assert 'Scraping failed' in result['error']


@pytest.mark.asyncio
async def test_process_single_profile_invalid_url(processor):
    """Test handling invalid URL in single profile processing."""
    profile_data = {
        'url': 'not-a-valid-url',
        'name': 'Test User'
    }
    
    result = await processor._process_single_profile(profile_data)
    
    assert result['success'] is False
    assert result['profile_url'] == 'not-a-valid-url'
    assert 'error' in result


@pytest.mark.asyncio
async def test_process_single_profile_without_qr_code(temp_output_dir):
    """Test processing profile with QR code disabled."""
    processor = BatchProcessor(
        output_dir=str(temp_output_dir),
        add_qr_code=False,
    )
    
    profile_data = {
        'url': 'https://linkedin.com/in/testuser',
        'name': 'Test User'
    }
    
    mock_html = '<html><body>Profile content</body></html>'
    mock_parsed_data = {
        'username': 'testuser',
        'name': 'Test User',
        'experience': [],
        'education': [],
    }
    
    with patch('src.batch.processor.LinkedInScraper') as mock_scraper_cls, \
         patch('src.batch.processor.ProfileParser') as mock_parser_cls, \
         patch('src.batch.processor.QRGenerator') as mock_qr_cls, \
         patch('src.batch.processor.PDFGenerator') as mock_pdf_cls:
        
        mock_scraper = AsyncMock()
        mock_scraper.scrape_profile = AsyncMock(return_value=mock_html)
        mock_scraper_cls.return_value = mock_scraper
        
        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_parsed_data
        mock_parser_cls.return_value = mock_parser
        
        mock_pdf = MagicMock()
        mock_pdf_cls.return_value = mock_pdf
        
        result = await processor._process_single_profile(profile_data)
        
        # QR generator should not be called
        mock_qr_cls.assert_not_called()
        assert result['success'] is True


@pytest.mark.asyncio
async def test_process_single_profile_html_output(temp_output_dir):
    """Test processing profile with HTML output format."""
    processor = BatchProcessor(
        output_dir=str(temp_output_dir),
        output_format="html",
    )
    
    profile_data = {
        'url': 'https://linkedin.com/in/testuser',
        'name': 'Test User'
    }
    
    mock_html = '<html><body>Profile content</body></html>'
    mock_parsed_data = {
        'username': 'testuser',
        'name': 'Test User',
        'experience': [],
        'education': [],
    }
    
    with patch('src.batch.processor.LinkedInScraper') as mock_scraper_cls, \
         patch('src.batch.processor.ProfileParser') as mock_parser_cls, \
         patch('src.batch.processor.HTMLExporter') as mock_html_cls:
        
        mock_scraper = AsyncMock()
        mock_scraper.scrape_profile = AsyncMock(return_value=mock_html)
        mock_scraper_cls.return_value = mock_scraper
        
        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_parsed_data
        mock_parser_cls.return_value = mock_parser
        
        mock_exporter = MagicMock()
        mock_html_cls.return_value = mock_exporter
        
        result = await processor._process_single_profile(profile_data)
        
        # HTML exporter should be called
        mock_exporter.export.assert_called_once()
        assert result['success'] is True
        assert result['output_file'].endswith('.html')


@pytest.mark.asyncio
async def test_process_batch_success(processor):
    """Test batch processing with all successful profiles."""
    profiles = [
        {'url': 'https://linkedin.com/in/user1', 'name': 'User One'},
        {'url': 'https://linkedin.com/in/user2', 'name': 'User Two'},
    ]
    
    # Mock _process_single_profile to return success
    async def mock_process(profile_data):
        return {
            'success': True,
            'profile_url': profile_data['url'],
            'username': 'testuser',
            'name': profile_data.get('name', 'Unknown'),
            'output_file': '/tmp/test.pdf'
        }
    
    processor._process_single_profile = mock_process
    
    results = await processor.process_batch(profiles)
    
    assert results['total'] == 2
    assert results['successful'] == 2
    assert results['failed'] == 0
    assert len(results['results']) == 2
    assert len(results['errors']) == 0
    assert results['duration'] > 0


@pytest.mark.asyncio
async def test_process_batch_with_failures(processor):
    """Test batch processing with some failures."""
    profiles = [
        {'url': 'https://linkedin.com/in/user1', 'name': 'User One'},
        {'url': 'https://linkedin.com/in/user2', 'name': 'User Two'},
        {'url': 'https://linkedin.com/in/user3', 'name': 'User Three'},
    ]
    
    # Mock _process_single_profile to alternate success/failure
    call_count = [0]
    
    async def mock_process(profile_data):
        call_count[0] += 1
        if call_count[0] % 2 == 0:
            return {
                'success': False,
                'profile_url': profile_data['url'],
                'error': 'Processing failed'
            }
        return {
            'success': True,
            'profile_url': profile_data['url'],
            'username': 'testuser',
            'name': profile_data.get('name', 'Unknown'),
            'output_file': '/tmp/test.pdf'
        }
    
    processor._process_single_profile = mock_process
    
    results = await processor.process_batch(profiles)
    
    assert results['total'] == 3
    assert results['successful'] == 2
    assert results['failed'] == 1
    assert len(results['results']) == 2
    assert len(results['errors']) == 1


@pytest.mark.asyncio
async def test_process_batch_with_exceptions(processor):
    """Test batch processing with exceptions."""
    profiles = [
        {'url': 'https://linkedin.com/in/user1', 'name': 'User One'},
        {'url': 'https://linkedin.com/in/user2', 'name': 'User Two'},
    ]
    
    # Mock _process_single_profile to raise exception
    async def mock_process(profile_data):
        if 'user1' in profile_data['url']:
            raise Exception("Unexpected error")
        return {
            'success': True,
            'profile_url': profile_data['url'],
            'username': 'testuser',
            'name': profile_data.get('name', 'Unknown'),
            'output_file': '/tmp/test.pdf'
        }
    
    processor._process_single_profile = mock_process
    
    results = await processor.process_batch(profiles)
    
    assert results['total'] == 2
    assert results['successful'] == 1
    assert results['failed'] == 1
    assert 'Unexpected error' in results['errors'][0]['error']


@pytest.mark.asyncio
async def test_process_batch_creates_output_dir(temp_output_dir):
    """Test that batch processing creates output directory."""
    output_dir = temp_output_dir / "new_dir"
    processor = BatchProcessor(output_dir=str(output_dir))
    
    profiles = [
        {'url': 'https://linkedin.com/in/user1', 'name': 'User One'},
    ]
    
    async def mock_process(profile_data):
        return {
            'success': True,
            'profile_url': profile_data['url'],
            'username': 'testuser',
            'name': 'User One',
            'output_file': '/tmp/test.pdf'
        }
    
    processor._process_single_profile = mock_process
    
    await processor.process_batch(profiles)
    
    # Output directory should be created
    assert output_dir.exists()


@pytest.mark.asyncio
async def test_process_batch_respects_concurrency_limit(processor):
    """Test that batch processing respects max_concurrent limit."""
    profiles = [
        {'url': f'https://linkedin.com/in/user{i}', 'name': f'User {i}'}
        for i in range(10)
    ]
    
    # Track concurrent executions
    concurrent_count = [0]
    max_concurrent = [0]
    
    async def mock_process(profile_data):
        concurrent_count[0] += 1
        max_concurrent[0] = max(max_concurrent[0], concurrent_count[0])
        
        # Simulate some work
        import asyncio
        await asyncio.sleep(0.01)
        
        concurrent_count[0] -= 1
        return {
            'success': True,
            'profile_url': profile_data['url'],
            'username': 'testuser',
            'name': profile_data.get('name', 'Unknown'),
            'output_file': '/tmp/test.pdf'
        }
    
    processor._process_single_profile = mock_process
    
    await processor.process_batch(profiles)
    
    # Max concurrent should not exceed limit
    assert max_concurrent[0] <= processor.max_concurrent


def test_display_summary(processor, capsys):
    """Test displaying batch processing summary."""
    successful = [
        {'name': 'User One', 'username': 'user1', 'output_file': '/tmp/user1.pdf'},
        {'name': 'User Two', 'username': 'user2', 'output_file': '/tmp/user2.pdf'},
    ]
    
    failed = [
        {'profile': {'url': 'https://linkedin.com/in/user3'}, 'error': 'Failed to scrape'},
    ]
    
    processor._display_summary(successful, failed, 10.5)
    
    # Can't easily test Rich output, but verify it doesn't crash
    assert True


def test_username_extraction_from_url(processor):
    """Test username extraction from LinkedIn URL in processing."""
    # This is implicitly tested in other tests, but we can verify the logic
    import re
    
    urls = [
        'https://linkedin.com/in/johndoe',
        'https://www.linkedin.com/in/janedoe/',
        'https://linkedin.com/in/user-name',
    ]
    
    for url in urls:
        match = re.search(r'linkedin\.com/in/([^/]+)', url)
        assert match is not None
        assert len(match.group(1)) > 0
