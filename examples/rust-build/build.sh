#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Check if Cargo is installed
if ! command -v cargo &> /dev/null
then
    echo "Error: Cargo is not installed. Please install Cargo to build this project."
    exit 1
fi

# Build the Rust project
echo "Building the Rust project..."
cargo build --release

# Confirm the build succeeded
if [ -f "./target/release/example" ]; then
    echo "Build succeeded. Binary is located at ./target/release/example"
else
    echo "Error: Build failed."
    exit 1
fi
