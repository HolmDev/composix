from __future__ import annotations

import getopt
import subprocess
import signal

from composix.util import LogLevel, log, options
from composix.images import Image


def usage() -> None:
    """Makes podman-compose prins its usage."""
    subprocess.run(["podman-compose"], check=False)


def _streamload(script: str) -> None:
    log("Streaming tarball from: " + script, LogLevel.DEBUG)

    p1 = subprocess.Popen(
        [script],
        stdout=subprocess.PIPE,
        stderr=None if options.verbose else subprocess.DEVNULL,
    )

    cmd = ["podman", "image", "load"]
    if not options.verbose:
        cmd.append("--quiet")

    p2 = subprocess.Popen(cmd, stdin=p1.stdout)

    if p1.wait() != 0 or p2.wait() != 0:
        log("podman stream load failed", LogLevel.ERROR)


def _fileload(tarball: str) -> None:
    log("Loading tarball at: " + tarball, LogLevel.DEBUG)

    cmd = ["podman", "image", "load", "--input", tarball]
    if not options.verbose:
        cmd.insert(3, "--quiet")

    if subprocess.run(cmd, check=False).returncode != 0:
        log("podman load failed", LogLevel.ERROR)


def load(img: Image) -> None:
    """Makes podman load an image.

    Parameters
    ----------
    img (Image): The image to be loaded

    """
    if img.drvtype == "T":
        _fileload(img.drv)
    elif img.drvtype == "S":
        _streamload(img.drv)
    else:
        log("Unknown image derivation type: " + img.drvtype, LogLevel.ERROR)


def retag(img: Image) -> None:
    """Makes podman retag an image.

    Parameters
    ----------
    img (Image): The image to be retagged

    """
    log(f"Retagging image: {img.ref} -> {img.nref}", LogLevel.DEBUG)

    cmd = ["podman", "image", "tag", img.ref, img.nref]

    if subprocess.run(cmd, check=False).returncode != 0:
        log("podman tag failed", LogLevel.ERROR)


def save(imgs: list[Image], argv: list[str]) -> None:
    """Makes podman save images.

    Parameters
    ----------
    imgs (list[Image]): The images to be save
    argv (list[str]): The original argv

    """
    log("Saving image derivations", LogLevel.INFO)

    try:
        i = argv.index("save")
    except ValueError:
        log("could not find index of `save'", LogLevel.ERROR)

    cmd = ["podman", "image", *argv[i:]]

    cmd.extend(img.nref for img in imgs)

    cmd.append("--multi-image-archive")

    log(f"Running podman with: {cmd}", LogLevel.DEBUG)
    proc = subprocess.Popen(cmd)

    try:
        proc.wait()
    except KeyboardInterrupt:
        log(f"Caught SIGINT, forwarding to podman", LogLevel.INFO)
        proc.send_signal(signal.SIGINT)
        proc.wait()


def compose(compose_file: str, argv: list[str]) -> None:
    """Wraps podman-compose.

    Parameters
    ----------
    compose_file (str): The compose.yml file to be used
    argv (list[str]): The original argv

    """
    log("Running podman-compose", LogLevel.INFO)

    cmd = ["podman-compose", "--file", compose_file, *argv[1:]]

    log(f"Running podman-compose with: {cmd}", LogLevel.DEBUG)
    proc = subprocess.Popen(cmd)

    try:
        proc.wait()
    except KeyboardInterrupt:
        log(f"Caught SIGINT, forwarding to podman-compose", LogLevel.INFO)
        proc.send_signal(signal.SIGINT)
        proc.wait()


def get_subcmd(argv: list[str]) -> str | None:
    """Parses podman-compose args and retrieves subcommand.

    Parameters
    ----------
    argv (list[str]): The original argv

    Returns
    -------
    str | None: The subcommand if found

    """
    global options

    longopts = [
        "help",
        "version",
        "in-pod=",
        "pod-args=",
        "env-file=",
        "file=",
        "profile=",
        "project-name=",
        "podman-path=",
        "podman-args=",
        "podman-pull-args=",
        "podman-push-args=",
        "podman-build-args=",
        "podman-inspect-args=",
        "podman-run-args=",
        "podman-start-args=",
        "podman-stop-args=",
        "podman-rm-args=",
        "podman-volume-args=",
        "parallel=",
        "no-ansi",
        "no-cleanup",
        "dry-run",
        "verbose",
    ]

    opts, rest = getopt.getopt(argv[1:], "hvf:p:", longopts)
    for opt, _ in opts:
        if opt == "-f":
            log(
                "Do not attempt to set --file yourself, it is managed by the wrapper",
                LogLevel.ERROR,
            )
        elif opt == "--no-ansi":
            options.ansi = False
        elif opt == "--verbose":
            options.verbose = True

    return rest[0] if rest else None
