#!/bin/bash

# Video Transcription CLI Tool - Installer
# Interactive installation script for macOS

set -e

# Colour codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo ""
}

ask_yes_no() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer y or n.";;
        esac
    done
}

# Main installation process
print_header "Video Transcription CLI - Installation"

echo "This script will install the required dependencies for the"
echo "Video Transcription CLI tool."
echo ""

# Track what was installed
INSTALLED_ITEMS=()

# 1. Check for Homebrew
print_header "Step 1: Homebrew"

if command -v brew &> /dev/null; then
    print_success "Homebrew is already installed"
    BREW_VERSION=$(brew --version | head -n1)
    print_info "$BREW_VERSION"
else
    print_warning "Homebrew is not installed"
    echo "Homebrew is required to install ffmpeg and other dependencies."
    echo ""

    if ask_yes_no "Would you like to install Homebrew?"; then
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ $(uname -m) == 'arm64' ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi

        print_success "Homebrew installed successfully"
        INSTALLED_ITEMS+=("Homebrew")
    else
        print_error "Cannot continue without Homebrew"
        exit 1
    fi
fi

# 2. Check for ffmpeg
print_header "Step 2: ffmpeg"

if command -v ffmpeg &> /dev/null; then
    print_success "ffmpeg is already installed"
    FFMPEG_VERSION=$(ffmpeg -version | head -n1)
    print_info "$FFMPEG_VERSION"
else
    print_warning "ffmpeg is not installed"
    echo "ffmpeg is required to extract audio from video files."
    echo ""

    if ask_yes_no "Would you like to install ffmpeg via Homebrew?"; then
        print_info "Installing ffmpeg..."
        brew install ffmpeg
        print_success "ffmpeg installed successfully"
        INSTALLED_ITEMS+=("ffmpeg")
    else
        print_error "Cannot continue without ffmpeg"
        exit 1
    fi
fi

# 3. Check for Python 3
print_header "Step 3: Python 3"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [[ $PYTHON_MAJOR -ge 3 ]] && [[ $PYTHON_MINOR -ge 8 ]]; then
        print_success "Python $PYTHON_VERSION is installed"
    else
        print_warning "Python $PYTHON_VERSION is installed, but 3.8+ is recommended"
        echo ""

        if ask_yes_no "Would you like to install the latest Python 3 via Homebrew?"; then
            print_info "Installing Python 3..."
            brew install python3
            print_success "Python 3 installed successfully"
            INSTALLED_ITEMS+=("Python 3")
        fi
    fi
else
    print_warning "Python 3 is not installed"
    echo "Python 3.8+ is required to run the transcription tool."
    echo ""

    if ask_yes_no "Would you like to install Python 3 via Homebrew?"; then
        print_info "Installing Python 3..."
        brew install python3
        print_success "Python 3 installed successfully"
        INSTALLED_ITEMS+=("Python 3")
    else
        print_error "Cannot continue without Python 3"
        exit 1
    fi
fi

# 4. Check for pip
print_header "Step 4: pip"

if command -v pip3 &> /dev/null; then
    print_success "pip3 is already installed"
    PIP_VERSION=$(pip3 --version)
    print_info "$PIP_VERSION"
else
    print_warning "pip3 is not installed"
    print_info "Installing pip3..."

    # pip should come with Python 3, but install if missing
    python3 -m ensurepip --upgrade
    print_success "pip3 installed successfully"
    INSTALLED_ITEMS+=("pip3")
fi

# 5. Install Python dependencies
print_header "Step 5: Python Dependencies"

echo "The following Python packages will be installed:"
echo "  - openai-whisper (includes PyTorch, NumPy, and other dependencies)"
echo ""
print_warning "Note: The first installation may take several minutes as it downloads"
print_warning "PyTorch and other large dependencies."
echo ""

if ask_yes_no "Would you like to install the Python dependencies?"; then
    print_info "Installing dependencies from requirements.txt..."

    # Get the directory where this script is located
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
        pip3 install --upgrade -r "$SCRIPT_DIR/requirements.txt"
        print_success "Python dependencies installed successfully"
        INSTALLED_ITEMS+=("Python dependencies (openai-whisper)")
    else
        print_error "requirements.txt not found in $SCRIPT_DIR"
        exit 1
    fi
else
    print_warning "Skipping Python dependencies installation"
    print_warning "You will need to install them manually with:"
    print_warning "  pip3 install -r requirements.txt"
fi

# 6. Create symlink (optional)
print_header "Step 6: Command-line Access"

echo "You can optionally create a 'transcribe' command that can be run"
echo "from anywhere by creating a symlink in /usr/local/bin."
echo ""
print_info "This allows you to run 'transcribe video.mp4' instead of"
print_info "'python3 ~/Sites/video-transcribe/transcribe.py video.mp4'"
echo ""

if ask_yes_no "Would you like to create the 'transcribe' command?"; then
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    TRANSCRIBE_SCRIPT="$SCRIPT_DIR/transcribe.py"
    SYMLINK_PATH="/usr/local/bin/transcribe"

    # Make the script executable
    chmod +x "$TRANSCRIBE_SCRIPT"

    # Create /usr/local/bin if it doesn't exist
    if [[ ! -d "/usr/local/bin" ]]; then
        print_info "Creating /usr/local/bin directory..."
        sudo mkdir -p /usr/local/bin
    fi

    # Remove existing symlink if present
    if [[ -L "$SYMLINK_PATH" ]] || [[ -f "$SYMLINK_PATH" ]]; then
        print_info "Removing existing 'transcribe' command..."
        sudo rm "$SYMLINK_PATH"
    fi

    # Create symlink
    print_info "Creating symlink..."
    sudo ln -s "$TRANSCRIBE_SCRIPT" "$SYMLINK_PATH"

    print_success "Command 'transcribe' created successfully"
    INSTALLED_ITEMS+=("'transcribe' command")
else
    print_info "Skipping symlink creation"
    print_info "You can run the tool with: python3 transcribe.py <video-file>"
fi

# Final summary
print_header "Installation Complete!"

if [ ${#INSTALLED_ITEMS[@]} -gt 0 ]; then
    echo "The following items were installed:"
    for item in "${INSTALLED_ITEMS[@]}"; do
        echo "  • $item"
    done
    echo ""
fi

print_success "All dependencies are ready!"
echo ""
echo "You can now transcribe videos using:"
echo ""

if [[ -L "/usr/local/bin/transcribe" ]]; then
    echo -e "  ${GREEN}transcribe video.mp4${NC}"
    echo -e "  ${GREEN}transcribe video1.mp4 video2.mp4${NC}"
    echo -e "  ${GREEN}transcribe video.mp4 --model small --language en${NC}"
else
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    echo -e "  ${GREEN}python3 $SCRIPT_DIR/transcribe.py video.mp4${NC}"
    echo -e "  ${GREEN}python3 $SCRIPT_DIR/transcribe.py video1.mp4 video2.mp4${NC}"
fi

echo ""
echo "For more information, see the README.md file."
echo ""
