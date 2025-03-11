import os
import json
import logging
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, send_from_directory
from ..config import DOMAuditorConfig
from ..core.scanner import DOMScanner
from ..core.report import ReportGenerator

logger = logging.getLogger(__name__)

class GUIServer:
    def __init__(self, config: DOMAuditorConfig = None):
        """Initialize the GUI server with optional configuration."""
        if config is None:
            self.config = DOMAuditorConfig()
        else:
            self.config = config
        
        self.app = Flask(
            __name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static')
        )
        
        self._register_routes()
    
    def _register_routes(self):
        """Register Flask routes for the application."""
        app = self.app
        
        @app.route('/')
        def index():
            """Render the main page."""
            return render_template('index.html')
        
        @app.route('/scan', methods=['POST'])
        def scan():
            """Handle scan requests from the frontend."""
            try:
                data = request.json
                
                # Update configuration with request data
                self.config.scan_directory = data.get('directory', '')
                self.config.recursive = data.get('recursive', True)
                self.config.output_format = data.get('format', 'json')
                
                # Validate the directory
                if not os.path.isdir(self.config.scan_directory):
                    return jsonify({
                        'success': False,
                        'error': f"Directory not found: {self.config.scan_directory}"
                    }), 400
                
                # Perform the scan
                scanner = DOMScanner(self.config)
                scan_results = scanner.scan()
                
                # Generate a report
                reporter = ReportGenerator(self.config)
                report = reporter.generate(scan_results)
                
                if self.config.output_format == 'json':
                    # For JSON, we already have a dict to return
                    return jsonify({
                        'success': True,
                        'results': scan_results
                    })
                else:
                    # For other formats (HTML, console), return the string report
                    return jsonify({
                        'success': True,
                        'results': {
                            'report': report,
                            'format': self.config.output_format
                        }
                    })
            
            except Exception as e:
                logger.exception(f"Error during scan: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @app.route('/config', methods=['GET', 'POST'])
        def config_handler():
            """Get or update configuration."""
            if request.method == 'GET':
                return jsonify({
                    'success': True,
                    'config': {k: v for k, v in self.config.__dict__.items()}
                })
            else:  # POST
                try:
                    data = request.json
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
                    
                    return jsonify({
                        'success': True,
                        'config': {k: v for k, v in self.config.__dict__.items()}
                    })
                except Exception as e:
                    logger.exception(f"Error updating config: {e}")
                    return jsonify({
                        'success': False,
                        'error': str(e)
                    }), 500
    
    def run(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """Run the Flask application."""
        logger.info(f"Starting DOM Auditor GUI server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def start_gui_server(config_path: Optional[str] = None, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
    """Start the GUI server with the given configuration."""
    config = None
    if config_path and os.path.exists(config_path):
        config = DOMAuditorConfig.from_file(config_path)
    
    server = GUIServer(config)
    server.run(host, port, debug)