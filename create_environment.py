#!/usr/bin/env python3
import argparse
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory


def pip_install(package):
    """
    Install a Python package using pip.

    Parameters
    ----------
    package : str
        The name of the Python package to install.
    """

    subprocess.check_call(
        [os.path.join(sys.exec_prefix, "bin", "python"), "-m", "ensurepip"]
    )
    subprocess.check_call(
        [
            os.path.join(sys.exec_prefix, "bin", "python"),
            "-m",
            "pip",
            "install",
            package,
        ]
    )


try:
    import yaml
except ImportError:
    pip_install("pyyaml")
    import yaml

try:
    import tomllib as toml
except ImportError:
    try:
        import tomli as toml
    except ImportError:
        pip_install("tomli")
        import tomli as toml


try:
    from packaging.specifiers import SpecifierSet
    from packaging.version import Version
except ImportError:
    pip_install("packaging")
    from packaging.specifiers import SpecifierSet
    from packaging.version import Version

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.ERROR
)

logger = logging.getLogger("create-conda-env")


def get_download_url():
    """
    Determine the appropriate Micromamba download URL based on the current system's
    architecture and operating system.

    Returns
    -------
    str:
        The Micromamba download URL.
    """
    system = platform.system().lower()
    arch = platform.machine().lower()

    logger.debug("Checking arch and getting mamba url")

    if system == "linux":
        if arch == "x86_64":
            return "https://micro.mamba.pm/api/micromamba/linux-64/latest"
        if arch == "aarch64":
            return "https://micro.mamba.pm/api/micromamba/linux-aarch64/latest"
        if arch == "ppc64le":
            return "https://micro.mamba.pm/api/micromamba/linux-ppc64le/latest"
    elif system == "darwin":
        if arch == "x86_64":
            return "https://micro.mamba.pm/api/micromamba/osx-64/latest"
        if arch == "arm64":
            return "https://micro.mamba.pm/api/micromamba/osx-arm64/latest"

    raise ValueError(f"Unsupported system or architecture: {system}-{arch}")


def download_with_progress(url, output_path):
    """
    Download a file from a URL with a visual progress bar.

    Parameters
    ----------
    url (str):
        The URL to download from.
    output_path (str):
        The path where the downloaded file will be saved.
    """
    logger.debug("Downloading micromamba")
    with urllib.request.urlopen(url) as response:
        total_size = int(response.getheader("Content-Length", 0))
        downloaded_size = 0
        chunk_size = 8192

        with open(output_path, "wb") as file:
            while chunk := response.read(chunk_size):
                file.write(chunk)
                downloaded_size += len(chunk)
                done = int(50 * downloaded_size / total_size)
                sys.stdout.write(
                    f"\rDownloading: [{'=' * done}{' ' * (50 - done)}] "
                    f"{downloaded_size // 1024} KB / {total_size // 1024} KB"
                )
                sys.stdout.flush()
    print("\nDownload complete.")


def extract_micromamba(tar_path, extract_dir):
    """
    Extract the Micromamba binary from the tar file.

    Parameters
    -----------
    tar_path (str):
        The path to the tar file.
    extract_dir (str):
        The directory to extract to.
    """
    logger.debug("Extracting micromamba")
    with tarfile.open(tar_path, "r") as tar:
        for member in tar.getmembers():
            if "bin/micromamba" in member.name:
                print(f"Extracting {member.name} to {extract_dir}...")
                tar.extract(member, path=extract_dir)
                break
    logger.debug("Extraction complete.")


def parse_args(argv=None):
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser("create-conda-env")
    parser.add_argument(
        "input_dir",
        default=".",
        help="The path to the tool definition.",
        type=Path,
    )
    parser.add_argument(
        "-d",
        "--dev",
        action="store_true",
        default=False,
        help="Use development mode for any installation.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="Force recreation of the environment.",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        help=("The install prefix where the environment should" " be installed"),
        type=Path,
        default=os.getenv("INSTALL_PREFIX", "~/.tools/"),
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)
    args = parser.parse_args(argv)
    logger.setLevel(max(logging.DEBUG, logger.level - (10 * args.verbose)))
    return args


