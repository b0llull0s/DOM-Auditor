from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Set
import logging

logger = logging.getLogger(__name__)


class HTMLAnalyzer:
    def __init__(self, config):
        self.config = config
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a single HTML file and return findings."""
        try:
            logger.info(f"Analyzing HTML file: {file_path}")
            content = self._read_file(file_path)
            return self.analyze_content(content, file_path)
        except Exception as e:
            logger.error(f"Error analyzing HTML file {file_path}: {e}")
            return {
                "file": file_path,
                "ids": [],
                "names": [],
                "inline_events": [],
                "error": str(e)
            }
    
    def analyze_content(self, html_content: str, source: str = "") -> Dict:
        """Analyze HTML content and return findings."""
        ids, names, inline_events = self._parse_html(html_content)
        
        results = {
            "file": source,
            "ids": ids,
            "names": names,
            "inline_events": inline_events
        }
        
        logger.debug(f"HTML analysis results for {source}: {len(ids)} IDs, {len(names)} names, {len(inline_events)} inline events")
        return results
    
    def _read_file(self, file_path: str) -> str:
        """Read file content."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _parse_html(self, html_content: str) -> Tuple[List[str], List[str], List[Tuple[str, str, str]]]:
        """Parse HTML and extract IDs, names, and inline event handlers."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract IDs
        ids = [tag.get('id') for tag in soup.find_all(id=True)]
        
        # Extract name attributes
        names = [tag.get('name') for tag in soup.find_all(name=True) if tag.get('name')]
        
        # Find inline event handlers
        inline_events = []
        for tag in soup.find_all():
            for attr in tag.attrs:
                if attr.startswith('on'):
                    inline_events.append((tag.name, attr, tag[attr]))
        
        return ids, names, inline_events
