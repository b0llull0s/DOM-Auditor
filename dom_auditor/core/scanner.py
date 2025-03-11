import os
import logging
from typing import Dict, List, Any, Set
from ..utils.file_utils import find_files
from ..analyzers.html_analyzer import HTMLAnalyzer
from ..analyzers.js_analyzer import JSAnalyzer
from ..analyzers.ast_analyzer import ASTAnalyzer

logger = logging.getLogger(__name__)


class DOMScanner:
    def __init__(self, config):
        self.config = config
        self.html_analyzer = HTMLAnalyzer(config)
        self.js_analyzer = JSAnalyzer(config)
        self.ast_analyzer = ASTAnalyzer(config)
    
    def scan(self) -> Dict[str, Any]:
        """Scan the specified directory for DOM vulnerabilities."""
        directory = self.config.scan_directory
        recursive = self.config.recursive
        
        logger.info(f"Starting scan of directory: {directory} (recursive={recursive})")
        
        html_files = find_files(directory, ['html', 'htm'], recursive)
        js_files = find_files(directory, ['js'], recursive)
        
        logger.info(f"Found {len(html_files)} HTML files and {len(js_files)} JS files in '{directory}'")
        
        html_results = self._analyze_html_files(html_files)
        
        # Extract all HTML IDs for use in JS analysis
        all_html_ids = []
        for result in html_results:
            all_html_ids.extend(result['ids'])
        
        js_regex_results = self._analyze_js_files_regex(js_files, all_html_ids)
        js_ast_results = self._analyze_js_files_ast(js_files, all_html_ids)
        
        scan_results = {
            'directory': directory,
            'html_files': len(html_files),
            'js_files': len(js_files),
            'html_results': html_results,
            'js_regex_results': js_regex_results,
            'js_ast_results': js_ast_results
        }
        
        logger.info(f"Scan completed for {directory}")
        return scan_results
    
    def _analyze_html_files(self, html_files: List[str]) -> List[Dict]:
        """Analyze all HTML files and return results."""
        results = []
        for html_file in html_files:
            result = self.html_analyzer.analyze_file(html_file)
            results.append(result)
        return results
    
    def _analyze_js_files_regex(self, js_files: List[str], html_ids: List[str]) -> List[Dict]:
        """Analyze all JS files using regex-based approach."""
        results = []
        for js_file in js_files:
            result = self.js_analyzer.analyze_file(js_file, html_ids)
            results.append(result)
        return results
    
    def _analyze_js_files_ast(self, js_files: List[str], html_ids: List[str]) -> List[Dict]:
        """Analyze all JS files using AST-based approach."""
        results = []
        for js_file in js_files:
            result = self.ast_analyzer.analyze_file(js_file, html_ids)
            results.append(result)
        return results