def create_environment(mamba_dir, tool_dir, env_dir, tool_config):
    """Create the the tool conda environments.

    Parameters
    ----------
    mamba_dir : Path
        Path to the Micromamba binary directory.
    tool_dir : Path
        Path to the tool definition directory.
    env_dir : Path
        Path where the Conda environment will be created.
    tool_config : dict
        The parsed configuration of the tool from the TOML file.
    """

    requ_file = tool_dir.expanduser().absolute() / "requirements.txt"
    pip_cmd = []
    env_file = tool_dir / "environment.yml"
    if env_dir.is_dir():
        shutil.rmtree(env_dir)
    if requ_file.is_file():
        pip_cmd = ["-r", str(requ_file)]
    for file in ("setup.py", "setup.cfg", "pyproject.toml"):
        if (tool_dir / file).is_file():
            pip_cmd = [str(tool_dir)]
            break
    logger.debug(
        "Creating environment for %s",
        tool_config["tool"]["run"].get("dependencies", []),
    )
    deps = tool_config["tool"]["run"].get("dependencies", []) + [
        "jq",
        "mamba",
        "websockets",
    ]
    if not env_file.is_file():
        env = os.environ.copy()
        subprocess.check_call(
            [
                str(mamba_dir / "bin" / "micromamba"),
                "create",
                "-c",
                "conda-forge",
                "-p",
                str(env_dir),
                "-y",
                "--strict-channel-priority",
            ]
            + deps,
        )
        env["PATH"] = str(env_dir / "bin") + os.pathsep + env["PATH"]
        create_environment_file(env_dir, env, env_file)
    else:
        logger.debug("Recrating principal environment")
        subprocess.check_call(
            [
                str(mamba_dir / "bin" / "micromamba"),
                "env",
                "create",
                "-y",
                "-p",
                str(env_dir),
                "--file",
                str(env_file),
            ],
        )
    if pip_cmd:
        logger.debug("Installing additional packages via pip")
        subprocess.check_call(
            [
                str(env_dir / "bin" / "python3"),
                "-m",
                "pip",
                "install",
            ]
            + pip_cmd
        )


def set_version(conda_dir, version, new=True):
    """Set the version in the version file.

    Parameters
    ----------
    conda_dir: Path
        The parent path of all conda environments for this tool
    version: str
        The of the tool
    new:
        Wheather or not an entire conda environment was created.
    """
    version_file = conda_dir.parent / ".versions.json"
    if version_file.is_file():
        content = json.loads(version_file.read_text())
    else:
        version_file.parent.mkdir(exist_ok=True, parents=True)
        new = True
        content = {"latest": str(conda_dir.absolute())}
    if new:
        content[version] = str(conda_dir.absolute())
        content["latest"] = content[version]
    else:
        content[version] = content["latest"]
    version_file.write_text(json.dumps(content, indent=3))


def copy_all(input_path, target_path):
    """
    Recursively copy all files and subdirectories from input_dir/* to target_dir/.

    Parameters
    ----------
    input_dir (str):
        Path to the source directory.
    target_dir (str):
        Path to the destination directory.
    """

    if not input_path.exists():
        raise FileNotFoundError(f"Input directory '{input_path}' does not exist.")
    shutil.rmtree(target_path)
    # Ensure the target directory exists
    target_path.mkdir(parents=True, exist_ok=True)

    # Iterate over all files and directories in input_path
    for item in input_path.rglob("*"):
        target_item = target_path / item.relative_to(input_path)

        if item.is_dir():
            # Creae the corresponding directory in the target path
            target_item.mkdir(parents=True, exist_ok=True)
        else:
            # Copy the file to the corresponding target path
            shutil.copy(item, target_item)
            logger.debug("Copied: %s -> %s", item, target_item)


def create_environment_file(path, env, env_file):
    """Create an environment file of a conda environment."""
    out = subprocess.check_output(
        ["mamba", "env", "export", "-p", str(path)],
        env=env,
    )
    conda_env = yaml.safe_load(out.decode())
    with (env_file).open("w", encoding="utf-8") as stream:
        stream.write(
            yaml.safe_dump(
                {
                    "dependencies": conda_env["dependencies"],
                    "channels": ["conda-forge"],
                }
            )
        )


def build(env_dir, build_dir, env_file, build_config):
    """Build the tool if it has to be built."""
    conda_dir = json.loads((env_dir / ".versions.json").read_text())["latest"]
    build_script = build_dir.expanduser().absolute() / "build.sh"
    env = os.environ.copy()
    if not build_config and not build_script.is_file():
        return
    with TemporaryDirectory() as temp_dir:
        temp_path = str(Path(temp_dir) / "bin")
        env["PATH"] = (
            temp_path
            + os.pathsep
            + str(conda_dir)
            + os.pathsep
            + os.getenv("PATH")
        )

        deps = build_config.get("dependencies", [])
        if deps:
            if not env_file.is_file():
                subprocess.check_call(
                    [
                        "mamba",
                        "create",
                        "-c",
                        "conda-forge",
                        "-p",
                        temp_dir,
                        "-y",
                        "--strict-channel-priority",
                    ]
                    + deps,
                    env=env,
                )
                create_environment_file(temp_dir, env, env_file)
            else:
                logger.debug("Recrating build environment")
                subprocess.check_call(
                    [
                        "mamba",
                        "env",
                        "create",
                        "-p",
                        temp_dir,
                        "--file",
                        str(env_file),
                    ],
                    env=env,
                )

    if build_script.is_file():
        build_script.chmod(0o755)
        subprocess.check_call(
            [str(build_script)], env=env, cwd=str(build_script.parent)
        )


