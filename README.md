# Freva Tool Configuration with `tool.toml`

Freva allows users to define data analysis tools in a structured and
reproducible way using `tool.toml` configuration files. These files provide
a standardized interface for defining tool metadata, parameters, dependencies,
and execution commands. Freva parses these files to automatically create a
user interface (via command-line or web UI) for applying the tools in a
reproducible manner.

## Purpose

The `tool.toml` file simplifies the process of:
1. **Tool Definition**:
   - Specify metadata such as name, version, and description.
   - Define input parameters, execution commands, and dependencies.
2. **Reproducibility**:
   - Document dependencies and build processes for consistent execution.
   - Capture all required information in a single, portable file.
3. **User Interface Integration**:
   - Automatically generate a CLI or web interface for the tool based on
     the `tool.toml` configuration.

## Writing the `tool.toml` File

The `tool.toml` file is structured into several sections:

### **1. General Information**
The `[tool]` section provides metadata about the tool.

```toml
[tool]
name = "example-tool"  # Unique name for the tool
version = "v1.0.0"  # Semantic version
authors = ["Author 1 <author1@email.com>", "Author 2 <author2@email.com>"]
summary = "A brief description of what this tool does."
title = "A catchy title for the tool (optional)"
description = """
A detailed explanation of the tool's purpose, functionality, and usage.
"""
```

### **2. Execution Settings**
The [tool.run] section defines how the tool is executed.

```toml
[tool.run]
command = "python script.py"  # Command to run the tool
dependencies = ["python=3.10", "numpy"]  # Conda-Forge dependencies
```

If the tool requires compilation or installation steps, include a build.sh script,
and define build-time dependencies in the `[tool.build]` section:

```toml
[tool.build]
dependencies = ["rust"]  # Build-specific dependencies
```

### **3. Input Parameters**

The `[tool.input_parameters]` section specifies the parameters the tool accepts.

Each parameter is defined with:

- `title`: The name or description of the parameter.
- `type`: The expected data type (e.g., string, integer, float).
- `mandatory`: Whether the parameter is required.
- `default`: The default value (if optional).
- `help`: A detailed explanation of the parameter's purpose.


```toml
[tool.input_parameters.parameter_1]
title = "Input File"
type = "string"
mandatory = true
help = "The path to the input file for the analysis."

[tool.input_parameters.parameter_2]
title = "Verbose Mode"
type = "bool"
default = false
help = "Enable verbose output during execution."
```

### **4. Advanced Features**

Freva supports advanced parameter types, such as databrowser integration or ranges, for more complex use cases.
Databrowser Parameters

These allow integration with a databrowser search interface:

#### Databrowser Parameters

These allow integration with a databrowser search interface:

```toml
[tool.input_parameters.parameter_db]
title = "Search Parameter"
type = "databrowser"
search_key = "variable"
default = "tas"
help = """
Integrates with the databrowser to search for data based on the specified key.
"""
```

#### Range Parameters

Define ranges for numerical inputs:

```toml
[tool.input_parameters.parameter_range]
title = "Range Example"
type = "range"
default = [0, 10, 1]
help = "Specify a numerical range in the format [start, end, increment]."
```

## Tool Execution Workflow

1. Define the tool.toml File:
    - Create the tool.toml file with the required sections.
1. Parse with Freva:
    - Freva parses the tool.toml file to generate a CLI or web interface.
1. Run the Tool:
    - Users can apply the tool through the Freva interface, providing input parameters interactively or via scripts.
1. Reproducibility:
    - Freva ensures all executions are logged with version and parameter details for reproducibility.


## Best Practices

- Semantic Versioning: Use clear versioning for tools (e.g., v1.0.0) to track changes.
- Dependencies: List all required dependencies explicitly in the tool.run.dependencies or tool.build.dependencies sections.
- Parameters: Provide descriptive help messages for all parameters to guide users.
- Reproducibility: Document any additional setup steps (e.g., build.sh) and ensure they are included in the tool's environment.

## Additional Resources

- [TOML Syntax Documentation](https://toml.io)
- [Conda forge](https://conda-forge.org/)
