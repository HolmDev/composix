import os
import sys

from composix import images, podman
from composix.util import LogLevel, log

REQUIRES_LOAD = {
    "up",
    "create",
    "run",
    "restart",
    "start",
    "build",
    "pull",
    "save",
}


def usage() -> None:
    """Prints the wrappers usage."""
    sys.stderr.write(
        "usage: composix {global options} [SUBCOMMAND {subcommand options}]\n\n"
        "custom subcommands:\n"
        "  save  Save image derivation(s) to an archive\n\n"
        "Everything is passed to podman-compose\n"
        "See podman-compose usage below\n",
    )
    podman.usage()


def main() -> None:
    subcmd = podman.get_subcmd(sys.argv)

    if not subcmd:
        log("Found no subcommand, printing usage", LogLevel.DEBUG)
        usage()
        sys.exit(1)

    log(f"Found subcommand: {subcmd}", LogLevel.DEBUG)

    compose_file = os.getenv("COMPOSIX_COMPOSE_FILE")
    image_envstr = os.getenv("COMPOSIX_IMAGES")

    if not compose_file:
        log("The compose file derivation path is missing, are you sure you are running it from the `composix.lib.mkWrapper'", LogLevel.ERROR)

    if not image_envstr:
        log("The image derivation paths are missing", LogLevel.ERROR)

    imgs = images.parse_envstr(str(image_envstr))

    if subcmd in REQUIRES_LOAD:
        log("Loading image derivations", LogLevel.INFO)
        for img in imgs:
            podman.load(img)
            podman.retag(img)

    if subcmd == "save":
        podman.save(imgs, sys.argv)
    else:
        podman.compose(str(compose_file), sys.argv)


if __name__ == "__main__":
    main()
