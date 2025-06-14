#!/usr/bin/env python3
"""
Version updater script using Fabric library.

Requirements:
    pip install fabric

Usage:
    fab update-version --current=1.0.0 --new=1.1.0
    fab check-versions
    fab run-bun
    fab list-deps
    fab update-deps
    fab show-outdated
    fab freeze-deps
    fab update-and-freeze
"""

import re
import sys
import tomllib
from pathlib import Path
from typing import Any

from fabric import Connection
from fabric import task
from invoke import run

# File update configurations
UPDATE_CONFIGS: list[dict[str, str]] = [
    {
        "file": "pyproject.toml",
        "pattern": 'version = "{current}"',
        "replacement": 'version = "{new}"',
        "description": "pyproject.toml version",
    },
    {
        "file": "Containerfiles/app/Containerfile",
        "pattern": 'LABEL version="{current}"',
        "replacement": 'LABEL version="{new}"',
        "description": "Containerfiles/app/Containerfile",
    },
    {
        "file": "Containerfiles/test/Containerfile",
        "pattern": 'LABEL version="{current}"',
        "replacement": 'LABEL version="{new}"',
        "description": "Containerfiles/test/Containerfile",
    },
    {
        "file": "src/config/settings.py",
        "pattern": 'APIFAIRY_VERSION = "{current}"',
        "replacement": 'APIFAIRY_VERSION = "{new}"',
        "description": "src/config/settings.py",
    },
]


def replace_in_file(config: dict[str, str], current_version: str, new_version: str) -> bool:
    """Replace version in file using fabric-style operations."""
    file_path = Path(config["file"])

    if not file_path.exists():
        print(f"Warning: {file_path} does not exist, skipping...")
        return False

    try:
        # Read current content
        content = file_path.read_text(encoding="UTF8")

        # Create the actual pattern and replacement strings
        search_pattern = config["pattern"].format(current=re.escape(current_version))
        replacement_text = config["replacement"].format(new=new_version)

        # Perform replacement
        new_content = re.sub(search_pattern, replacement_text, content)

        if content != new_content:
            # Write back to file
            file_path.write_text(new_content, encoding="UTF8")
            print(f"Updated {config['description']}")
            return True
        print(f"No changes needed in {config['description']}")
        return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def parse_dependency_name(dep_string: str) -> str:
    """Extract package name from dependency string (remove version constraints)"""
    # Handle different formats: "package>=1.0", "package[extra]>=1.0", etc.
    match = re.match(r"^([a-zA-Z0-9\-_]+(?:\[[^\]]+\])?)", dep_string)
    return (
        match.group(1)
        if match
        else dep_string.split(">=")[0].split("==")[0].split("<")[0].split(">")[0]
    )


def is_dev_dependency(package_name: str) -> bool:
    """Check if a package is a dev dependency"""
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        return False

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        # Check if package is in dev dependencies
        if "dependency-groups" in data and "dev" in data["dependency-groups"]:
            dev_deps = data["dependency-groups"]["dev"]
            dev_package_names = [parse_dependency_name(dep) for dep in dev_deps]
            return package_name in dev_package_names

        return False

    except Exception:
        return False


