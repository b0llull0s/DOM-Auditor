import os
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


@dataclass
class DOMAuditorConfig:
    scan_directory: str = ""
    output_format: str = "console"  # console, json, html
    recursive: bool = True
    js_patterns: Dict[str, str] = field(default_factory=lambda: {
        'innerHTML': r'\.innerHTML\s*=\s*',
        'eval': r'eval\s*\(',
        'setTimeout': r'setTimeout\s*\(',
        'setInterval': r'setInterval\s*\(',
    })
    safe_functions: Set[str] = field(default_factory=lambda: {
        'encodeURIComponent', 
        'escapeHTML'
    })
    log_level: str = "INFO"
    output_file: Optional[str] = None
    
    @classmethod
    def from_file(cls, config_path: str) -> 'DOMAuditorConfig':
        """Load configuration from a JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
            print(f"Error loading config: {e}")
            return cls()
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to a JSON file."""
        config_dict = {k: v for k, v in self.__dict__.items()}
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2)
