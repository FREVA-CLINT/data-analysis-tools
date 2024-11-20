#!/usr/bin/env python3
import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory


def pip_install(package):
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
        import toml
    except ImportError:
        pip_install("toml")
        import toml


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.ERROR
)

logger = logging.getLogger("create-conda-env")


def get_download_url() -> str:
    """
    Determine the appropriate Micromamba download URL based on the current system's
    architecture and operating system.

    Returns:
        str: The Micromamba download URL.
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

    raise SystemExit(f"Unsupported system or architecture: {system}-{arch}")


def download_with_progress(url, output_path) -> None:
    """
    Download a file from a URL with a visual progress bar.

    Args:
        url (str): The URL to download from.
        output_path (str): The path where the downloaded file will be saved.
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


def extract_micromamba(tar_path: str, extract_dir: str) -> None:
    """
    Extract the Micromamba binary from the tar file.

    Args:
        tar_path (str): The path to the tar file.
        extract_dir (str): The directory to extract to.
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
        help=(
            "The install prefix where the environment should" " be installed"
        ),
        type=Path,
        default=os.getenv("INSTALL_PREFIX", "~/.tools/"),
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)
    args = parser.parse_args(argv)
    logger.setLevel(max(logging.DEBUG, logger.level - (10 * args.verbose)))
    return args


def create_environment(mamba_dir, tool_dir, env_dir, tool_config):
    """Create the environments."""
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
    deps = tool_config["tool"]["run"].get("dependencies", []) + ["jq", "mamba"]
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
    """Set the version in the version file."""
    version_file = conda_dir.parent / ".versions.json"
    if version_file.is_file():
        content = json.loads(version_file.read_text())
    else:
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

    Args:
        input_dir (str): Path to the source directory.
        target_dir (str): Path to the destination directory.
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input directory '{input_path}' does not exist."
        )
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
            logger.debug(f"Copied: {item} -> {target_item}")


def create_environment_file(path, env, env_file):
    """Create an environment file of a conda environment."""
    out = subprocess.check_output(
        ["mamba", "env", "export", "-p", path], env=env
    )
    conda_env = yaml.safe_load(out.decode())
    conda_env.pop("name", "")
    conda_env.pop("prefix", "")
    with (env_file).open("w", encoding="utf-8") as stream:
        stream.write(yaml.safe_dump(conda_env))


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
    """Load the tool config."""
    for file in ("tool.toml", "pyproject.toml"):
        if (input_dir / file).is_file():
            return toml.loads((input_dir / file).read_text())
    raise SystemExit(
        "Your tool must be defined in either a tool.toml or pyproject.toml file"
    )


def main():
    """Create the conda environment."""
    args = parse_args()
    mamba_url = get_download_url()
    input_dir = args.input_dir.expanduser().absolute()
    config = load_config(input_dir)
    version = config["tool"].get(
        "version", config.get("project", {}).get("version")
    )
    if not version:
        raise SystemExit("You need to define a version.")
    env_dir = (
        args.prefix.expanduser().absolute()
        / config["tool"]["name"]
        / version.lower().strip("v")
    )
    if not env_dir.parent.exists() or args.force is True:
        with TemporaryDirectory() as temp_dir:
            tar_path = Path(temp_dir) / "micromamba.tar.bz2"
            download_with_progress(mamba_url, tar_path)
            extract_micromamba(tar_path, temp_dir)
            micromamba_path = Path(temp_dir) / "bin" / "micromamba"
            if not micromamba_path.is_file:
                raise SystemExit(
                    "Micromamba binary was not found after extraction."
                )
            create_environment(Path(temp_dir), args.input_dir, env_dir, config)
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
        raise SystemExit("Failed to create environment.")
    print("The tool was successfully deployed in:", share_dir)


if __name__ == "__main__":
    main()
