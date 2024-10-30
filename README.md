# DOM-Auditor

**DOM-Auditor** is a security auditing tool designed to detect potential vulnerabilities in your web application by scanning HTML and JavaScript files. It uses **AST (Abstract Syntax Tree)** for deep JavaScript analysis and **regex-based checks** to identify common dangerous patterns and potential DOM clobbering issues. The tool can help developers identify issues related to DOM manipulation, XSS (Cross-Site Scripting), and unsafe user input handling.

## Current Features

1. **ID and Name Attribute Extraction**: Extracts IDs and names from HTML files.
2. **Inline Event Handler Detection**: Detects inline event handlers.
3. **AST-based Analysis**: Deep analysis of JavaScript files using AST to find unsafe assignments and track user input flow.
4. **Regex-based Detection**: Identifies patterns such as `eval()`, `innerHTML`, `setTimeout()`, etc.
5. **DOM Clobbering Detection**: Detects variable clashes between JS and HTML files.
6. **Recursive Scanning**: Supports scanning an entire folder for `.html` and `.js` files.
  
## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/b0llull0s/DOM-Auditor
   ```

2. **Install Dependencies:**

   Ensure you have **Node.js** installed. Then, install the necessary Node.js package (Esprima) for AST parsing:

   ```bash
   npm install esprima
   ```

3. **Run the Tool:**

   You can run the tool on any folder containing your HTML and JS files by executing the following commands:

   ```bash
   # Make sure to give executable permissions
   chmod +x DOM-Auditor.py
   # Run it
   python3 DOM-Auditor.py
   ```
> [!important]
> Make sure to set the correct folder path in the script for analysis.

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
