# DOM-Auditor

DOM-Auditor is a tool for scanning and analyzing HTML and JavaScript files for DOM-based vulnerabilities. It provides both a command-line interface and a web-based GUI for analyzing web applications.

## Features

- Static analysis of HTML and JavaScript files
- Detection of common DOM-based vulnerabilities
- Interactive web GUI for visualizing results
- Modular design for easy extension

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installing from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/b0llull0s/DOM-Auditor.git
   cd DOM-Auditor
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Project Structure

The project follows a standard Python package structure:

```
DOM-Auditor/
├── dom_auditor/             # Main package directory
│   ├── __init__.py
│   ├── main.py              # Main entry point
│   ├── cli.py               # Command-line interface
│   ├── config.py            # Configuration settings
│   ├── analyzers/           # Analysis modules
│   │   ├── __init__.py
│   │   ├── ast_analyzer.py
│   │   ├── html_analyzer.py
│   │   └── js_analyzer.py
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── report.py
│   │   └── scanner.py
│   ├── gui/                 # Web GUI components
│   │   ├── __init__.py
│   │   ├── server.py
│   │   ├── static/
│   │   └── templates/
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── data_utils.py
│       ├── file_utils.py
│       ├── logging_utils.py
│       └── network_utils.py
├── setup.py                 # Package installation configuration
├── MANIFEST.in              # Package data inclusion
├── LICENSE
└── README.md
```

## Usage

### Command-line Interface

After installation, you can use the command-line tool:

```bash
# Show help and available commands
dom-auditor --help

# Scan a single file
dom-auditor scan --file path/to/file.html

# Scan a directory
dom-auditor scan --dir path/to/directory

# Scan a website (requires network access)
dom-auditor scan --url https://example.com
```

### Web GUI

To start the web-based interface:

```bash
dom-auditor-gui
```

Then open your browser and navigate to `http://localhost:5000` (default port).

## Development

### Dependencies

The project requires the following main dependencies:
- beautifulsoup4 - For HTML parsing
- requests - For HTTP requests
- flask - For the web GUI
- esprima - For JavaScript parsing
- lxml - For advanced HTML parsing
- colorama - For colored terminal output
- jinja2 - For templating in the GUI

### Testing

You can test the installation with:

```bash
# Test command-line interface
dom-auditor --version

# Test basic scanning functionality
dom-auditor scan --test

# Test GUI server startup
dom-auditor-gui --test
```

To run the unit tests (if available):

```bash
# Using pytest (if implemented)
pytest
```

### Common Issues

If you encounter the error "No module named 'dom_auditor'", ensure:
1. You have the correct directory structure with dom_auditor as the main package
2. All subdirectories have `__init__.py` files
3. The package is properly installed with `pip install -e .`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Possible Improvements

### 1. **Advanced Data Flow Analysis**
   - Improve user input tracking by identifying all possible sources of user input (`document.getElementById()`, `window.location`, etc.) and tracing its path through the application.
   - Implement a taint-tracking system to ensure the tool can handle more complex cases of data flow across multiple functions and files.

### 2. **Handling Minified/Obfuscated Code**
   - Add support for de-obfuscating or prettifying minified or obfuscated JavaScript to improve detection accuracy.

### 3. **Extending to Other Vulnerabilities**
   - Add checks for other common vulnerabilities like SQL Injection patterns or SSRF (Server-Side Request Forgery).

### 4. **Support for More JavaScript Features**
   - Improve support for modern JavaScript features (e.g., `async/await`, `arrow functions`, etc.).
   - Detect issues specific to modern frameworks (e.g., React, Vue, Angular).
