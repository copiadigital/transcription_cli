# Video Transcription CLI

A command-line tool for extracting audio from videos and generating timestamped transcripts using OpenAI Whisper.

## Features

- **Automatic audio extraction** from video files using ffmpeg
- **High-quality transcription** powered by OpenAI Whisper
- **Multiple output formats**: SRT subtitles and plain text with timestamps
- **Batch processing**: Transcribe multiple videos in one command
- **Flexible model selection**: Choose from 5 Whisper model sizes
- **Language support**: Auto-detect or specify source language
- **Progress tracking**: Clear progress indicators and summary reports
- **Error handling**: Detailed error logging for failed transcriptions

## Installation

### Requirements

- macOS (tested on macOS 11+)
- Homebrew (will be installed if missing)
- Python 3.8+ (will be installed if missing)
- ffmpeg (will be installed if missing)

### Quick Install

1. Clone or download this repository:
   ```bash
   cd ~/Sites
   git clone git@github.com:copiadigital/transcription_cli.git video-transcribe
   cd video-transcribe
   ```

2. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. Follow the interactive prompts to install dependencies.

The installer will:
- Check and install Homebrew (if needed)
- Install ffmpeg via Homebrew
- Verify Python 3.8+ is installed
- Install Python dependencies (openai-whisper)
- Optionally create a `transcribe` command in your PATH

## Usage

### Basic Usage

Transcribe a single video:
```bash
transcribe video.mp4
```

Or if you didn't create the symlink:
```bash
python3 transcribe.py video.mp4
```

### Batch Processing

Transcribe multiple videos:
```bash
transcribe video1.mp4 video2.mp4 video3.mp4
```

Process all MP4 files in a directory:
```bash
transcribe *.mp4
```

### Options

#### Model Selection

Choose a Whisper model size (tiny, base, small, medium, large):
```bash
transcribe video.mp4 --model small
```

**Model comparison:**
- `tiny`: Fastest, least accurate (~1GB RAM)
- `base`: Good balance of speed and accuracy (default, ~1GB RAM)
- `small`: Better accuracy, slower (~2GB RAM)
- `medium`: High accuracy, much slower (~5GB RAM)
- `large`: Best accuracy, very slow (~10GB RAM)

#### Language Specification

Specify the source language for better accuracy:
```bash
transcribe video.mp4 --language en
```

Common language codes: `en` (English), `es` (Spanish), `fr` (French), `de` (German), `it` (Italian), `pt` (Portuguese), `nl` (Dutch), `ja` (Japanese), `zh` (Chinese)

If not specified, Whisper will auto-detect the language.

#### Output Directory

Specify a custom output directory:
```bash
transcribe video.mp4 --output-dir ./transcripts
```

By default, output files are saved in the same directory as the input video.

### Combined Options

```bash
transcribe video1.mp4 video2.mp4 --model small --language en --output-dir ./output
```

## Output Formats

The tool generates two output files for each video:

### 1. SRT Subtitle File (`.srt`)

Standard SubRip subtitle format, compatible with most video players and editing software:

```
1
00:00:00,000 --> 00:00:03,500
This is the first subtitle line.

2
00:00:03,500 --> 00:00:07,200
This is the second subtitle line.
```

**Use cases:**
- Add subtitles to videos
- Import into video editing software
- Use with media players (VLC, QuickTime, etc.)

### 2. Plain Text File (`.txt`)

Simple text format with timestamps:

```
[00:00:00.000] This is the first subtitle line.
[00:00:03.500] This is the second subtitle line.
```

**Use cases:**
- Easy reading and searching
- Content analysis
- Documentation

## Examples

### Example 1: Quick Transcription

Transcribe a single video with default settings:
```bash
transcribe meeting.mp4
```

Output:
```
Processing 1 video(s)...
============================================================

Processing file 1 of 1: meeting.mp4
------------------------------------------------------------
Loading Whisper model 'base'...
Model loaded successfully.
Extracting audio from 'meeting.mp4'...
Audio extracted successfully.
Transcribing audio with Whisper...
Transcription completed.
Generating SRT file: meeting.srt
Generating text file: meeting.txt

✓ Successfully transcribed 'meeting.mp4'
  Output files:
    - /path/to/meeting.srt
    - /path/to/meeting.txt
```

### Example 2: Batch Processing

Transcribe multiple videos with a better model:
```bash
transcribe lecture1.mp4 lecture2.mp4 lecture3.mp4 --model small
```

### Example 3: Non-English Content

Transcribe Spanish content with language hint:
```bash
transcribe spanish-video.mp4 --language es --model small
```

### Example 4: Organised Output

Process all videos and save transcripts to a separate directory:
```bash
mkdir transcripts
transcribe *.mp4 --output-dir ./transcripts
```

## Error Handling

If a transcription fails:
1. The tool will continue processing remaining videos
2. A summary will show which videos succeeded and failed
3. Error details are saved to `transcription_errors.log`

Example output:
```
SUMMARY
============================================================
Total videos: 3
Successful: 2
Failed: 1

Failed videos:
  - corrupted-video.mp4: Failed to extract audio: Invalid data found

Error details saved to: /path/to/transcription_errors.log
```

## Troubleshooting

### "Error: ffmpeg is not installed"

Install ffmpeg manually:
```bash
brew install ffmpeg
```

### "Error: openai-whisper is not installed"

Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

### "No speech detected in video"

The video may not contain any speech, or the audio track may be missing. Verify the video has audio:
```bash
ffmpeg -i video.mp4
```

### Slow transcription

- Use a smaller model: `--model tiny` or `--model base`
- Consider GPU acceleration (requires additional setup with PyTorch CUDA)

### Out of memory errors

- Use a smaller model: `--model tiny` or `--model base`
- Close other applications to free up RAM
- Process videos one at a time instead of in batch

## Technical Details

### Dependencies

- **openai-whisper**: OpenAI's Whisper speech recognition model
- **ffmpeg**: Audio/video processing toolkit
- **PyTorch**: Machine learning framework (installed automatically with Whisper)

### Audio Processing

Videos are converted to:
- Format: 16-bit PCM WAV
- Sample rate: 16kHz
- Channels: Mono

This format is optimal for Whisper transcription.

### Model Storage

Whisper models are automatically downloaded on first use and cached in:
```
~/.cache/whisper/
```

Models are reused for subsequent transcriptions.

## Development

### Project Structure

```
video-transcribe/
├── install.sh              # Interactive installer script
├── transcribe.py           # Main CLI application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- Use British English spelling in documentation
- Test with multiple video formats
- Update README for new features

## Licence

This tool is provided as-is for internal use at Copia Digital.

## Credits

- **OpenAI Whisper**: https://github.com/openai/whisper
- **ffmpeg**: https://ffmpeg.org/

## Support

For issues or questions, contact the development team.