def read_dependencies_from_pyproject() -> list[str]:
    """Read dependencies from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        print("pyproject.toml not found in current directory")
        return []

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        dependencies: list[str] = []

        # Read main dependencies
        if "project" in data and "dependencies" in data["project"]:
            main_deps = data["project"]["dependencies"]
            dependencies.extend([parse_dependency_name(dep) for dep in main_deps])
            print(f"Found {len(main_deps)} main dependencies")

        # Read dev dependencies from dependency-groups
        if "dependency-groups" in data and "dev" in data["dependency-groups"]:
            dev_deps = data["dependency-groups"]["dev"]
            dev_parsed = [parse_dependency_name(dep) for dep in dev_deps]
            dependencies.extend(dev_parsed)
            print(f"Found {len(dev_deps)} dev dependencies")

        return list(set(dependencies))  # Remove duplicates

    except Exception as e:
        print(f"Error reading pyproject.toml: {str(e)}")
        return []


@task
def update_version(c: Connection, current: str, new: str) -> None:
    """
    Update version strings across multiple files.

    Args:
        current: Current version string to replace
        new: New version string to use
    """
    print(f"Replacing version from {current} to {new}")
    print("=" * 50)

    updated_files = 0
    total_files = len(UPDATE_CONFIGS)

    for config in UPDATE_CONFIGS:
        print(f"Processing {config['description']}")

        if replace_in_file(config, current, new):
            updated_files += 1

    print("=" * 50)
    print(f"Version update complete! Updated {updated_files}/{total_files} files")


@task
def check_versions(c: Connection) -> None:
    """Check current versions in all configured files."""
    print("Checking current versions in files:")
    print("=" * 40)

    for config in UPDATE_CONFIGS:
        file_path = Path(config["file"])
        if file_path.exists():
            try:
                content = file_path.read_text()
                print(f"{config['description']}:")

                # Extract version patterns (simplified)
                if "version =" in config["pattern"]:
                    matches = re.findall(r'version = "([^"]+)"', content)
                elif "LABEL version=" in config["pattern"]:
                    matches = re.findall(r'LABEL version="([^"]+)"', content)
                elif "APIFAIRY_VERSION =" in config["pattern"]:
                    matches = re.findall(r'APIFAIRY_VERSION = "([^"]+)"', content)
                else:
                    matches = []

                if matches:
                    print(f"   Current version: {matches[0]}")
                else:
                    print("   No version found")

            except Exception as e:
                print(f"   Error reading file: {e}")
        else:
            print(f"{config['description']}: File not found")
        print()


@task
def run_bun(c: Connection) -> None:
    """Install and copy frontend dependencies using Bun."""
    print("Starting frontend dependency installation and setup...")
    print("=" * 60)

    # Install dependencies
    print("Installing dependencies with Bun...")
    result = c.run(
        "bun add bootstrap-icons bootstrap @popperjs/core jquery datatables.net-bs5 datatables.net",
        hide=False,
    )
    if result.failed:
        print("Error: Failed to install dependencies")
        return

    # Create directories if they don't exist
    print("Ensuring static directories exist...")
    c.run("mkdir -p src/app/static/js src/app/static/css src/app/static/css/fonts", hide=True)

    print("Processing PopperJS files...")
    try:
        c.run("ls -la ./node_modules/@popperjs/core/dist/umd/", hide=True)
        c.run("cp node_modules/@popperjs/core/dist/umd/popper.min.js src/app/static/js/")
        # Only copy optional files if they exist
        c.run("cp node_modules/@popperjs/core/dist/umd/popper.min.js.flow src/app/static/js/")
        c.run("cp node_modules/@popperjs/core/dist/umd/popper.min.js.map src/app/static/js/")
        print("  ✓ PopperJS files copied")
    except Exception as e:
        print(f"  Warning: PopperJS copy failed: {e}")

    # Bootstrap
    print("Processing Bootstrap files...")
    try:
        c.run("ls -la ./node_modules/bootstrap/dist/js/", hide=True)
        c.run("cp node_modules/bootstrap/dist/js/bootstrap.bundle.min.js src/app/static/js/")
        c.run("cp node_modules/bootstrap/dist/js/bootstrap.bundle.min.js.map src/app/static/js/")
        print("  ✓ Bootstrap JS files copied")

        # Download custom Bootstrap theme
        print("  Downloading Bootswatch Darkly theme...")
        result = c.run(
            "wget https://bootswatch.com/5/darkly/bootstrap.min.css -O src/app/static/css/bootstrap.min.css",
            hide=True,
        )
        if result.ok:
            print("  ✓ Bootstrap theme downloaded")
        else:
            print("  Warning: Failed to download Bootstrap theme, using default...")
            c.run("cp node_modules/bootstrap/dist/css/bootstrap.min.css src/app/static/css/")

        c.run("cp node_modules/bootstrap/dist/css/bootstrap.min.css.map src/app/static/css/")
    except Exception as e:
        print(f"  Warning: Bootstrap copy failed: {e}")

    # Bootstrap Icons
    print("Processing Bootstrap Icons...")
    try:
        c.run("ls -la ./node_modules/bootstrap-icons/font", hide=True)
        c.run("cp node_modules/bootstrap-icons/font/bootstrap-icons.css src/app/static/css/")
        c.run("cp -r node_modules/bootstrap-icons/font/fonts/* src/app/static/css/fonts/")
        print("  ✓ Bootstrap Icons copied")
    except Exception as e:
        print(f"  Warning: Bootstrap Icons copy failed: {e}")

    # DataTables
    print("Processing DataTables files...")
    try:
        c.run("ls -la ./node_modules/datatables.net/js", hide=True)
        c.run("cp node_modules/datatables.net/js/jquery.dataTables.min.js src/app/static/js/")

        c.run("ls -la ./node_modules/datatables.net-bs5/", hide=True)
        c.run(
            "cp node_modules/datatables.net-bs5/js/dataTables.bootstrap5.min.js src/app/static/js/"
        )
        c.run(
            "cp node_modules/datatables.net-bs5/css/dataTables.bootstrap5.min.css src/app/static/css/"
        )
        print("  ✓ DataTables files copied")
    except Exception as e:
        print(f"  Warning: DataTables copy failed: {e}")

    # jQuery
    print("Processing jQuery files...")
    try:
        c.run("ls -la ./node_modules/jquery/dist", hide=True)
        c.run("cp node_modules/jquery/dist/jquery.min.js src/app/static/js/")
        c.run("cp node_modules/jquery/dist/jquery.min.map src/app/static/js/")
        print("  ✓ jQuery files copied")
    except Exception as e:
        print(f"  Warning: jQuery copy failed: {e}")

    # Verify copied files
    print("Verifying copied files...")
    js_files = [
        "src/app/static/js/popper.min.js",
        "src/app/static/js/bootstrap.bundle.min.js",
        "src/app/static/js/jquery.dataTables.min.js",
        "src/app/static/js/dataTables.bootstrap5.min.js",
        "src/app/static/js/jquery.min.js",
    ]

    css_files = [
        "src/app/static/css/bootstrap.min.css",
        "src/app/static/css/bootstrap-icons.css",
        "src/app/static/css/dataTables.bootstrap5.min.css",
    ]

    missing_files = []
    for file_path in js_files + css_files:
        result = c.run(f"test -f {file_path}", hide=True, warn=True)
        if result.failed:
            missing_files.append(file_path)

    if missing_files:
        print("Warning: The following files were not copied successfully:")
        for file in missing_files:
            print(f"  - {file}")
    else:
        print("  ✓ All files verified successfully")

    # Cleanup
    print("Cleaning up node_modules...")
    c.run("rm -rf node_modules/", hide=True)

    print("=" * 60)
    print("Frontend dependency setup completed!")

    # Summary
    print("\nSummary of installed components:")
    print("- Bootstrap 5 (with Darkly theme)")
    print("- Bootstrap Icons")
    print("- jQuery")
    print("- DataTables with Bootstrap 5 integration")
    print("- PopperJS (Bootstrap dependency)")

    if missing_files:
        print(
            f"\nNote: {len(missing_files)} files had issues during copying. Check warnings above."
        )
    else:
        print("\nAll components installed successfully!")


@task
def update_deps(c: Connection) -> None:
    """
    Update Python dependencies to latest versions using uv
    """
    dependencies: list[str] = read_dependencies_from_pyproject()

    if not dependencies:
        print("No dependencies found to update")
        return

    print(f"Starting dependency update process with uv for {len(dependencies)} packages...")

    # Update each dependency to latest version
    failed_updates: list[str] = []
    successful_updates: list[str] = []

    for dep in dependencies:
        try:
            print(f"\nUpdating {dep}...")

            # Check if this is a dev dependency by reading the original pyproject.toml
            is_dev_dep = is_dev_dependency(dep)

            # First remove the package
            if is_dev_dep:
                remove_result = c.run(f"uv remove {dep} --dev", warn=True, hide="out")
            else:
                remove_result = c.run(f"uv remove {dep}", warn=True, hide="out")

            if not remove_result.ok:
                print(f"Warning: Could not remove {dep}, continuing with add...")

            # Then add the latest version
            if is_dev_dep:
                result = c.run(f"uv add {dep} --dev", warn=True, hide="out")
            else:
                result = c.run(f"uv add {dep}", warn=True, hide="out")

            if result.ok:
                dep_type = " (dev)" if is_dev_dep else ""
                print(f"Successfully updated {dep}{dep_type}")
                successful_updates.append(dep)
            else:
                print(f"Failed to update {dep}")
                failed_updates.append(dep)

        except Exception as e:
            print(f"Error updating {dep}: {str(e)}")
            failed_updates.append(dep)

    # Print summary
    print("\n" + "=" * 50)
    print("UPDATE SUMMARY")
    print("=" * 50)

    if successful_updates:
        print(f"Successfully updated ({len(successful_updates)}):")
        for dep in successful_updates:
            print(f"   - {dep}")

    if failed_updates:
        print(f"\nFailed to update ({len(failed_updates)}):")
        for dep in failed_updates:
            print(f"   - {dep}")
        print("\nTip: Check if these packages have breaking changes or compatibility issues")

    print(f"\nUpdate process completed!")
    print(
        f"   Total: {len(dependencies)} | Success: {len(successful_updates)} | Failed: {len(failed_updates)}"
    )


@task
def list_deps(c: Connection) -> None:
    """
    List all dependencies found in pyproject.toml
    """
    dependencies: list[str] = read_dependencies_from_pyproject()

    if dependencies:
        print(f"Found {len(dependencies)} dependencies in pyproject.toml:")
        for dep in sorted(dependencies):
            print(f"   - {dep}")
    else:
        print("No dependencies found in pyproject.toml")


@task
def show_outdated(c: Connection) -> None:
    """
    Show outdated dependencies
    """
    print("Checking for outdated dependencies...")
    try:
        # Use uv tree with --outdated flag to show outdated packages
        # Include both main dependencies and dev dependencies
        c.run("uv tree --outdated --depth=1")
    except Exception as e:
        print(f"Error checking outdated packages: {str(e)}")
        print("Trying alternative method...")
        try:
            # Try with explicit groups
            c.run("uv tree --group dev --outdated --depth=1")
        except Exception as e2:
            print(f"Alternative method also failed: {str(e2)}")
            print("Note: Make sure you're in a uv project directory with a pyproject.toml file")


@task
def freeze_deps(c: Connection) -> None:
    """
    Generate requirements.txt and uv.lock with current versions
    """
    print("Generating updating lock...")
    try:
        c.run("uv lock --upgrade")
        print("uv.lock successfully updated")
    except Exception as e:
        print(f"Error updating uv.lock: {str(e)}")

    print("Generating requirements.txt...")
    try:
        c.run("uv export --no-group dev --frozen --output-file=requirements.txt --quiet")
        print("requirements.txt generated successfully")
    except Exception as e:
        print(f"Error generating requirements.txt: {str(e)}")


@task
def update_and_freeze(c: Connection) -> None:
    """
    Update dependencies and generate requirements.txt
    """
    update_deps(c)
    freeze_deps(c)
