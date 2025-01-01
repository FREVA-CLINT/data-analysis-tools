#!/usr/bin/env Rscript

# Load necessary libraries
if (!requireNamespace("jsonlite", quietly = TRUE)) {
  stop("Please install the 'jsonlite' package to run this script.")
}
if (!requireNamespace("futile.logger", quietly = TRUE)) {
  stop("Please install the 'futile.logger' package to run this script.")
}

library(jsonlite)
library(futile.logger)

# Configure logging
flog.appender(appender.console(), name = "default")
flog.threshold(INFO, name = "default")

load_config <- function(config_file) {
  #' Load and parse the configuration JSON file.
  #'
  #' @param config_file Path to the configuration JSON file.
  #' @return A list representing the parsed configuration.
  #' @throws Error if the file does not exist or JSON is invalid.

  if (!file.exists(config_file)) {
    flog.error("Error: File '%s' does not exist.", config_file)
    stop("Configuration file not found.")
  }

  tryCatch(
    {
      config <- fromJSON(config_file)
      return(config)
    },
    error = function(e) {
      flog.error("Error: Invalid JSON format in '%s': %s", config_file, e$message)
      stop("Failed to parse JSON configuration.")
    }
  )
}

main <- function(config_file) {
  #' Main function to evaluate the configuration file and perform actions.
  #'
  #' @param config_file Path to the configuration JSON file.

  # Load the configuration
  config <- tryCatch(
    load_config(config_file),
    error = function(e) {
      stop("Exiting due to error: ", e$message)
    }
  )

  flog.info("Evaluating configuration from '%s'...", config_file)

  # Extract specific parameters with defaults
  parameter_1 <- ifelse("parameter_1" %in% names(config), config$parameter_1, "default_value")
  parameter_2 <- ifelse("parameter_2" %in% names(config), config$parameter_2, NULL)
  parameter_3 <- ifelse("parameter_3" %in% names(config), config$parameter_3, "/path/to/default")
  parameter_4 <- ifelse("parameter_4" %in% names(config), config$parameter_4, FALSE)
  parameter_5 <- ifelse("parameter_5" %in% names(config), config$parameter_5, "2000-01-01T00:00:00Z")

  # Handle mandatory parameter checks
  if (is.null(parameter_2)) {
    flog.error("Error: 'parameter_2' is mandatory but is not provided in the config.")
    stop("Mandatory parameter missing.")
  }

  # Log extracted parameters
  flog.info("Extracted Parameters:")
  flog.info("  Parameter 1: %s", parameter_1)
  flog.info("  Parameter 2: %s", parameter_2)
  flog.info("  Parameter 3: %s", parameter_3)
  flog.info("  Parameter 4: %s", parameter_4)
  flog.info("  Parameter 5: %s", parameter_5)

  # Perform actions based on the parameters
  flog.info("Performing actions based on the configuration...")

  # Example: Conditional logic based on a boolean parameter
  if (parameter_4) {
    flog.info("Boolean parameter is true, taking appropriate action.")
  }

  # Example: Simulating action based on a parameter
  if (!is.null(parameter_3)) {
    flog.info("Simulating action with parameter 3: %s", parameter_3)
  }

  flog.info("Configuration evaluation completed successfully.")
}

# Script entry point
if (!interactive()) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) != 1) {
    flog.error("Usage: Rscript %s <config.json>", commandArgs()[1])
    stop("Invalid number of arguments.")
  }

  config_file_path <- args[1]
  tryCatch(
    main(config_file_path),
    error = function(e) {
      flog.error("Script terminated with error: %s", e$message)
      quit(status = 1)
    }
  )
}
