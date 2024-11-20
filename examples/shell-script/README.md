# Example Shell Script Tool

This example demonstrates how to define a tool in `tool.toml` to set up a 
**bash shell script** execution environment using Conda-Forge. The tool 
executes a shell script (`example.sh`) which takes a single command-line 
argument: a `JSON` file containing all the parsed parameters defined in the 
`tool.toml` file.

## Purpose

This configuration allows you to:
1. Define a reproducible Conda-Forge environment specifically tailored for 
   running shell scripts.
2. Specify and document input parameters directly in the `tool.toml` file.
3. Provide flexibility by parameterizing the shell script through a `JSON` 
   file generated from the tool's input configuration.

## How It Works

1. **Environment Setup**:
   - The `tool.toml` file specifies all dependencies required to run the 
     shell script. For this example, dependencies such as `python=3.13` are 
     included to support auxiliary functionality like parsing JSON.

2. **Parameter Input**:
   - Input parameters, along with their metadata (e.g., type, default value, 
     and description), are defined in the `tool.input_parameters` section of 
     the `tool.toml` file.

3. **Script Execution**:
   - When the tool runs, it generates a `JSON` file containing the parsed 
     parameters from the `tool.toml` configuration.
   - This `JSON` file is passed as an argument to the shell script 
     (`example.sh`), allowing the script to dynamically handle user-defined 
     parameters.

## Example Use Case

- **File Processing**:
  Execute a shell script that processes files dynamically based on user-
  specified parameters such as file paths, processing methods, or filters.

- **System Automation**:
  Automate tasks like backups, deployments, or data migrations by defining 
  parameters for paths, thresholds, or other criteria in the `tool.toml` 
  configuration.

## Notes

- Ensure that all dependencies required by the shell script (e.g., `bash`, 
  `python`, `ffmpeg`) are specified in the `tool.run.dependencies` section 
  of `tool.toml`.
- For more details on TOML syntax, visit [https://toml.io](https://toml.io).

## Additional Resources

- [Conda-Forge Bash](https://github.com/conda-forge/bash-feedstock)
- [JSON Parsing in Bash](https://stedolan.github.io/jq/)
- [TOML Syntax Documentation](https://toml.io)
