import sys
from .cli import run_cli
from .utils.logging_utils import setup_logger

def main():
    """Main entry point for the application."""
    # Setup basic logging
    logger = setup_logger("dom_auditor")
    
    try:
        exit_code = run_cli()
        sys.exit(exit_code)
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
