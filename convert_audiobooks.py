#!/usr/bin/env python3
"""
Audiobook to Opus Converter
Converts audiobooks to opus format with optimal settings for voice content.
"""

import argparse
import subprocess
import sys
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple
import logging
from dataclasses import dataclass
import multiprocessing


@dataclass
class ConversionStats:
    """Statistics for conversion process"""

    total_files: int = 0
    converted_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0


class Colors:
    """ANSI color codes for terminal output"""

    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    NC = "\033[0m"  # No Color

    @classmethod
    def disable(cls):
        """Disable colors for non-terminal output"""
        cls.BLUE = cls.GREEN = cls.YELLOW = cls.RED = cls.NC = ""


class AudiobookConverter:
    """Main converter class"""

    SUPPORTED_FORMATS = (
        ".mp3",
        ".m4a",
        ".m4b",
        ".aac",
        ".flac",
        ".wav",
        ".ogg",
        ".wma",
        ".opus",
    )

    def __init__(
        self,
        source_dir: Path,
        output_dir: Path,
        bitrate: str = "20k",
        skip_existing: bool = True,
        workers: int = 1,
        verbose: bool = False,
    ):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.bitrate = bitrate
        self.skip_existing = skip_existing
        self.workers = workers
        self.verbose = verbose
        self.stats = ConversionStats()

        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=log_level, format="%(message)s")
        self.logger = logging.getLogger(__name__)

    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

    def check_dependencies(self) -> bool:
        """Check if FFmpeg is installed"""
        if not shutil.which("ffmpeg"):
            self.print_error("FFmpeg is not installed. Please install it first.")
            return False

        if not shutil.which("ffprobe"):
            self.print_error("FFprobe is not installed. Please install it first.")
            return False

        # Check for opus support
        try:
            result = subprocess.run(
                ["ffmpeg", "-codecs"], capture_output=True, text=True, timeout=5
            )
            if "libopus" not in result.stdout:
                self.print_error("FFmpeg does not have Opus codec support.")
                return False
        except Exception as e:
            self.print_error(f"Error checking FFmpeg codecs: {e}")
            return False

        return True

    def find_audio_files(self) -> List[Path]:
        """Find all audio files in source directory"""
        audio_files = []
        for ext in self.SUPPORTED_FORMATS:
            audio_files.extend(self.source_dir.rglob(f"*{ext}"))
        return sorted(audio_files)

    def get_output_path(self, input_path: Path) -> Path:
        """Get output path for converted file"""
        relative_path = input_path.relative_to(self.source_dir)
        output_path = self.output_dir / relative_path
        return output_path.with_suffix(".opus")

    def convert_file(self, input_file: Path) -> Tuple[bool, str]:
        """Convert a single audio file to Opus"""
        output_file = self.get_output_path(input_file)

        # Create output directory
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Check if output file already exists
        if self.skip_existing and output_file.exists():
            return True, f"Skipped (already exists): {output_file.name}"

        try:
            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                str(input_file),
                "-map",
                "0:a",  # Map only audio streams, exclude cover art/video
                "-map_metadata",
                "0",
                "-c:a",
                "libopus",
                "-b:a",
                self.bitrate,
                "-vbr",
                "on",
                "-compression_level",
                "10",
                "-application",
                "voip",
                str(output_file),
            ]

            # Run conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
            )

            if result.returncode == 0:
                self.stats.converted_files += 1
                return True, f"Converted: {output_file.name}"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                if self.verbose:
                    self.logger.error(f"FFmpeg error: {error_msg}")
                return False, f"Failed to convert: {input_file.name}"

        except subprocess.TimeoutExpired:
            return False, f"Timeout converting: {input_file.name}"
        except Exception as e:
            if self.verbose:
                self.logger.exception(f"Error converting {input_file}")
            return False, f"Error converting: {input_file.name} - {str(e)}"

    def process_file(self, input_file: Path) -> None:
        """Process a single file with progress output"""
        self.stats.total_files += 1

        self.print_info(f"Converting: {input_file.name}")

        success, message = self.convert_file(input_file)

        if success:
            if "Skipped" in message:
                self.print_info(message)
                self.stats.skipped_files += 1
            else:
                self.print_success(message)
        else:
            self.print_error(message)
            self.stats.failed_files += 1

    def run(self) -> int:
        """Main conversion process"""
        self.print_info("=" * 50)
        self.print_info("Audiobook to Opus Converter")
        self.print_info("=" * 50)
        self.print_info(f"Source: {self.source_dir}")
        self.print_info(f"Output: {self.output_dir}")
        self.print_info(f"Bitrate: {self.bitrate} (VBR)")
        self.print_info(f"Workers: {self.workers}")
        self.print_info("=" * 50)

        # Check dependencies
        if not self.check_dependencies():
            return 1

        # Check if source directory exists
        if not self.source_dir.exists():
            self.print_error(f"Source directory not found: {self.source_dir}")
            return 1

        # Find audio files
        self.print_info("Scanning for audio files...")
        audio_files = self.find_audio_files()

        if not audio_files:
            self.print_warning(f"No audio files found in {self.source_dir}")
            return 0

        self.print_info(f"Found {len(audio_files)} audio files")
        print()

        # Process files
        if self.workers == 1:
            # Single-threaded processing
            for audio_file in audio_files:
                self.process_file(audio_file)
        else:
            # Multi-threaded processing
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(self.convert_file, audio_file): audio_file
                    for audio_file in audio_files
                }

                # Process completed tasks
                for future in as_completed(future_to_file):
                    audio_file = future_to_file[future]
                    self.stats.total_files += 1

                    try:
                        success, message = future.result()

                        if success:
                            if "Skipped" in message:
                                self.print_info(message)
                                self.stats.skipped_files += 1
                            else:
                                self.print_success(message)
                        else:
                            self.print_error(message)
                            self.stats.failed_files += 1

                    except Exception as e:
                        self.print_error(f"Error processing {audio_file.name}: {e}")
                        self.stats.failed_files += 1

        # Print statistics
        print()
        self.print_info("=" * 50)
        self.print_info("Conversion Complete!")
        self.print_info("=" * 50)
        self.print_info(f"Total files found:        {self.stats.total_files}")
        self.print_success(f"Successfully converted:   {self.stats.converted_files}")
        self.print_warning(f"Skipped (already exist):  {self.stats.skipped_files}")

        if self.stats.failed_files > 0:
            self.print_error(f"Failed:                   {self.stats.failed_files}")

        self.print_info("=" * 50)

        return 0 if self.stats.failed_files == 0 else 1


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert audiobooks to Opus format optimized for voice content.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion with defaults
  %(prog)s

  # Custom source and output directories
  %(prog)s -s /path/to/audiobooks -o /path/to/output

  # High quality with 4 parallel workers
  %(prog)s -b 24k -w 4

  # Full custom setup
  %(prog)s -s ./books -o ./opus -b 20k -w 8 -v

