# Example Python Script Tool

This example demonstrates how to define a tool in `tool.toml` to set up a 
**Python** environment using Conda-Forge. The tool executes a Python script 
(`example.py`) which takes a single command-line argument: a `JSON` file 
containing all the parsed parameters defined in the `tool.toml` file.

## Purpose

This configuration allows you to:
1. Define a reproducible Conda-Forge environment specifically tailored for 
   running Python scripts.
2. Specify and document input parameters directly in the `tool.toml` file.
3. Provide flexibility by parameterizing the Python script through a `JSON` 
   file generated from the tool's input configuration.

## How It Works

1. **Environment Setup**:
   - The `tool.toml` file specifies all dependencies required to run the 
     Python script. For this example, the `python=3.13` package is included 
     to provide the Python environment.
    - Additional pip based dependencies can be added into the [requirements.txt]
      file. Those dependencies will be added automatically to the conda environment.

2. **Parameter Input**:
   - Input parameters, along with their metadata (e.g., type, default value, 
     and description), are defined in the `tool.input_parameters` section of 
     the `tool.toml` file.

3. **Script Execution**:
   - When the tool runs, it generates a `JSON` file containing the parsed 
     parameters from the `tool.toml` configuration.
   - This `JSON` file is passed as an argument to the Python script 
     (`example.py`), allowing the script to dynamically handle user-defined 
     parameters.

## Example Use Case

- **Data Processing**:
  Run a Python script to process data dynamically, based on user-specified 
  parameters such as file paths, thresholds, or processing options.

- **Machine Learning**:
  Train or evaluate machine learning models with parameters like hyper-
  parameters, datasets, and evaluation metrics passed through the 
  `tool.toml` configuration.

## Notes

- Ensure that all dependencies (e.g., `python`, `ffmpeg`) are specified in the 
  `tool.run.dependencies` section of `tool.toml`.
- For more details on TOML syntax, visit [https://toml.io](https://toml.io).

## Additional Resources

- [Conda-Forge Python](https://conda-forge.org/feedstocks/python)
- [JSON Parsing in Python](https://docs.python.org/3/library/json.html)
- [TOML Syntax Documentation](https://toml.io)

