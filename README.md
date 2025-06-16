# Pre-commit JSON Replace

A pre-commit hook that replaces values for specified keys in JSON files.

## Overview

This tool helps manage environment-specific values in JSON files within your Git repository. It automatically replaces values when committing to the repository and restores them when checking out, making it easier to work with configuration files that need different values in different environments.

## Use Cases

- Replace sensitive information (like connection strings) with placeholder values when committing to a repository
- Switch between development and production configurations automatically
- Maintain different values for local development vs. committed code

## Installation

### Prerequisites

- Python 3.8 or higher
- [pre-commit](https://pre-commit.com/) installed in your repository

### Install via pip

```bash
pip install pre-commit-json-replace
```

### Add to your pre-commit configuration

Add the following to your `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/josefondrej/pre-commit-json-replace
    rev: v0.1.0  # Use the latest version
    hooks:
      - id: json-replace-to-committed
      - id: json-replace-to-working
```

## Configuration

Create a `.json-replace-config.yaml` file in the root of your repository with the following structure:

```yaml
patterns:
  - path: "path/to/your/*.json"  # Glob pattern to match JSON files
    keys:
      - key: "nested.key.path"   # Dot-separated path to the key to replace
        working: "local-value"   # Value to use in working copy
        committed: "repo-value"  # Value to use in committed version
    indent: 2  # Optional: JSON indentation level (default: 2)

  # You can add multiple patterns
  - path: "another/path/*.json"
    keys:
      - key: "anotherKey"
        working: "development"
        committed: "production"
```

## How It Works

The tool provides two hooks:

1. **json-replace-to-committed**: Runs before committing files to replace working values with committed values
2. **json-replace-to-working**: Runs after checkout, commit, or merge to replace committed values with working values

### Example

Given a JSON file `config.json`:

```json
{
  "database": {
    "connectionString": "localhost:5432"
  }
}
```

And a configuration:

```yaml
patterns:
  - path: "config.json"
    keys:
      - key: "database.connectionString"
        working: "localhost:5432"
        committed: "SERVER:5432"
```

When committing, the file will be changed to:

```json
{
  "database": {
    "connectionString": "SERVER:5432"
  }
}
```

After checkout, it will be changed back to use `localhost:5432`.

## Command Line Usage

You can also run the tool manually:

```bash
# Replace working values with committed values
json-replace --direction to_committed --config=.json-replace-config.yaml

# Replace committed values with working values
json-replace --direction to_working --config=.json-replace-config.yaml
```

## License

See the [LICENSE](LICENSE) file for details.