def load_config(input_dir):
    """
    Load the tool configuration from a TOML or pyproject.toml file.

    Parameters
    ----------
    input_dir : Path
        Path to the directory containing the configuration file.

    Returns
    -------
    dict
        The parsed configuration data.

    Raises
    ------
    ValueError
        f no valid configuration file is found in the directory.
    """

    for file in ("tool.toml", "pyproject.toml"):
        if (input_dir / file).is_file():
            return toml.loads((input_dir / file).read_text())
    raise ValueError(
        "Your tool must be defined in either a tool.toml or pyproject.toml file"
    )


def parse_dependency(dependency: str):
    """
    Parse a dependency string into a package name and version constraint.

    Parameters
    ----------
    dependency : str
        The dependency string (e.g., "foo>3").

    Returns
    -------
    tuple
        A tuple of (package_name, version_constraint).
        If no version constraint is provided, returns (package_name, "").
    """
    match = re.match(r"^([a-zA-Z0-9_\-]+)([<>=!~^].*)?$", dependency)
    if not match:
        raise ValueError(f"Invalid dependency format: {dependency}")
    package_name, version_constraint = match.groups()
    return package_name, version_constraint or ""


def check_for_environment_creation(source_dir, env_dir, dependencies):
    """Check the dependencies and decide about a (re)creation of the environment.

    Parameters
    ----------
    source_dir: Path
        The source-code directory
    env_dir: Path
        The conda env of all versions of the tool
    dependencies: List[str]
        defined dependencies of the tool

    Returns
    -------
    bool: whether or not a complete new environment needs to be created.
    """

    env_file = source_dir / "environment.yml"
    for file in (env_file, env_dir, env_dir / ".versions.json"):
        if not file.exists():
            return True
    deps_lock = {}

    try:
        deps_lock = yaml.safe_load(env_file.read_text())
    except Exception:
        logger.warning("Could not read environment.yml file")
        env_file.unlink()
        return True
    dependency_specs = {}
    for dep in deps_lock["dependencies"]:
        dep_vers = dep.split("=")
        dependency_specs[dep_vers[0]] = dep_vers[1:]
    try:
        versions = json.loads((env_dir / ".versions.json").read_text())
        if not (Path(versions["latest"]) / "bin").exists():
            recreate = True
        else:
            recreate = False
    except Exception:
        recreate = True
    for p in dependencies:
        package_name, constraint = parse_dependency(p)
        if package_name not in dependency_specs:
            # We do have a requested package that is not installed yet.
            deps_lock["dependencies"].append(p)
            recreate = True
        else:

            installed_version = Version(dependency_specs[package_name][0])
            if constraint and installed_version not in SpecifierSet(constraint):
                recreate = True
                # We need another version
                deps_lock["dependencies"] = [
                    d
                    for d in deps_lock["dependencies"]
                    if not d.startswith(package_name)
                ]
                deps_lock["dependencies"].append(p)
    if recreate:
        deps_lock["dependencies"].sort()
        env_file.write_text(yaml.safe_dump(deps_lock))
    return recreate


def main(input_dir, prefix_dir, force=False):
    """
    Main function to create the Conda environment for a tool.

    Parameters
    ----------
    input_dir : Path
        Path to the tool definition directory.
    prefix_dir : Path
        Installation prefix for the Conda environment.
    force : bool, optional
        Whether to force recreation of the environment, by default False.
    """

    mamba_url = get_download_url()
    input_dir = input_dir.expanduser().absolute()
    config = load_config(input_dir)
    version = config["tool"].get(
        "version", config.get("project", {}).get("version")
    )
    if not version:
        raise ValueError("You need to define a version.")
    env_dir = (
        prefix_dir.expanduser().absolute()
        / config["tool"]["name"]
        / version.lower().strip("v")
    )
    if force is True or check_for_environment_creation(
        input_dir, env_dir.parent, config["tool"]["run"].get("dependencies", [])
    ):
        with TemporaryDirectory() as temp_dir:
            tar_path = Path(temp_dir) / "micromamba.tar.bz2"
            download_with_progress(mamba_url, tar_path)
            extract_micromamba(tar_path, temp_dir)
            micromamba_path = Path(temp_dir) / "bin" / "micromamba"
            if not micromamba_path.is_file:
                raise ValueError(
                    "Micromamba binary was not found after extraction."
                )
            create_environment(Path(temp_dir), input_dir, env_dir, config)
            set_version(env_dir, version, new=True)
    else:
        set_version(env_dir, version, new=False)
    share_dir = env_dir / "share" / "tool" / config["tool"]["name"]
    share_dir.mkdir(exist_ok=True, parents=True)
    build_env_file = input_dir / "build-environment.yml"
    copy_all(input_dir, share_dir)
    try:
        build(
            env_dir.parent,
            share_dir,
            build_env_file,
            config["tool"].get("build", {}),
        )
    except Exception as error:
        logger.error(error)
        shutil.rmtree(env_dir)
        raise ValueError("Failed to create environment.")
    print("The tool was successfully deployed in:", share_dir)


if __name__ == "__main__":
    app = parse_args()
    try:
        main(app.input_dir, app.prefix, force=app.force)
    except ValueError as error:
        raise SystemExit(error) from None
