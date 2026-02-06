# Audiobook to Opus Converter

A Python tool that efficiently converts audiobooks to the [Opus format](https://opus-codec.org/), optimized for voice content. Achieves significant file size reduction while maintaining excellent audio quality, with automatic parallel processing using all CPU cores.

## Features

- ✅ **Fast** - Parallel processing using all CPU cores by default
- ✅ **High Compression** - Opus codec works well for voice content
- ✅ **Quality Preserved** - Maintains metadata, directory structure, and cover art
- ✅ **Smart** - Skips already converted files
- ✅ **Simple** - Single command with sensible defaults
- ✅ **Flexible** - Supports MP3, M4A, M4B, AAC, FLAC, WAV, OGG, WMA

## Quick Start

```bash
# Install dependencies
sudo apt install ffmpeg python3  # Ubuntu/Debian
# or: brew install ffmpeg python3  # macOS

# Convert audiobooks (uses all CPU cores)
python3 convert_audiobooks.py
```

Input files: `./original/` → Output files: `./opus/`

## Usage

### Basic Examples

```bash
# Convert with defaults (all CPU cores, 20k bitrate)
python3 convert_audiobooks.py

# Custom directories
python3 convert_audiobooks.py -s ~/Audiobooks -o ~/Audiobooks_Opus

# Specific number of workers
python3 convert_audiobooks.py -w 4

# High quality
python3 convert_audiobooks.py -b 24k

# Verbose output
python3 convert_audiobooks.py -v
```

### Options

```plain
-s, --source DIR       Source directory (default: ./original)
-o, --output DIR       Output directory (default: ./opus)
-b, --bitrate RATE     Bitrate: 15k, 20k, 24k, 32k (default: 20k)
-w, --workers NUM      Parallel workers (default: CPU count)
--no-skip              Re-convert existing files
-v, --verbose          Verbose output
--no-color             Disable colors
-h, --help             Show help
```

## Quality Settings

| Bitrate | Quality | Use Case |
| ------- | ------- | -------- |
| 15k | Good | Maximum compression |
| **20k** | Excellent | **Recommended** |
| 24k | Very High | Complex audio |
| 32k | Maximum | Archival quality |

## Technical Details

**Codec Settings:**

- Opus at 20 kbps VBR (Variable Bitrate)
- VOIP mode (optimized for speech)
- Compression level 10 (maximum quality)
- Preserves all metadata and cover art

**Supported Formats:**

- Input: MP3, M4A, M4B, AAC, FLAC, WAV, OGG, WMA
- Output: Opus (.opus)

## Troubleshooting

```bash
# Check dependencies
python3 --version    # Should be 3.7+
ffmpeg -version      # Should be installed

# Verify Opus support
ffmpeg -codecs | grep opus

# Make script executable
chmod +x convert_audiobooks.py

# Run with verbose output
python3 convert_audiobooks.py -v
```

## How It Works

1. Scans source directory recursively for audio files
2. Creates parallel workers (one per CPU core by default)
3. Converts each file using FFmpeg with Opus codec
4. Maintains directory structure and metadata
5. Skips files that already exist in output directory

## Project Structure

```plain
audiobook-opus-converter/
├── convert_audiobooks.py    # Main script
├── README.md                # Documentation
├── original/                # Place source files here
│   └── Book Name/
│       └── chapter01.mp3
└── opus/                    # Converted files (auto-created)
    └── Book Name/
        └── chapter01.opus
```

## Requirements

- Python 3.7 or later
- FFmpeg with libopus support

```bash
# Ubuntu/Debian
sudo apt install ffmpeg python3

# Fedora
sudo dnf install ffmpeg python3

# Arch Linux
sudo pacman -S ffmpeg python3

# macOS
brew install ffmpeg python3
```
