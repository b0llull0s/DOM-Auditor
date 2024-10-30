import os
import glob
import re
import json
import subprocess
from bs4 import BeautifulSoup

# Parse HTML and find id/name attributes
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    ids = [tag.get('id') for tag in soup.find_all(id=True)]
    names = [tag.get('name') for tag in soup.find_all(name=True) if tag.get('name')]
    # Find inline event handlers
    inline_events = []
    for tag in soup.find_all():
        for attr in tag.attrs:
            if attr.startswith('on'):
                inline_events.append((tag.name, attr, tag[attr]))

    return ids, names, inline_events

# Invoke Esprima
def parse_js_ast(js_content):
    try:
        with open('temp.js', 'w', encoding='utf-8') as temp_js:
            temp_js.write(js_content)
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

# Track the flow of user input data
def track_user_input_flow(ast, html_ids):
    vulnerabilities = []
    user_input_vars = set() 
    # Helper to check if an expression is sanitized
    def is_sanitized(expr):
        # Add known safe functions here
        safe_functions = {'encodeURIComponent', 'escapeHTML'}
        return (expr['type'] == 'CallExpression' and 
                expr['callee']['type'] == 'Identifier' and 
                expr['callee']['name'] in safe_functions)
    for node in ast['body']: 
        if node['type'] == 'VariableDeclaration':
            for decl in node['declarations']:
                if decl['init'] and decl['init']['type'] == 'CallExpression': 
                    if (decl['init']['callee']['type'] == 'MemberExpression' and 
                        decl['init']['callee']['object']['name'] in {'document', 'location'}):
                        user_input_vars.add(decl['id']['name'])
                            
    for node in ast['body']:
        if (node['type'] == 'ExpressionStatement' and 
            node['expression']['type'] == 'AssignmentExpression'):
            left = node['expression']['left']
            right = node['expression']['right']

            if (left['type'] == 'MemberExpression' and 
                left['property']['name'] == 'innerHTML'):
                
                if (right['type'] == 'Identifier' and 
                    right['name'] in user_input_vars and 
                    not is_sanitized(right)):
                    vulnerabilities.append(f"Potential XSS: unsanitized user input assigned to innerHTML at position {node['range']}.")

    return vulnerabilities


# Analyze JS using AST for dangerous patterns
def analyze_js_ast(js_file, html_ids):
    with open(js_file, 'r', encoding='utf-8') as file:
        js_content = file.read()
    ast = parse_js_ast(js_content)
    if not ast:
        print(f"Could not analyze {js_file}")
        return

    vulnerabilities = track_user_input_flow(ast, html_ids)

    print(f"----- Analyzing JS file (AST): {js_file} -----")
    if vulnerabilities:
        for vuln in vulnerabilities:
            print(vuln)
    else:
        print("No unsafe input-to-DOM patterns detected.")

# Parse JavaScript code to detect vulnerabilities via regex
def parse_javascript(js_content, html_ids):
    patterns = {
        'innerHTML': r'\.innerHTML\s*=\s*',
        'eval': r'eval\s*\(',
        'setTimeout': r'setTimeout\s*\(',
        'setInterval': r'setInterval\s*\(',
    }

    vulnerabilities = {}
    for issue, pattern in patterns.items():
        if re.search(pattern, js_content):
            vulnerabilities[issue] = re.findall(pattern, js_content)

    # Look for potential DOM clobbering
    variables = re.findall(r'var\s+(\w+)\s*=', js_content)
    dom_clobbering = set(variables) & set(html_ids)

    return vulnerabilities, dom_clobbering

# Scan a single HTML file
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

    analyze_js_ast(js_file, html_ids)

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

# Scan all files in a folder
def analyze_folder(folder):
    html_files = glob.glob(os.path.join(folder, '**', '*.html'), recursive=True)
    js_files = glob.glob(os.path.join(folder, '**', '*.js'), recursive=True)

    print(f"\nFound {len(html_files)} HTML files and {len(js_files)} JS files in '{folder}'\n")

    all_html_ids = []
    for html_file in html_files:
        html_ids = analyze_html_file(html_file)
        all_html_ids.extend(html_ids)  
    
    for js_file in js_files:
        analyze_js_file(js_file, all_html_ids)

# Directory to analize 
folder_to_scan = '/home/b0llull0s/Documents/Projects/The_Odin_Project/odin-recipes'
analyze_folder(folder_to_scan)
