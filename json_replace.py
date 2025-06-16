#!/usr/bin/env python3
"""
JSON Replace Pre-commit Hook.

This module provides functionality to replace values in JSON files based on a configuration.
It can be used as a pre-commit hook to modify JSON files before committing them to a repository,
and to restore the original values after checkout.
"""

import argparse
import json
import glob
import sys
from typing import Dict, List, Any, Optional, Union, Tuple
import yaml


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.
            Contains 'direction' (str) and 'config' (str) attributes.
    """
    parser = argparse.ArgumentParser(description='Replace values in JSON files')
    parser.add_argument('--direction', choices=['to_committed', 'to_working'],
                        required=True, help='Direction of replacement')
    parser.add_argument('--config', required=True, help='Path to config file')
    return parser.parse_args()


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dict containing the parsed YAML configuration.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        yaml.YAMLError: If the configuration file is not valid YAML.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in configuration file '{config_path}': {e}")
        sys.exit(1)


def find_json_files(pattern: str) -> List[str]:
    """Find JSON files matching the given pattern.

    Args:
        pattern: Glob pattern to match JSON files.

    Returns:
        List of paths to matching JSON files.
    """
    return glob.glob(pattern, recursive=True)


def replace_in_json(file_path: str, keys: List[Dict[str, str]], direction: str, indent: int = 2) -> bool:
    """Replace values in a JSON file according to the direction.

    Args:
        file_path: Path to the JSON file to modify.
        keys: List of key configurations, each containing 'key', 'working', and 'committed' values.
        direction: Direction of replacement, either 'to_committed' or 'to_working'.
        indent: Number of spaces for indentation in the output JSON file.

    Returns:
        True if the file was modified, False otherwise.

    Raises:
        json.JSONDecodeError: If the file is not valid JSON (handled internally).
        FileNotFoundError: If the file is not found (handled internally).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        return False
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    modified = False
    for key_config in keys:
        key_path = key_config['key'].split('.')
        current = data

        # Navigate to the nested key
        for i, part in enumerate(key_path):
            if i == len(key_path) - 1:
                # We're at the final key
                if part in current:
                    if direction == 'to_committed' and current[part] == key_config['working']:
                        current[part] = key_config['committed']
                        modified = True
                    elif direction == 'to_working' and current[part] == key_config['committed']:
                        current[part] = key_config['working']
                        modified = True
            else:
                # Navigate deeper
                if part not in current or not isinstance(current[part], dict):
                    break
                current = current[part]

    if modified:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent)
            print(f"Modified: {file_path}")
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False

    return modified


def process_files(config: Dict[str, Any], direction: str) -> int:
    """Process all files according to the configuration.

    Args:
        config: Configuration dictionary loaded from YAML.
        direction: Direction of replacement, either 'to_committed' or 'to_working'.

    Returns:
        Number of files that were modified.
    """
    modified_files = 0

    for pattern_config in config.get('patterns', []):
        path_pattern = pattern_config['path']
        keys = pattern_config['keys']
        indent = pattern_config.get('indent', 2)

        for file_path in find_json_files(path_pattern):
            if replace_in_json(file_path, keys, direction, indent):
                modified_files += 1

    return modified_files


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    args = parse_args()
    config = load_config(args.config)
    modified_files = process_files(config, args.direction)
    print(f"Modified {modified_files} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
