#!/usr/bin/env python3

import json
import logging
import sys
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load and parse the configuration JSON file.

    Parameters
    -----------
    config_file (str):
        Path to the configuration JSON file.

    Returns
    -------
    Dict[str, Any]:
        Parsed configuration as a dictionary.

    Raises
    -------
    FileNotFoundError:
        If the file does not exist.
    json.JSONDecodeError:
        If the JSON is not properly formatted.
    """
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except FileNotFoundError as error:
        logging.error(f"Error: File '{config_file}' does not exist.")
        raise error
    except json.JSONDecodeError as error:
        logging.error(
            f"Error: Invalid JSON format in '{config_file}': {error}"
        )
        raise error


def main(config_file: str) -> None:
    """
    Main function to evaluate the configuration file and perform actions.

    Parameters
    -----------
    config_file (str):
        Path to the configuration JSON file.
    """
    config = load_config(config_file)

    logging.info("Evaluating configuration from '%s'...", config_file)

    # Extract specific parameters with defaults
    parameter_1 = config.get("parameter_1", "default_value")
    parameter_2 = config.get("parameter_2")
    parameter_3 = config.get("parameter_3", "/path/to/default")
    parameter_4 = config.get("parameter_4", False)
    parameter_5 = config.get("parameter_5", "2000-01-01T00:00:00Z")

    # Handle mandatory parameter checks
    if parameter_2 is None:
        logging.error(
            "'parameter_2' is mandatory but is not provided in the config."
        )
        sys.exit(1)

    # Log extracted parameters
    logging.info("Extracted Parameters:")
    logging.info("  Parameter 1: %s", parameter_1)
    logging.info("  Parameter 2: %s", parameter_2)
    logging.info("  Parameter 3: %s", parameter_3)
    logging.info("  Parameter 4: %s", parameter_4)
    logging.info("  Parameter 5: %s", parameter_5)

    # Perform actions based on the parameters
    logging.info("Performing actions based on the configuration...")

    # Example: Conditional logic based on a boolean parameter
    if parameter_4:
        logging.info("Boolean parameter is true, taking appropriate action.")

    # Example: Using a parameter in a simulated action
    if parameter_3:
        logging.info("Simulating action with parameter 3: %s", parameter_3)

    logging.info("Configuration evaluation completed successfully.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <config.json>")

    config_file_path = sys.argv[1]
    main(config_file_path)
