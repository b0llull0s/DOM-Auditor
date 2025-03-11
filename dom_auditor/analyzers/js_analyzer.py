import re
import logging
from typing import Dict, Set, List, Tuple

logger = logging.getLogger(__name__)


class JSAnalyzer:
    def __init__(self, config):
        self.config = config
        self.patterns = config.js_patterns
    
    def analyze_file(self, js_file: str, html_ids: List[str] = None) -> Dict:
        """Analyze a JavaScript file using regex patterns and return findings."""
        if html_ids is None:
            html_ids = []
        
        try:
            logger.info(f"Analyzing JS file (regex): {js_file}")
            js_content = self._read_file(js_file)
            return self.analyze_content(js_content, html_ids, js_file)
        except Exception as e:
            logger.error(f"Error analyzing JS file {js_file}: {e}")
            return {
                "file": js_file,
                "vulnerabilities": {},
                "dom_clobbering": [],
                "error": str(e)
            }
    
    def analyze_content(self, js_content: str, html_ids: List[str], source: str = "") -> Dict:
        """Analyze JavaScript content and return findings."""
        vulnerabilities, dom_clobbering = self._parse_javascript(js_content, html_ids)
        
        results = {
            "file": source,
            "vulnerabilities": vulnerabilities,
            "dom_clobbering": list(dom_clobbering)
        }
        
        logger.debug(f"JS analysis results for {source}: {len(vulnerabilities)} vulnerabilities, {len(dom_clobbering)} dom clobbering issues")
        return results
    
    def _read_file(self, file_path: str) -> str:
        """Read file content."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _parse_javascript(self, js_content: str, html_ids: List[str]) -> Tuple[Dict[str, List[str]], Set[str]]:
        """Parse JavaScript code using regex to detect vulnerabilities."""
        vulnerabilities = {}
        for issue, pattern in self.patterns.items():
            matches = re.findall(pattern, js_content)
            if matches:
                vulnerabilities[issue] = matches
        
        # Look for potential DOM clobbering
        variables = re.findall(r'var\s+(\w+)\s*=', js_content)
        dom_clobbering = set(variables) & set(html_ids)
        
        return vulnerabilities, dom_clobbering