Supported input formats:
  MP3, M4A, M4B, AAC, FLAC, WAV, OGG, WMA, Opus

Recommended bitrates for audiobooks:
  15k - Minimum quality, maximum compression
  20k - Recommended (default)
  24k - High quality
  32k - Maximum quality
        """,
    )

    parser.add_argument(
        "-s",
        "--source",
        type=Path,
        default=Path("./original"),
        help="Source directory containing audiobooks (default: ./original)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("./opus"),
        help="Output directory for converted files (default: ./opus)",
    )

    parser.add_argument(
        "-b",
        "--bitrate",
        type=str,
        default="20k",
        help="Target bitrate (e.g., 15k, 20k, 24k, 32k) (default: 20k)",
    )

    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (default: CPU count)",
    )

    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Re-convert files even if they already exist",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    # Disable colors if requested or not in a TTY
    if args.no_color or not sys.stdout.isatty():
        Colors.disable()

    # Set default workers to CPU count if not specified
    workers = args.workers if args.workers is not None else multiprocessing.cpu_count()

    # Create converter
    converter = AudiobookConverter(
        source_dir=args.source,
        output_dir=args.output,
        bitrate=args.bitrate,
        skip_existing=not args.no_skip,
        workers=workers,
        verbose=args.verbose,
    )

    # Run conversion
    try:
        return converter.run()
    except KeyboardInterrupt:
        print("\n\nConversion interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR]{Colors.NC} Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
