# Example R Script Tool

This example demonstrates how to define a tool in `tool.toml` to set up a 
**GNU R** environment using Conda-Forge. The tool executes an R script 
(`example.R`) which takes a single command-line argument: a `JSON` file 
containing all the parsed parameters defined in the `tool.toml` file.

## Purpose

This configuration allows you to:
1. Define a reproducible Conda-Forge environment specifically tailored for 
   running R scripts.
2. Specify and document input parameters directly in the `tool.toml` file.
3. Provide flexibility by parameterizing the R script through a `JSON` file 
   generated from the tool's input configuration.

## How It Works

1. **Environment Setup**: 
   - The `tool.toml` file specifies all dependencies required to run the 
     R script. For this example, the `r-base` package is included to provide 
     the R environment.

2. **Parameter Input**: 
   - Input parameters, along with their metadata (e.g., type, default value, 
     and description), are defined in the `tool.input_parameters` section of 
     the `tool.toml` file.

3. **Script Execution**:
   - When the tool runs, it generates a `JSON` file containing the parsed 
     parameters from the `tool.toml` configuration.
   - This `JSON` file is passed as an argument to the R script (`example.R`), 
     allowing the script to dynamically handle user-defined parameters.

## Example Use Case

- **Data Analysis**:
  Run an R script that processes datasets dynamically, based on user-specified 
  parameters such as file paths, thresholds, or analysis methods.

- **Visualization**:
  Generate plots or dashboards in R by passing custom parameters for data 
  sources, filters, and styles through the `tool.toml` configuration.

## Notes

- Ensure that all dependencies (e.g., `r-base`, `jsonlite`) are specified in 
  the `tool.run.dependencies` section of `tool.toml`.
- For more details on TOML syntax, visit [https://toml.io](https://toml.io).

## Additional Resources

- [GNU R on Conda-Forge](https://conda-forge.org/feedstocks/r-base)
- [JSON Parsing in R (jsonlite)](https://cran.r-project.org/web/packages/jsonlite/index.html)
- [TOML Syntax Documentation](https://toml.io)

