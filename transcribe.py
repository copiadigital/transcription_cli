#!/usr/bin/env python3
"""
Video Transcription CLI Tool
Extracts audio from videos and generates timestamped transcripts using OpenAI Whisper.
"""

import argparse
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import timedelta
from typing import List, Tuple, Optional

try:
    import whisper
except ImportError:
    print("Error: openai-whisper is not installed.")
    print("Please run: pip3 install -r requirements.txt")
    sys.exit(1)


class TranscriptionError(Exception):
    """Custom exception for transcription errors."""
    pass


class VideoTranscriber:
    """Handles video transcription with Whisper."""

    SUPPORTED_MODELS = ['tiny', 'base', 'small', 'medium', 'large']

    def __init__(self, model_name: str = 'base', language: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialise the transcriber.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            language: Source language code (e.g., 'en', 'es') or None for auto-detect
            output_dir: Directory for output files (uses video directory if None)
        """
        self.model_name = model_name
        self.language = language
        self.output_dir = Path(output_dir) if output_dir else None
        self.model = None

    def load_model(self):
        """Load the Whisper model (lazy loading)."""
        if self.model is None:
            print(f"Loading Whisper model '{self.model_name}'...")
            try:
                self.model = whisper.load_model(self.model_name)
                print("Model loaded successfully.")
            except Exception as e:
                raise TranscriptionError(f"Failed to load Whisper model: {e}")

    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def extract_audio(self, video_path: Path, temp_dir: str) -> Path:
        """
        Extract audio from video file using ffmpeg.

        Args:
            video_path: Path to input video file
            temp_dir: Temporary directory for audio file

        Returns:
            Path to extracted audio file (WAV format)
        """
        audio_path = Path(temp_dir) / f"{video_path.stem}.wav"

        print(f"Extracting audio from '{video_path.name}'...")

        try:
            # Extract audio as 16kHz mono WAV (optimal for Whisper)
            subprocess.run([
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite output file
                str(audio_path)
            ], capture_output=True, check=True, text=True)

            print("Audio extracted successfully.")
            return audio_path

        except subprocess.CalledProcessError as e:
            raise TranscriptionError(f"Failed to extract audio: {e.stderr}")

    def format_timestamp_srt(self, seconds: float) -> str:
        """
        Format timestamp for SRT format (HH:MM:SS,mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def format_timestamp_txt(self, seconds: float) -> str:
        """
        Format timestamp for plain text format ([HH:MM:SS.mmm]).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)

        return f"[{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}]"

    def transcribe_audio(self, audio_path: Path) -> dict:
        """
        Transcribe audio file using Whisper.

        Args:
            audio_path: Path to audio file

        Returns:
            Whisper transcription result dictionary
        """
        print("Transcribing audio with Whisper...")

        try:
            # Transcribe with word-level timestamps
            kwargs = {'verbose': False}
            if self.language:
                kwargs['language'] = self.language

            result = self.model.transcribe(str(audio_path), **kwargs)
            print("Transcription completed.")
            return result

        except Exception as e:
            raise TranscriptionError(f"Transcription failed: {e}")

    def generate_srt(self, result: dict, output_path: Path):
        """
        Generate SRT subtitle file from Whisper result.

        Args:
            result: Whisper transcription result
            output_path: Path for output SRT file
        """
        print(f"Generating SRT file: {output_path.name}")

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], start=1):
                start_time = self.format_timestamp_srt(segment['start'])
                end_time = self.format_timestamp_srt(segment['end'])
                text = segment['text'].strip()

                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def generate_txt(self, result: dict, output_path: Path):
        """
        Generate plain text file with timestamps from Whisper result.

        Args:
            result: Whisper transcription result
            output_path: Path for output text file
        """
        print(f"Generating text file: {output_path.name}")

        with open(output_path, 'w', encoding='utf-8') as f:
            for segment in result['segments']:
                timestamp = self.format_timestamp_txt(segment['start'])
                text = segment['text'].strip()
                f.write(f"{timestamp} {text}\n")

    def get_output_dir(self, video_path: Path) -> Path:
        """
        Get the output directory for a video file.

        Args:
            video_path: Path to video file

        Returns:
            Path to output directory
        """
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            return self.output_dir
        return video_path.parent

    def process_video(self, video_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Process a single video file.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Validate input file
        if not video_path.exists():
            return False, f"File not found: {video_path}"

        if not video_path.is_file():
            return False, f"Not a file: {video_path}"

        # Load model (first time only)
        try:
            self.load_model()
        except TranscriptionError as e:
            return False, str(e)

        # Process video
        temp_dir = None
        try:
            # Create temporary directory for audio extraction
            temp_dir = tempfile.mkdtemp()

            # Extract audio
            audio_path = self.extract_audio(video_path, temp_dir)

            # Transcribe
            result = self.transcribe_audio(audio_path)

            # Check if transcription contains any speech
            if not result.get('segments'):
                return False, "No speech detected in video"

            # Generate output files
            output_dir = self.get_output_dir(video_path)
            srt_path = output_dir / f"{video_path.stem}.srt"
            txt_path = output_dir / f"{video_path.stem}.txt"

            self.generate_srt(result, srt_path)
            self.generate_txt(result, txt_path)

            print(f"\n✓ Successfully transcribed '{video_path.name}'")
            print(f"  Output files:")
            print(f"    - {srt_path}")
            print(f"    - {txt_path}")

            return True, None

        except TranscriptionError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Extract audio from videos and generate timestamped transcripts using Whisper.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s video.mp4
  %(prog)s video1.mp4 video2.mp4 video3.mp4
  %(prog)s video.mp4 --model small --language en
  %(prog)s *.mp4 --output-dir ./transcripts
        """
    )

    parser.add_argument(
        'videos',
        nargs='+',
        help='video file(s) to transcribe'
    )

    parser.add_argument(
        '--model',
        default='base',
        choices=VideoTranscriber.SUPPORTED_MODELS,
        help='Whisper model size (default: base)'
    )

    parser.add_argument(
        '--language',
        help='source language code (e.g., en, es, fr) - auto-detect if not specified'
    )

    parser.add_argument(
        '--output-dir',
        help='output directory for transcripts (default: same as video)'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    # Check for ffmpeg
    transcriber = VideoTranscriber(
        model_name=args.model,
        language=args.language,
        output_dir=args.output_dir
    )

    if not transcriber.check_ffmpeg():
        print("Error: ffmpeg is not installed or not in PATH.")
        print("Please install ffmpeg using: brew install ffmpeg")
        sys.exit(1)

    # Convert video arguments to Path objects
    video_paths = [Path(v).resolve() for v in args.videos]
    total_videos = len(video_paths)

    # Process videos
    print(f"\nProcessing {total_videos} video(s)...\n")
    print("=" * 60)

    successes = []
    failures = []

    for i, video_path in enumerate(video_paths, start=1):
        print(f"\nProcessing file {i} of {total_videos}: {video_path.name}")
        print("-" * 60)

        success, error_msg = transcriber.process_video(video_path)

        if success:
            successes.append(video_path)
        else:
            failures.append((video_path, error_msg))
            print(f"\n✗ Failed to transcribe '{video_path.name}'")
            print(f"  Error: {error_msg}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total videos: {total_videos}")
    print(f"Successful: {len(successes)}")
    print(f"Failed: {len(failures)}")

    if failures:
        print("\nFailed videos:")
        for video_path, error_msg in failures:
            print(f"  - {video_path.name}: {error_msg}")

        # Save error log
        log_path = Path.cwd() / "transcription_errors.log"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("Transcription Errors Log\n")
            f.write("=" * 60 + "\n\n")
            for video_path, error_msg in failures:
                f.write(f"File: {video_path}\n")
                f.write(f"Error: {error_msg}\n\n")

        print(f"\nError details saved to: {log_path}")

    # Exit with appropriate code
    sys.exit(0 if not failures else 1)


if __name__ == '__main__':
    main()
