#!/bin/sh
# This is an example script that should demonstrate how your data-analysis
# shell based tool can handle the input.

# Check if the required input JSON file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <config.json>"
    exit 1
fi

# Read the JSON file
CONFIG_FILE="$1"

# Check if the file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: File '$CONFIG_FILE' does not exist."
    exit 1
fi

# Parse and extract values from the JSON file using jq
# By default jq (https://stedolan.github.io/jq/) is installed into the tools
# conda-forge environment.
echo "Evaluating configuration from '$CONFIG_FILE'..."

# Example: Extract specific parameters
PARAMETER_1=$(jq -r '.parameter_1' "$CONFIG_FILE")
PARAMETER_2=$(jq -r '.parameter_2' "$CONFIG_FILE")
PARAMETER_3=$(jq -r '.parameter_3' "$CONFIG_FILE")
PARAMETER_4=$(jq -r '.parameter_4' "$CONFIG_FILE")
PARAMETER_5=$(jq -r '.parameter_5' "$CONFIG_FILE")

# Handle default values or mandatory checks if needed
if [ -z "$PARAMETER_2" ]; then
    echo "Error: 'parameter_2' is mandatory but is not provided in the config."
    exit 1
fi

# Log extracted parameters
echo "Parameter 1: $PARAMETER_1"
echo "Parameter 2: $PARAMETER_2"
echo "Parameter 3: $PARAMETER_3"
echo "Parameter 4: $PARAMETER_4"
echo "Parameter 5: $PARAMETER_5"

# Perform actions based on the parameters
echo "Performing actions based on the configuration..."

# Example of conditional logic
if [ "$PARAMETER_4" = "true" ]; then
    echo "Boolean parameter is true, taking appropriate action."
fi

# Final message
echo "Configuration evaluation completed successfully."
exit 0
