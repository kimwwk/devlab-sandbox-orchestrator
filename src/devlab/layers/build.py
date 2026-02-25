"""Layer 1: Build - Docker image building."""

import subprocess
from pathlib import Path

# Image naming convention
IMAGE_PREFIX = "devlab-sandbox"

# Path to Dockerfiles
IMAGES_DIR = Path(__file__).parent.parent / "images"


def get_image_tag(toolchain: str) -> str:
    """Get full image tag for a toolchain.

    Args:
        toolchain: Toolchain name (node, python, fullstack)

    Returns:
        Full image tag (e.g., devlab-sandbox:node)
    """
    return f"{IMAGE_PREFIX}:{toolchain}"


def get_dockerfile_path(toolchain: str) -> Path:
    """Get path to Dockerfile for a toolchain.

    Args:
        toolchain: Toolchain name

    Returns:
        Path to Dockerfile

    Raises:
        FileNotFoundError: If Dockerfile doesn't exist
    """
    dockerfile = IMAGES_DIR / f"Dockerfile.{toolchain}"
    if not dockerfile.exists():
        available = [f.stem.replace("Dockerfile.", "") for f in IMAGES_DIR.glob("Dockerfile.*")]
        raise FileNotFoundError(
            f"No Dockerfile for toolchain '{toolchain}'. Available: {available}"
        )
    return dockerfile


def image_exists(tag: str) -> bool:
    """Check if Docker image exists locally.

    Args:
        tag: Full image tag

    Returns:
        True if image exists
    """
    result = subprocess.run(
        ["docker", "image", "inspect", tag],
        capture_output=True,
    )
    return result.returncode == 0


def build_image(toolchain: str = "node", force: bool = False) -> str:
    """Build Docker image for a toolchain.

    Args:
        toolchain: Toolchain name (default: node)
        force: Force rebuild even if image exists

    Returns:
        Image tag that was built

    Raises:
        FileNotFoundError: If Dockerfile doesn't exist
        subprocess.CalledProcessError: If build fails
    """
    tag = get_image_tag(toolchain)

    # Skip if already exists (unless forced)
    if not force and image_exists(tag):
        print(f"Image {tag} already exists (use force=True to rebuild)")
        return tag

    dockerfile = get_dockerfile_path(toolchain)

    print(f"Building image {tag} from {dockerfile}...")

    # Build image
    subprocess.run(
        [
            "docker", "build",
            "-t", tag,
            "-f", str(dockerfile),
            str(IMAGES_DIR),
        ],
        check=True,
    )

    print(f"Successfully built {tag}")
    return tag


def list_images() -> list[str]:
    """List available devlab images.

    Returns:
        List of image tags
    """
    result = subprocess.run(
        ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}", IMAGE_PREFIX],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []

    return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
