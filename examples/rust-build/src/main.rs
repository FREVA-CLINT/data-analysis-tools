use std::env;
use std::fs::File;
use std::io::Read;
use serde_json::Value;
use log::{info, error};

fn main() {
    // Initialize logging
    env_logger::init();

    // Get the configuration file path from the command-line arguments
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        error!("Usage: {} <config.json>", args[0]);
        std::process::exit(1);
    }
    let config_file = &args[1];

    // Read and parse the configuration JSON file
    let config = match load_config(config_file) {
        Ok(config) => config,
        Err(e) => {
            error!("Failed to load configuration: {}", e);
            std::process::exit(1);
        }
    };

    // Assign a long-lived default value
    let default_parameter_1 = Value::String("default_value".to_string());
    let parameter_1 = config.get("parameter_1").unwrap_or(&default_parameter_1);

    let parameter_2 = config.get("parameter_2");

    // Check mandatory parameter
    if parameter_2.is_none() {
        error!("Error: 'parameter_2' is mandatory but is not provided.");
        std::process::exit(1);
    }

    // Log extracted parameters
    info!("Parameter 1: {}", parameter_1);
    info!("Parameter 2: {}", parameter_2.unwrap());

    // Perform actions based on the parameters
    info!("Performing actions based on the configuration...");
    // Add logic for processing parameters

    info!("Configuration evaluation completed successfully.");
}

fn load_config(config_file: &str) -> Result<Value, Box<dyn std::error::Error>> {
    let mut file = File::open(config_file)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    let json: Value = serde_json::from_str(&contents)?;
    Ok(json)
}
