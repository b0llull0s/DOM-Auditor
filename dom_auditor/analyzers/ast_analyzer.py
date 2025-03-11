import json
import subprocess
import logging
import os
from typing import Dict, List, Any, Optional, Set

logger = logging.getLogger(__name__)


class ASTAnalyzer:
    def __init__(self, config):
        self.config = config
        self.safe_functions = config.safe_functions
    
    def analyze_file(self, js_file: str, html_ids: List[str] = None) -> Dict:
        """Analyze a JavaScript file using AST and return findings."""
        if html_ids is None:
            html_ids = []
        
        try:
            logger.info(f"Analyzing JS file (AST): {js_file}")
            js_content = self._read_file(js_file)
            return self.analyze_content(js_content, html_ids, js_file)
        except Exception as e:
            logger.error(f"Error analyzing JS file {js_file} with AST: {e}")
            return {
                "file": js_file,
                "vulnerabilities": [],
                "error": str(e)
            }
    
    def analyze_content(self, js_content: str, html_ids: List[str], source: str = "") -> Dict:
        """Analyze JavaScript content using AST and return findings."""
        ast = self._parse_js_ast(js_content)
        if not ast:
            logger.warning(f"Could not generate AST for {source}")
            return {
                "file": source,
                "vulnerabilities": [],
                "error": "Failed to generate AST"
            }
        
        vulnerabilities = self._track_user_input_flow(ast, html_ids)
        
        results = {
            "file": source,
            "vulnerabilities": vulnerabilities
        }
        
        logger.debug(f"AST analysis results for {source}: {len(vulnerabilities)} vulnerabilities")
        return results
    
    def _read_file(self, file_path: str) -> str:
        """Read file content."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _parse_js_ast(self, js_content: str) -> Optional[Dict]:
        """Invoke Esprima to parse JavaScript and generate AST."""
        try:
            temp_js_path = 'temp.js'
            with open(temp_js_path, 'w', encoding='utf-8') as temp_js:
                temp_js.write(js_content)
            
            result = subprocess.run(['node', '-e',
                                     "const esprima = require('esprima');"
                                     "const fs = require('fs');"
                                     "const code = fs.readFileSync('temp.js', 'utf-8');"
                                     "try {"
                                     "  const ast = esprima.parseScript(code, {range: true});"
                                     "  console.log(JSON.stringify(ast, null, 2));"
                                     "} catch(e) {"
                                     "  console.error(e.message);"
                                     "  process.exit(1);"
                                     "}"],
                                     capture_output=True, text=True)
            
            os.remove(temp_js_path)
            
            if result.returncode != 0:
                logger.error(f"Esprima error: {result.stderr}")
                return None
            
            return json.loads(result.stdout)
        except Exception as e:
            logger.exception(f"Error parsing JavaScript via AST: {e}")
            return None
    
    def _is_sanitized(self, expr: Dict) -> bool:
        """Check if an expression is sanitized using safe functions."""
        try:
            return (expr['type'] == 'CallExpression' and 
                    expr['callee']['type'] == 'Identifier' and 
                    expr['callee']['name'] in self.safe_functions)
        except (KeyError, TypeError) as e:
            logger.debug(f"Error while checking sanitization: {e}")
            return False
    
    def _track_user_input_flow(self, ast: Dict, html_ids: List[str]) -> List[str]:
        """Track the flow of user input data through the AST."""
        vulnerabilities = []
        user_input_vars = set()
        
        try:
            # First pass: identify variables that contain user input
            for node in ast.get('body', []):
                if node.get('type') == 'VariableDeclaration':
                    for decl in node.get('declarations', []):
                        init = decl.get('init')
                        if init and init.get('type') == 'CallExpression':
                            callee = init.get('callee')
                            if (callee and callee.get('type') == 'MemberExpression' and 
                                callee.get('object') and callee['object'].get('name') in {'document', 'location'}):
                                user_input_vars.add(decl['id']['name'])
            
            # Second pass: find unsafe assignments using those variables
            for node in ast.get('body', []):
                if (node.get('type') == 'ExpressionStatement' and 
                    node.get('expression') and node['expression'].get('type') == 'AssignmentExpression'):
                    left = node['expression'].get('left')
                    right = node['expression'].get('right')
                    
                    if (left and left.get('type') == 'MemberExpression' and 
                        left.get('property') and left['property'].get('name') == 'innerHTML'):
                        
                        if (right and right.get('type') == 'Identifier' and 
                            right.get('name') in user_input_vars and 
                            not self._is_sanitized(right)):
                            vulnerabilities.append(f"Potential XSS: unsanitized user input assigned to innerHTML at position {node.get('range')}.")
        
        except Exception as e:
            logger.exception(f"Error during AST traversal: {e}")
        
        return vulnerabilities
