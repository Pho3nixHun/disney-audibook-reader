# Disney Audiobook Extraction Scripts

This directory contains Python scripts for extracting audio files and metadata from Disney NFC audiobook SD card images.

## Prerequisites

- Python 3.6+
- SD card image file (`.img` format)

## Scripts Overview

### `fat16_reader.py`
Core FAT16 filesystem reader library used by other scripts.

**Usage:** This is a library module imported by other scripts.

### `extract_audio.py`
Extracts all MP3 audio files from the Disney SD card image.

**Usage:**
```bash
python3 extract_audio.py
```

**Requirements:**
- `disney.img` file in the same directory
- Creates `partition1.img` (temporary partition file)
- Creates `extracted_audio/` directory with all MP3 files

**Output:**
- 80 MP3 files extracted to `extracted_audio/`
- Files are renamed from truncated FAT16 names
- Also displays contents of README.TXT from the image

### `final_metadata_extractor.py`
Extracts ID3 metadata from MP3 files and creates a complete JSON report.

**Usage:**
```bash
python3 final_metadata_extractor.py
```

**Requirements:**
- `partition1.img` file (created by `extract_audio.py`)
- MP3 files in `extracted_audio/` directory

**Output:**
- `complete_disney_metadata.json` with full file analysis
- Includes file sizes, ID3 tags, and filename-based title guesses

### `extract_metadata.py` *(Legacy)*
Basic metadata extraction using simple ID3 parsing.

**Usage:**
```bash
python3 extract_metadata.py
```

### `improved_metadata.py` *(Analysis Tool)*
Diagnostic tool for analyzing ID3v2 tag structure in sample files.

**Usage:**
```bash
python3 improved_metadata.py
```

## Typical Workflow

1. **Place your SD card image** as `disney.img` in the parent directory

2. **Extract audio files:**
   ```bash
   python3 bin/extract_audio.py
   ```

3. **Generate metadata report:**
   ```bash
   python3 bin/final_metadata_extractor.py
   ```

## File Structure After Extraction

```
disney/
├── disney.img                          # Original SD card image
├── partition1.img                      # Extracted FAT16 partition
├── extracted_audio/                    # 80 MP3 audiobook files
│   ├── _01-ALA.MP3                    # Aladdin
│   ├── _02-SNO.MP3                    # Snow White
│   └── ...
├── complete_disney_metadata.json      # Full metadata analysis
└── bin/                               # Extraction scripts
    ├── fat16_reader.py
    ├── extract_audio.py
    └── final_metadata_extractor.py
```

## Notes

- All scripts assume the SD card uses FAT16 filesystem
- The Disney audiobooks contain minimal ID3 metadata (only genre: "Blues")
- Filenames are truncated due to FAT16's 8.3 naming limitation
- Title guessing is based on filename patterns and Disney story knowledge

## Disney Stories Found

The extraction reveals 80 Disney audiobook stories including:
- Classic tales: Aladdin, Snow White, Lion King, etc.
- Modern stories: Frozen, Moana, Tangled, etc.
- Pixar films: Toy Story, Finding Nemo, The Incredibles, etc.

Each story is approximately 7-11 MB and contains full audiobook narration.