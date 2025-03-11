import os
import glob
from typing import List, Tuple, Set


def find_files(directory: str, extensions: List[str], recursive: bool = True) -> List[str]:
    """Find all files with the given extensions in the directory."""
    files = []
    for ext in extensions:
        if recursive:
            pattern = os.path.join(directory, '**', f'*.{ext}')
            files.extend(glob.glob(pattern, recursive=True))
        else:
            pattern = os.path.join(directory, f'*.{ext}')
            files.extend(glob.glob(pattern))
    return files


def read_file(file_path: str) -> str:
    """Read and return the content of a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Write content to a file, creating directories if needed."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_temp_file(content: str, filename: str = 'temp.js') -> str:
    """Create a temporary file with the given content and return its path."""
    path = os.path.join(os.getcwd(), filename)
    write_file(path, content)
    return path