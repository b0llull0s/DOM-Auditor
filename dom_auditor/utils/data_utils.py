import json
from typing import Dict, List, Any, Union
import csv
import xml.etree.ElementTree as ET
import xml.dom.minidom

def convert_to_json(data: Any) -> str:
    """Convert data structure to JSON string."""
    return json.dumps(data, indent=2)

def load_json(json_str: str) -> Any:
    """Load data from JSON string."""
    return json.loads(json_str)

def convert_to_csv(data: List[Dict[str, Any]], headers: List[str] = None) -> str:
    """Convert list of dictionaries to CSV format."""
    if not data:
        return ""
    
    if not headers:
        headers = list(data[0].keys())
    
    result = []
    result.append(",".join(headers))
    
    for row in data:
        csv_row = []
        for header in headers:
            value = row.get(header, "")
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            csv_row.append(f'"{value}"' if ',' in str(value) else str(value))
        result.append(",".join(csv_row))
    
    return "\n".join(result)

def convert_to_xml(data: Dict[str, Any], root_name: str = "root") -> str:
    """Convert dictionary to XML format."""
    def _dict_to_xml(data, parent):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    sub_elem = ET.SubElement(parent, key)
                    _dict_to_xml(value, sub_elem)
                else:
                    sub_elem = ET.SubElement(parent, key)
                    sub_elem.text = str(value)
        elif isinstance(data, list):
            for item in data:
                item_elem = ET.SubElement(parent, "item")
                _dict_to_xml(item, item_elem)
        else:
            parent.text = str(data)
    
    root = ET.Element(root_name)
    _dict_to_xml(data, root)
    
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def merge_data(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple data dictionaries into one."""
    result = {}
    for data in data_list:
        for key, value in data.items():
            if key in result:
                if isinstance(result[key], list) and isinstance(value, list):
                    result[key].extend(value)
                elif isinstance(result[key], dict) and isinstance(value, dict):
                    result[key].update(value)
                else:
                    # Convert to list if not already
                    if not isinstance(result[key], list):
                        result[key] = [result[key]]
                    if not isinstance(value, list):
                        value = [value]
                    result[key].extend(value)
            else:
                result[key] = value
    return result

