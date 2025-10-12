# Output Directory Structure

## Overview

All generated files are organized in user-specific directories under the `output/` folder.

## Directory Structure

```
output/
└── <linkedin-username>/
    ├── profile_data.json     # Complete profile data export
    └── cv_YYYYMMDD_HHMMSS.pdf  # Generated CV with timestamp
```

## Examples

For a LinkedIn profile URL: `https://www.linkedin.com/in/alex-colls-outumuro/`

The output structure will be:
```
output/
└── alex-colls-outumuro/
    ├── profile_data.json
    ├── cv_20241012_141530.pdf
    ├── cv_20241015_093021.pdf  # Multiple CVs with different timestamps
    └── cv_20241020_162145.pdf
```

## File Naming Conventions

### JSON Export
- **Location**: `output/<username>/profile_data.json`
- **Name**: Always `profile_data.json` (overwrites on each export)
- **Content**: Complete LinkedIn profile data in JSON format

### PDF CVs
- **Location**: `output/<username>/cv_<timestamp>.pdf`
- **Format**: `cv_YYYYMMDD_HHMMSS.pdf`
- **Example**: `cv_20241012_141530.pdf`
- **Note**: Each generation creates a new PDF with unique timestamp

## Username Extraction

The username is automatically extracted from:
1. LinkedIn URL: `https://www.linkedin.com/in/username/` → `username`
2. Direct username input: `john-doe` → `john-doe`
3. Profile data if available
4. Fallback: `linkedin-profile` (if extraction fails)

## Benefits

1. **Organization**: Each LinkedIn profile has its own directory
2. **History**: Multiple CV versions are preserved with timestamps
3. **Clean**: No file conflicts between different profiles
4. **Easy Access**: Find all files for a user in one place

## Usage Examples

### Export to JSON
```bash
# Via menu
./run.sh
# Select option 2: Export Profile to JSON
# Enter: alex-colls-outumuro
# Output: output/alex-colls-outumuro/profile_data.json

# Via CLI
./run.sh alex-colls-outumuro --json
```

### Generate PDF CV
```bash
# Via menu
./run.sh
# Select option 1: Generate CV
# Enter: alex-colls-outumuro
# Output: output/alex-colls-outumuro/cv_20241012_141530.pdf

# Via CLI
./run.sh alex-colls-outumuro
```

## Accessing Files

### View JSON data
```bash
# Pretty print with jq
jq . output/alex-colls-outumuro/profile_data.json

# Quick view
cat output/alex-colls-outumuro/profile_data.json
```

### List all CVs for a user
```bash
ls -la output/alex-colls-outumuro/*.pdf
```

### Find latest CV
```bash
ls -t output/alex-colls-outumuro/cv_*.pdf | head -1
```

## Notes

- The `profile_data.json` is overwritten on each export
- PDF files are never overwritten (unique timestamps)
- Directories are created automatically
- No cleanup needed - files are organized by user