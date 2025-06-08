# This scripts is a automated process to push a commit to a remote repository
# Also to change the version and upload the packet to the pypi server
import os
import subprocess
import sys
import toml
from dotenv import load_dotenv
load_dotenv()

# Import rich for colorful output
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt


# Define a custom theme for rich console output
release_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "step": "bold magenta",
    "command_output": "dim blue", # For command stdout/stderr
    "prompt": "bold blue"
})
console = Console(theme=release_theme)

# --- Configuration ---
PYPROJECT_TOML_PATH = "pyproject.toml"
DIST_DIR = "dist"
VERSION_CHOICES = ["major", "minor", "patch"]
REMOTE_NAME = "origin" # Your Git remote name (e.g., 'origin', 'upstream')
MAIN_BRANCH = "main"   # Your main branch (e.g., 'main', 'master')

# --- Helper Functions ---

# Removed: check_dependencies() as per user request
# Removed: check_is_git_repo() as per user request

def read_pyproject_toml():
    """Reads the pyproject.toml file and returns its content."""
    try:
        with open(PYPROJECT_TOML_PATH, "r") as f:
            return toml.load(f)
    except FileNotFoundError:
        console.print(f"[error]Error: {PYPROJECT_TOML_PATH} not found. Please ensure it's in the current directory.[/error]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[error]Error reading {PYPROJECT_TOML_PATH}: {e}[/error]")
        sys.exit(1)

def write_pyproject_toml(data):
    """Writes content back to the pyproject.toml file."""
    try:
        with open(PYPROJECT_TOML_PATH, "w") as f:
            toml.dump(data, f)
    except Exception as e:
        console.print(f"[error]Error writing to {PYPROJECT_TOML_PATH}: {e}[/error]")
        sys.exit(1)

def get_current_version(pyproject_data):
    """Extracts the current version from the pyproject.toml data."""
    try:
        return pyproject_data["project"]["version"]
    except KeyError:
        console.print(f"[error]Error: 'project.version' not found in {PYPROJECT_TOML_PATH}.[/error]")
        console.print("Please ensure your pyproject.toml has a [project] section with a 'version' key.")
        sys.exit(1)

def bump_version(current_version, bump_type):
    """Bumps the version string based on the bump_type (major, minor, patch)."""
    parts = list(map(int, current_version.split(".")))
    if len(parts) != 3:
        console.print(f"[warning]Warning: Unexpected version format '{current_version}'. Assuming X.Y.Z format.[/warning]")
        # Attempt to handle non-standard versions, e.g., 0.1 -> 0.1.0
        while len(parts) < 3:
            parts.append(0)

    if bump_type == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif bump_type == "minor":
        parts[1] += 1
        parts[2] = 0
    elif bump_type == "patch":
        parts[2] += 1
    else:
        console.print(f"[error]Error: Invalid bump type '{bump_type}'. Choose from {', '.join(VERSION_CHOICES)}.[/error]")
        sys.exit(1)

    return ".".join(map(str, parts))

