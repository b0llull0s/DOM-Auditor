import argparse
import sys
import os
from typing import List, Optional
import logging
from .config import DOMAuditorConfig
from .core.scanner import DOMScanner
from .core.report import ReportGenerator
from .utils.logging_utils import setup_logger


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DOM Auditor - A tool for analyzing DOM-based vulnerabilities"
    )
    
    parser.add_argument(
        "-d", "--directory",
        help="Directory to scan for HTML and JS files",
        required=False
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file",
        default="dom_auditor_config.json"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file for the report",
        required=False
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["console", "json", "html"],
        default="console",
        help="Output format for the report"
    )
    
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Disable recursive directory scanning"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file path",
        required=False
    )
    
    return parser.parse_args(args)


def run_cli() -> int:
    """Main CLI entrypoint for DOM Auditor."""
    args = parse_args()
    
    # Set up logging
    logger = setup_logger("dom_auditor", args.log_level, args.log_file)
    
    try:
        # Load or create configuration
        config = DOMAuditorConfig()
        if os.path.exists(args.config):
            config = DOMAuditorConfig.from_file(args.config)
            logger.info(f"Loaded configuration from {args.config}")
        
        # Override config with command-line arguments
        if args.directory:
            config.scan_directory = args.directory
        if args.output:
            config.output_file = args.output
        if args.format:
            config.output_format = args.format
        if args.no_recursive:
            config.recursive = False
        config.log_level = args.log_level
        
        # Ensure we have a directory to scan
        if not config.scan_directory:
            logger.error("No directory specified for scanning")
            print("Error: No directory specified for scanning. Use --directory or set in config file.")
            return 1
        
        # Run the scanner
        scanner = DOMScanner(config)
        scan_results = scanner.scan()
        
        # Generate and output the report
        reporter = ReportGenerator(config)
        report = reporter.generate(scan_results)
        
        # Save to file if specified, otherwise print to console
        if config.output_file:
            reporter.save(report)
        else:
            print(report)
        
        return 0
        
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        print(f"Error: {e}")
        return 1