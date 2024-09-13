import os
import glob
import re
import json
import subprocess
from bs4 import BeautifulSoup

# A function to parse HTML and find id/name attributes
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract all 'id' and 'name' attributes, ignoring None values
    ids = [tag.get('id') for tag in soup.find_all(id=True)]
    names = [tag.get('name') for tag in soup.find_all(name=True) if tag.get('name')]

    # Find inline event handlers (e.g., onclick, onmouseover)
    inline_events = []
    for tag in soup.find_all():
        for attr in tag.attrs:
            if attr.startswith('on'):
                inline_events.append((tag.name, attr, tag[attr]))

    return ids, names, inline_events


# A function to invoke Esprima via subprocess and parse JS into AST
def parse_js_ast(js_content):
    try:
        # Write the JavaScript content to a temporary file
        with open('temp.js', 'w', encoding='utf-8') as temp_js:
            temp_js.write(js_content)

        # Use subprocess to run Esprima from Node.js and output the AST as JSON
        result = subprocess.run(['node', '-e',
                                 "const esprima = require('esprima');"
                                 "const fs = require('fs');"
                                 "const code = fs.readFileSync('temp.js', 'utf-8');"
                                 "const ast = esprima.parseScript(code, {range: true});"
                                 "console.log(JSON.stringify(ast, null, 2));"],
                                 capture_output=True, text=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error parsing JavaScript via AST: {e}")
        return None

# A function to track the flow of user input data
def track_user_input_flow(ast, html_ids):
    vulnerabilities = []

    # Traverse AST to track assignments and detect dangerous uses
    for node in ast['body']:
        # Check for dangerous assignments (e.g., innerHTML = userInput)
        if node['type'] == 'ExpressionStatement' and node['expression']['type'] == 'AssignmentExpression':
            left = node['expression']['left']
            right = node['expression']['right']

            # Check if 'innerHTML' or other DOM properties are used
            if left['type'] == 'MemberExpression' and left['property']['name'] == 'innerHTML':
                # Check if the right side involves user input
                if right['type'] == 'Identifier' and right['name'] == 'userInput':
                    vulnerabilities.append(f"Potential XSS: innerHTML is assigned userInput at position {node['range']}.")

    return vulnerabilities

# A function to analyze JS using AST for dangerous patterns
def analyze_js_ast(js_file, html_ids):
    with open(js_file, 'r', encoding='utf-8') as file:
        js_content = file.read()

    # Parse JS into AST
    ast = parse_js_ast(js_content)
    if not ast:
        print(f"Could not analyze {js_file}")
        return

    # Track user input flow
    vulnerabilities = track_user_input_flow(ast, html_ids)

    print(f"----- Analyzing JS file (AST): {js_file} -----")
    if vulnerabilities:
        for vuln in vulnerabilities:
            print(vuln)
    else:
        print("No unsafe input-to-DOM patterns detected.")

# A function to parse JavaScript code to detect vulnerabilities via regex
def parse_javascript(js_content, html_ids):
    # Regex patterns for common issues
    patterns = {
        'innerHTML': r'\.innerHTML\s*=\s*',
        'eval': r'eval\s*\(',
        'setTimeout': r'setTimeout\s*\(',
        'setInterval': r'setInterval\s*\(',
    }

    vulnerabilities = {}

    # Search for each pattern in JavaScript content
    for issue, pattern in patterns.items():
        if re.search(pattern, js_content):
            vulnerabilities[issue] = re.findall(pattern, js_content)

    # Look for potential DOM clobbering
    variables = re.findall(r'var\s+(\w+)\s*=', js_content)
    dom_clobbering = set(variables) & set(html_ids)

    return vulnerabilities, dom_clobbering

# A function to scan a single HTML file
def analyze_html_file(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    html_ids, html_names, inline_events = parse_html(html_content)
    
    print(f"----- Analyzing HTML file: {html_file} -----")
    print(f"Found IDs: {html_ids}")
    print(f"Found Names: {html_names}")
    if inline_events:
        print("Found inline event handlers:")
        for tag, attr, val in inline_events:
            print(f"  Tag: <{tag}> Attribute: {attr} -> {val}")
    else:
        print("No inline event handlers found.")
    return html_ids

# A function to analyze JavaScript files (AST and regex)
def analyze_js_file(js_file, html_ids):
    with open(js_file, 'r', encoding='utf-8') as file:
        js_content = file.read()

    # Use AST analysis for user input flow and other dangerous patterns
    analyze_js_ast(js_file, html_ids)

    # Use regex analysis for clobbering and known patterns
    js_vulnerabilities, dom_clobbering = parse_javascript(js_content, html_ids)
    
    print(f"----- Analyzing JS file (Regex): {js_file} -----")
    if js_vulnerabilities:
        for issue, occurrences in js_vulnerabilities.items():
            print(f"Possible {issue} usage found {len(occurrences)} time(s).")
    else:
        print("No unsafe JavaScript patterns detected.")

    if dom_clobbering:
        print(f"Potential DOM clobbering detected: {dom_clobbering}")
    else:
        print("No DOM clobbering issues detected.")

# Function to scan all files in a folder
def analyze_folder(folder):
    # Get all HTML and JS files in the folder recursively
    html_files = glob.glob(os.path.join(folder, '**', '*.html'), recursive=True)
    js_files = glob.glob(os.path.join(folder, '**', '*.js'), recursive=True)

    print(f"\nFound {len(html_files)} HTML files and {len(js_files)} JS files in '{folder}'\n")

    # Analyze each HTML file and collect IDs
    all_html_ids = []
    for html_file in html_files:
        html_ids = analyze_html_file(html_file)
        all_html_ids.extend(html_ids)  # Collect IDs to check against JS files

    # Analyze each JS file
    for js_file in js_files:
        analyze_js_file(js_file, all_html_ids)

# Run the analysis on a directory
folder_to_scan = '/home/b0llull0s/Documents/Projects/The_Odin_Project/odin-recipes'  # Replace with the path of the folder you want to scan
analyze_folder(folder_to_scan)