def run_command(command, cwd=None, shell=False, check=True, capture_output=False):
    """Helper to run shell commands, printing output with rich."""
    console.print(f"\n[info]Running command:[/info] [blue]{' '.join(command) if isinstance(command, list) else command}[/blue]")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            check=check,
            capture_output=capture_output,
            text=True,
            encoding='utf-8'
        )
        if result.stdout and capture_output: # Only print if capture_output is True
            console.print("[command_output]STDOUT:[/command_output]\n", result.stdout)
        if result.stderr and capture_output: # Only print if capture_output is True
            console.print("[warning]STDERR:[/warning]\n", result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        console.print(f"[error]Command failed with error code {e.returncode}[/error]")
        if e.stdout: console.print("[command_output]STDOUT:[/command_output]\n", e.stdout)
        if e.stderr: console.print("[warning]STDERR:[/warning]\n", e.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        console.print(f"[error]Error: Command not found. Make sure '{command[0]}' is in your PATH.[/error]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[error]An unexpected error occurred while running command: {e}[/error]")
        sys.exit(1)


# --- Main Release Logic ---

def main():
    # Removed: check_dependencies() as per user request
    # Removed: check_is_git_repo() as per user request
    # Removed: Git status and pull checks as per user request

    # Read pyproject.toml
    pyproject_data = read_pyproject_toml()
    current_version = get_current_version(pyproject_data)
    console.print(f"[info]Current package version:[/info] [bold white]{current_version}[/bold white]")

    # Get bump type from user using rich.prompt
    bump_type = Prompt.ask(
        f"[prompt]Enter bump type[/prompt]",
        choices=VERSION_CHOICES,
        default="patch"
    ).lower()

    new_version = bump_version(current_version, bump_type)
    console.print(f"[info]New version will be:[/info] [bold white]{new_version}[/bold white]")

    confirm = Prompt.ask("[prompt]Confirm release[/prompt]", choices=["y", "n"], default="n").lower()
    if confirm != "y":
        console.print("[info]Release cancelled.[/info]")
        sys.exit(0)

    # --- Step 1: Update pyproject.toml ---
    console.print("\n[step]--- Updating pyproject.toml ---[/step]")
    pyproject_data["project"]["version"] = new_version
    write_pyproject_toml(pyproject_data)
    console.print(f"[success]Updated {PYPROJECT_TOML_PATH} to version [bold white]{new_version}[/bold white].[/success]")

    # --- Step 2: Git Commit ---
    # console.print("\n[step]--- Committing changes ---[/step]")
    # run_command(["git", "add", PYPROJECT_TOML_PATH])
    # commit_message = f"chore(release): {new_version}"
    # run_command(["git", "commit", "-m", commit_message])
    # console.print(f"[success]Committed: {commit_message}[/success]")

    # --- Step 3: Create Git Tag ---
    console.print("\n[step]--- Creating Git tag ---[/step]")
    tag_name = f"v{new_version}"
    existing_tags_result = run_command(["git", "tag", "-l", tag_name], capture_output=True)
    if existing_tags_result.stdout.strip() == tag_name:
        console.print(f"[warning]Warning: Tag '{tag_name}' already exists. Skipping tag creation.[/warning]")
    else:
        run_command(["git", "tag", "-a", tag_name, "-m", f"Release {new_version}"])
        console.print(f"[success]Created tag: [bold green]{tag_name}[/bold green][/success]")

    # --- Step 4: Clean old dist files ---
    console.print(f"\n[step]--- Cleaning '{DIST_DIR}' directory ---[/step]")
    run_command(["Remove-Item", "-Path", DIST_DIR, "-Recurse", "-Force"])
    console.print(f"[success]Cleaned '{DIST_DIR}'.[/success]")

    # --- Step 5: Build package with Flit ---
    console.print("\n[step]--- Building package with Flit ---[/step]")
    run_command(["flit", "build"])
    console.print("[success]Package built successfully.[/success]")

    # --- Step 6: Upload to PyPI with Twine ---
    console.print("\n[step]--- Uploading to PyPI with Twine ---[/step]")
    # Prompt for PyPI API Token interactively
    pypi_token = os.getenv("PYPI_TOKEN")
    if not pypi_token:
        console.print("[error]PyPI API Token cannot be empty. Release cancelled.[/error]")
        sys.exit(1)

    # Twine uses -u and -p for username and password (token)
    run_command(["twine", "upload", "-u", "__token__", "-p", pypi_token, f"{DIST_DIR}/*"])
    console.print("[success]Package uploaded to PyPI successfully![/success]")

    # --- Step 7: Push to GitHub ---
    console.print(f"\n[step]--- Pushing commit and tag to {REMOTE_NAME}/{MAIN_BRANCH} ---[/step]")
    try:
        # Push the current branch and all new tags
        run_command(["git", "push", REMOTE_NAME, MAIN_BRANCH, "--follow-tags"])
        console.print("[success]Changes pushed to GitHub successfully![/success]")
    except Exception as e: # Catch all exceptions from run_command for Git ops
        console.print(f"[error]Error pushing to GitHub: {e}[/error]")
        console.print("[info]Please ensure your Git credentials are set up for pushing.[/info]")
        sys.exit(1)

    console.print("\n[success]--- Release process completed successfully! ---[/success]")
    console.print(f"[info]New version:[/info] [bold white]{new_version}[/bold white]")
    console.print(f"[info]Git tag:[/info] [bold white]{tag_name}[/bold white]")
    console.print("[info]Check your PyPI project and GitHub repository for the new release.[/info]")

if __name__ == "__main__":
    main()
