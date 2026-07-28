#!/bin/bash
set -e

# Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "uv not found. Install it: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Create/sync the venv (.venv) from pyproject.toml + uv.lock
echo "Syncing virtual environment..."
uv sync

# Upgrade all dependencies to their latest compatible versions
echo "Upgrading all dependencies..."
uv lock --upgrade

# Re-sync the venv with the updated lockfile
echo "Installing upgraded dependencies..."
uv sync

echo "Updates complete! uv.lock has been updated."
echo "Commit uv.lock so future Docker builds use these versions."
exit 0
        pip3 install "$pkg_name" --upgrade
    done < "$REQUIREMENTS_FILE"

    # Now reset it
    rm -r requirements.txt
    pip3 freeze >> requirements.txt
done

# Final dependency check
echo "Running final pip check..."
if ! pip check; then
    echo "pip check failed — exiting with error."
    exit 3  # exit code signaling dependency issues
fi

echo "Updates Complete!"
exit 0
