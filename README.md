# Audiobook to Opus Converter

A Python tool that efficiently converts audiobooks to the [Opus format](https://opus-codec.org/), optimized for voice content. Achieves significant file size reduction while maintaining excellent audio quality, with automatic parallel processing using all CPU cores.

## Features

- ✅ **Fast** - Parallel processing using all CPU cores by default
- ✅ **High Compression** - Opus codec works well for voice content
- ✅ **Quality Preserved** - Maintains metadata, directory structure, and cover art
- ✅ **Smart** - Skips already converted files; copies Opus files if already optimal
- ✅ **Flexible Stereo Handling** - Downmix to mono, keep stereo, or increase bitrate
- ✅ **Cover Image Support** - Automatically copies and optimizes cover images
- ✅ **Simple** - Single command with sensible defaults
- ✅ **Flexible** - Supports MP3, M4A, M4B, AAC, FLAC, WAV, OGG, WMA, Opus

## Quick Start

```bash
# Install dependencies
sudo apt install ffmpeg python3 imagemagick  # Ubuntu/Debian
# or: brew install ffmpeg python3 imagemagick  # macOS

# Convert audiobooks (uses all CPU cores, 20k bitrate by default)
python3 convert_audiobooks.py

# Or use recommended 24k bitrate
python3 convert_audiobooks.py -b 24k
```

Input files: `./original/` → Output files: `./opus/`

## Usage

### Basic Examples

```bash
# Convert with defaults (all CPU cores, 20k bitrate, downmix stereo to mono)
python3 convert_audiobooks.py

# Custom directories
python3 convert_audiobooks.py -s ~/Audiobooks -o ~/Audiobooks_Opus

# Specific number of workers
python3 convert_audiobooks.py -w 4

# High quality
python3 convert_audiobooks.py -b 24k

# Keep stereo files as stereo
python3 convert_audiobooks.py --stereo keep

# Increase bitrate for stereo files (32k)
python3 convert_audiobooks.py --stereo increase-bitrate

# Verbose output
python3 convert_audiobooks.py -v
```

### Options

```plain
-s, --source DIR       Source directory (default: ./original)
-o, --output DIR       Output directory (default: ./opus)
-b, --bitrate RATE     Bitrate: 15k, 20k, 24k, 32k, 40k, 48k, etc. (default: 20k)
-w, --workers NUM      Parallel workers (default: CPU count)
--stereo STRATEGY      Stereo handling: downmix, keep, increase-bitrate (default: downmix)
--no-images            Skip copying cover images
--no-skip              Re-convert existing files
-v, --verbose          Verbose output
--no-color             Disable colors
-h, --help             Show help
```

## Quality Settings

Choosing the right bitrate depends on your source recording quality and personal preferences:

| Bitrate | Quality | Characteristics | Best For |
| ------- | ------- | --------------- | -------- |
| 15k | Good | Narrower frequency range, some artifacts in sibilants (S/SH sounds) | Lower quality recordings, maximum compression |
| 20k | Very Good | Improved clarity, still some muddiness in sibilants | General use, balanced quality/size |
| **24k** | **Excellent** | Natural sibilants, recommended by Opus developers | **Most audiobooks** |
| 32k | High | Better transparency and frequency response | High-quality recordings |
| 40k+ | Very High | Fuller sound, closer to source | Studio-quality recordings |

**Recommendations:**

- **24k** is the sweet spot for most audiobooks (recommended by [xiph.org](https://wiki.xiph.org/Opus_Recommended_Settings) for mono speech)
- **15k** works surprisingly well for lower-quality source recordings
- **32k+** is worthwhile for high-quality studio recordings where you can hear the difference
- For stereo files with `--stereo increase-bitrate`, the script automatically uses 60% higher bitrates (e.g., 20k → 32k)
- You can use any bitrate value (e.g., 19k, 21k, 26k) - Opus VBR is flexible

**Note:** Opus excels at low bitrates, but no bitrate perfectly preserves the full bandwidth and clarity of high-quality source recordings. Test different bitrates with your specific audiobooks to find the best balance for your needs.

## Stereo Handling

The script provides three strategies for handling multi-channel audio:

### downmix (Default)

Converts stereo to mono, preserving more bitrate for voice clarity. Best for audiobooks where narration is the primary focus.

```bash
python3 convert_audiobooks.py --stereo downmix
```

### keep

Keeps stereo files as-is. At lower bitrates (e.g., 20k), Opus may partially downmix stereo anyway.

```bash
python3 convert_audiobooks.py --stereo keep
```

### increase-bitrate

Automatically increases bitrate for stereo files by 60% to preserve stereo imaging. Examples:
- 15k → 24k
- 20k → 32k
- 24k → 38k
- 32k → 51k
- 40k → 64k

```bash
python3 convert_audiobooks.py --stereo increase-bitrate
```

## Technical Details

**Codec Settings:**

- Opus at 20 kbps VBR (Variable Bitrate) by default
- VOIP mode (optimized for speech)
- Compression level 10 (maximum quality)
- Preserves all metadata and cover art
- Smart handling: Copies Opus files if source bitrate ≤ target bitrate
- Stereo downmixing to mono (default) for better voice quality

**Supported Formats:**

- Input: MP3, M4A, M4B, AAC, FLAC, WAV, OGG, WMA, Opus
- Output: Opus (.opus)

**Cover Images:**

- Automatically finds and copies common cover files:
  - Names: cover, folder, album, front
  - Formats: .jpg, .jpeg, .png, .webp
- Optimizes images (requires ImageMagick): resizes to max 1200px, reduces quality to 85%, strips metadata
- Falls back to simple copy if ImageMagick is not installed
- ImageMagick is commonly pre-installed on most Linux distributions

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
3. For each file:
   - If already Opus with bitrate ≤ target: copies file (no re-encoding)
   - Otherwise: converts using FFmpeg with Opus codec
   - Applies stereo strategy (downmix/keep/increase-bitrate)
4. Maintains directory structure and metadata
5. Copies and optimizes cover images (cover.jpg, folder.png, etc.)
6. Skips files that already exist in output directory

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

**Required:**
- Python 3.7 or later
- FFmpeg with libopus support

**Optional:**
- ImageMagick (for cover image optimization, usually pre-installed on Linux)

```bash
# Ubuntu/Debian
sudo apt install ffmpeg python3 imagemagick

# Fedora
sudo dnf install ffmpeg python3 ImageMagick

# Arch Linux
sudo pacman -S ffmpeg python3 imagemagick

# macOS
brew install ffmpeg python3 imagemagick
```
