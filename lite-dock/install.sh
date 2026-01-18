#!/bin/bash
set -e

echo "Building lite-dock..."

# Navigate to script directory
cd "$(dirname "$0")"

# Check Go version or install it locally
GO_VERSION="1.22.0"
GO_DIR="$HOME/.go_local"
GO_BIN="$GO_DIR/go/bin/go"

setup_go() {
    echo "Checking Go version..."
    if command -v go &> /dev/null; then
        CURRENT_VER=$(go version | grep -oE "go[0-9]+\.[0-9]+")
        # Simple string comparison isn't perfect but works for massive version diffs (go1.13 vs go1.22)
        if [[ "$CURRENT_VER" == "go1.22"* ]] || [[ "$CURRENT_VER" == "go1.23"* ]]; then
            echo "Found suitable Go version: $CURRENT_VER"
            return 0
        fi
        echo "Found Go version $CURRENT_VER, but we need go1.22+. Switching to local install."
    fi

    if [ -f "$GO_BIN" ]; then
        echo "Using local Go from $GO_BIN"
        export PATH="$GO_DIR/go/bin:$PATH"
        return 0
    fi

    echo "Installing Go $GO_VERSION to $GO_DIR..."
    mkdir -p "$GO_DIR"
    wget -q https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz -O "$GO_DIR/go.tar.gz"
    
    # Remove old extraction
    rm -rf "$GO_DIR/go"
    tar -C "$GO_DIR" -xzf "$GO_DIR/go.tar.gz"
    rm "$GO_DIR/go.tar.gz"
    
    export PATH="$GO_DIR/go/bin:$PATH"
    echo "Go installed at $(which go)"
}

setup_go

# Check for runc
if ! command -v runc &> /dev/null; then
    echo "runc not found. Attempting to install..."
    if command -v apt-get &> /dev/null; then
        echo "Running: sudo apt-get update && sudo apt-get install -y runc"
        sudo apt-get update
        sudo apt-get install -y runc
    else
        echo "Error: 'runc' is missing and could not find apt-get."
        echo "Please install runc manually (e.g., sudo apt install runc)."
        exit 1
    fi
fi

# Tidy dependencies which might verify network too
go mod tidy

# Build
go build -o lite-dock main.go

echo "Build complete! Binary matches: $(ls -l lite-dock)"
echo "You can now run: ./lite-dock help"
