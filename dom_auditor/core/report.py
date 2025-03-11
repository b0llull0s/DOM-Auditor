import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self, config):
        self.config = config
    
    def generate(self, scan_results: Dict[str, Any]) -> str:
        """Generate a report from scan results in the specified format."""
        output_format = self.config.output_format.lower()
        
        if output_format == 'json':
            return self._generate_json(scan_results)
        elif output_format == 'html':
            return self._generate_html(scan_results)
        else:  # Default to console format
            return self._generate_console(scan_results)
    
    def save(self, report_content: str) -> None:
        """Save the report to a file if output_file is specified."""
        output_file = self.config.output_file
        if not output_file:
            return
        
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving report to {output_file}: {e}")
    
    def _generate_json(self, scan_results: Dict[str, Any]) -> str:
        """Generate a JSON report."""
        return json.dumps(scan_results, indent=2)
    
    def _generate_html(self, scan_results: Dict[str, Any]) -> str:
        """Generate an HTML report."""
        # This is a simple HTML template - for a real implementation,
        # you might want to use a proper template engine
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>DOM Auditor Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2, h3 { color: #333; }
                .container { max-width: 1200px; margin: 0 auto; }
                .section { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
                .file { margin-bottom: 15px; padding: 10px; background-color: #f8f8f8; }
                .vulnerability { color: red; }
                .safe { color: green; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>DOM Auditor Report</h1>
                <div class="summary section">
                    <h2>Summary</h2>
                    <p>Directory: {directory}</p>
                    <p>HTML Files: {html_count}</p>
                    <p>JS Files: {js_count}</p>
                </div>
        """.format(
            directory=scan_results['directory'],
            html_count=scan_results['html_files'],
            js_count=scan_results['js_files']
        )
        
        # HTML Results Section
        html += """
                <div class="html-results section">
                    <h2>HTML Analysis Results</h2>
        """
        
        for result in scan_results['html_results']:
            html += """
                    <div class="file">
                        <h3>File: {file}</h3>
                        <h4>IDs:</h4>
                        <p>{ids}</p>
                        <h4>Names:</h4>
                        <p>{names}</p>
                        <h4>Inline Events:</h4>
                        <ul>
            """.format(
                file=result['file'],
                ids=', '.join(result['ids']) if result['ids'] else 'None',
                names=', '.join(result['names']) if result['names'] else 'None'
            )
            
            if result['inline_events']:
                for tag, attr, val in result['inline_events']:
                    html += f"<li>&lt;{tag}&gt; - {attr} = {val}</li>"
            else:
                html += "<li>None</li>"
            
            html += """
                        </ul>
                    </div>
            """
        
        html += """
                </div>
        """
        
        # JS Regex Results Section
        html += """
                <div class="js-regex-results section">
                    <h2>JavaScript Regex Analysis Results</h2>
        """
        
        for result in scan_results['js_regex_results']:
            html += """
                    <div class="file">
                        <h3>File: {file}</h3>
                        <h4>Vulnerabilities:</h4>
            """.format(file=result['file'])
            
            if result['vulnerabilities']:
                html += "<ul>"
                for issue, occurrences in result['vulnerabilities'].items():
                    html += f"<li class='vulnerability'>{issue}: {len(occurrences)} occurrence(s)</li>"
                html += "</ul>"
            else:
                html += "<p class='safe'>No vulnerabilities detected</p>"
            
            html += """
                        <h4>DOM Clobbering:</h4>
            """
            
            if result['dom_clobbering']:
                html += "<ul>"
                for issue in result['dom_clobbering']:
                    html += f"<li class='vulnerability'>{issue}</li>"
                html += "</ul>"
            else:
                html += "<p class='safe'>No DOM clobbering issues detected</p>"
            
            html += """
                    </div>
            """
        
        html += """
                </div>
        """
        
        # JS AST Results Section
        html += """
                <div class="js-ast-results section">
                    <h2>JavaScript AST Analysis Results</h2>
        """
        
        for result in scan_results['js_ast_results']:
            html += """
                    <div class="file">
                        <h3>File: {file}</h3>
                        <h4>Vulnerabilities:</h4>
            """.format(file=result['file'])
            
            if result.get('vulnerabilities'):
                html += "<ul>"
                for vuln in result['vulnerabilities']:
                    html += f"<li class='vulnerability'>{vuln}</li>"
                html += "</ul>"
            else:
                html += "<p class='safe'>No vulnerabilities detected</p>"
            
            html += """
                    </div>
            """
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_console(self, scan_results: Dict[str, Any]) -> str:
        """Generate a console-friendly text report."""
        report = []
        
        # Summary section
        report.append("=" * 80)
        report.append(f"DOM AUDITOR REPORT")
        report.append("=" * 80)
        report.append(f"Directory: {scan_results['directory']}")
        report.append(f"HTML Files: {scan_results['html_files']}")
        report.append(f"JS Files: {scan_results['js_files']}")
        report.append("")
        
        # HTML Results
        report.append("=" * 80)
        report.append("HTML ANALYSIS RESULTS")
        report.append("=" * 80)
        
        for result in scan_results['html_results']:
            report.append(f"File: {result['file']}")
            report.append(f"IDs: {', '.join(result['ids']) if result['ids'] else 'None'}")
            report.append(f"Names: {', '.join(result['names']) if result['names'] else 'None'}")
            
            report.append("Inline Events:")
            if result['inline_events']:
                for tag, attr, val in result['inline_events']:
                    report.append(f"  <{tag}> - {attr} = {val}")
            else:
                report.append("  None")
            
            report.append("-" * 80)
        
        # JS Regex Results
        report.append("")
        report.append("=" * 80)
        report.append("JAVASCRIPT REGEX ANALYSIS RESULTS")
        report.append("=" * 80)
        
        for result in scan_results['js_regex_results']:
            report.append(f"File: {result['file']}")
            
            report.append("Vulnerabilities:")
            if result['vulnerabilities']:
                for issue, occurrences in result['vulnerabilities'].items():
                    report.append(f"  {issue}: {len(occurrences)} occurrence(s)")
            else:
                report.append("  No vulnerabilities detected")
            
            report.append("DOM Clobbering:")
            if result['dom_clobbering']:
                for issue in result['dom_clobbering']:
                    report.append(f"  {issue}")
            else:
                report.append("  No DOM clobbering issues detected")
            
            report.append("-" * 80)
        
        # JS AST Results
        report.append("")
        report.append("=" * 80)
        report.append("JAVASCRIPT AST ANALYSIS RESULTS")
        report.append("=" * 80)
        
        for result in scan_results['js_ast_results']:
            report.append(f"File: {result['file']}")
            
            report.append("Vulnerabilities:")
            if result.get('vulnerabilities'):
                for vuln in result['vulnerabilities']:
                    report.append(f"  {vuln}")
            else:
                report.append("  No vulnerabilities detected")
            
            report.append("-" * 80)
        
        return "\n".join(report)
