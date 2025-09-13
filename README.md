# Disney Audiobook Reader

A complete toolkit for Disney NFC audiobook figures, including SD card extraction tools and a web-based NFC reader.

🌐 **Live Demo:** [https://pho3nixhun.github.io/disney-audibook-reader](https://pho3nixhun.github.io/disney-audibook-reader)

## 🏰 What This Project Does

This project provides tools to:

1. **Extract audio files** from Disney audiobook SD card images
2. **Read NFC tags** from Disney figures using your phone
3. **Analyze metadata** and understand the audiobook collection

## 📱 NFC Reader Web App

The main feature is a React web application that reads NFC tags from Disney figures using your Android phone.

### Features
- 🔍 Real-time NFC tag scanning
- 📊 Raw tag data display in hex format
- 🏰 Disney-themed mobile-optimized UI
- 💾 Tag history (last 10 scans)
- 🔒 HTTPS enabled for NFC functionality

### Usage
1. Visit [the live app](https://pho3nixhun.github.io/disney-audibook-reader) on Android Chrome
2. Enable NFC in your phone settings
3. Tap "Start NFC Scanning"
4. Hold Disney figures near your phone's NFC area
5. View the raw data stored on each figure

### Requirements
- Android device with NFC capability
- Chrome browser (Web NFC API support)
- HTTPS connection (automatically provided by GitHub Pages)

## 🛠️ Audio Extraction Tools

Located in the [`bin/`](bin/) directory, these Python scripts extract audiobooks from SD card images.

### Quick Start
```bash
# 1. Place your SD card image as disney.img
# 2. Extract all audio files
python3 bin/extract_audio.py

# 3. Generate metadata report
python3 bin/final_metadata_extractor.py
```

### What You Get
- **80 Disney audiobook MP3 files** (7-11 MB each)
- **Complete metadata analysis** in JSON format
- **Story identification** based on filename patterns

### Stories Included
The Disney audiobook collection includes:
- **Classic tales:** Aladdin, Snow White, Lion King
- **Modern stories:** Frozen, Moana, Tangled
- **Pixar films:** Toy Story, Finding Nemo, The Incredibles
- **And many more...**

## 🚀 Development

### Run Locally
```bash
npm install
npm start
```

### Deploy
Push to the `main` branch and GitHub Actions automatically deploys to GitHub Pages.

## 📁 Project Structure

```
disney-audibook-reader/
├── src/                    # React NFC reader app
├── public/                 # Web app assets
├── bin/                    # Audio extraction scripts
│   ├── README.md          # Detailed script documentation
│   ├── extract_audio.py   # Main extraction script
│   └── ...                # Other utilities
├── .github/workflows/     # GitHub Actions deployment
└── package.json           # React app configuration
```

## 🔍 Technical Details

### Disney Audiobook System
- **Hardware:** NFC reader box with speaker
- **Storage:** SD card with FAT16 filesystem
- **Audio:** 80 MP3 files, ~650MB total
- **NFC Tags:** Store simple identifiers linking to specific audio files

### NFC Technology
- Uses Web NFC API (Chrome Android only)
- Reads NDEF (NFC Data Exchange Format) records
- Displays both text content and raw hexadecimal data
- Works with various NFC tag types

### File System
- SD card uses FAT16 with standard partition table
- Filenames truncated to 8.3 format
- Minimal ID3 metadata (genre: "Blues" only)
- Custom extraction preserves full audio quality

## 🤝 Contributing

Feel free to:
- Report issues with NFC reading
- Add support for other Disney audiobook systems
- Improve the extraction scripts
- Enhance the web UI

## 📋 License

This project is for educational and personal use. Disney content remains property of The Walt Disney Company.

---

**Note:** This project was created to understand and preserve Disney audiobook content for personal use. All extracted audio remains under Disney's copyright.