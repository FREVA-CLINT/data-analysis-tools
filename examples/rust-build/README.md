# Example Rust Binary Tool

This example demonstrates how to define a tool in `tool.toml` to set up a 
**Rust binary execution environment** using Conda-Forge. The tool compiles 
and executes a Rust binary (`example`) which takes a single command-line 
argument: a `JSON` file containing all the parsed parameters defined in the 
`tool.toml` file.

## Purpose

This configuration allows you to:
1. Define a reproducible Conda-Forge environment with Rust as the primary 
   language.
2. Automate the build process for compiling the Rust binary.
3. Specify and document input parameters directly in the `tool.toml` file.

## How It Works

1. **Environment Setup**:
   - The `tool.toml` file specifies all dependencies required to build and 
     execute the Rust binary. For this example, the `rust` package is included 
     to provide the Rust compiler.

2. **Build Process**:
   - A `build.sh` script is required to handle all compilation or additional 
     commands needed to prepare the binary for execution.
   - This script is automatically executed during the build process.

3. **Parameter Input**:
   - Input parameters, along with their metadata (e.g., type, default value, 
     and description), are defined in the `tool.input_parameters` section of 
     the `tool.toml` file.

4. **Binary Execution**:
   - After the build process completes, the compiled binary is executed 
     using the command defined in `tool.run.command`. It dynamically handles 
     user-defined parameters provided through a `JSON` file.

## Build Script (`build.sh`)

The `build.sh` script is essential for tools requiring compilation. It allows 
you to define custom build steps. For this Rust example, the script compiles 
the binary and places it in the `target/release` directory.
