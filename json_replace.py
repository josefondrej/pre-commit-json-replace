#!/usr/bin/env python3

import argparse
import json
import os
import glob
import yaml
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Replace values in JSON files')
    parser.add_argument('--direction', choices=['to_committed', 'to_working'],
                        required=True, help='Direction of replacement')
    parser.add_argument('--config', required=True, help='Path to config file')
    return parser.parse_args()


def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def find_json_files(pattern):
    """Find JSON files matching the given pattern."""
    return glob.glob(pattern, recursive=True)


def replace_in_json(file_path, keys, direction, indent=2):
    """Replace values in a JSON file according to the direction."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        return False
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
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
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        print(f"Modified: {file_path}")

    return modified


def process_files(config, direction):
    """Process all files according to the configuration."""
    modified_files = 0

    for pattern_config in config.get('patterns', []):
        path_pattern = pattern_config['path']
        keys = pattern_config['keys']
        indent = pattern_config.get('indent', 2)

        for file_path in find_json_files(path_pattern):
            if replace_in_json(file_path, keys, direction, indent):
                modified_files += 1

    return modified_files


def main():
    """Main entry point."""
    args = parse_args()
    config = load_config(args.config)
    modified_files = process_files(config, args.direction)
    print(f"Modified {modified_files} files")
    return 0


if __name__ == "__main__":
    exit(main())
