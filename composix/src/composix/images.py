from __future__ import annotations

from dataclasses import dataclass

from composix.util import LogLevel, log

"""
Stores information about an image derivation
"""


@dataclass
class Image:
    drvtype: str
    drv: str
    ref: str
    nref: str


def parse_envstr(envstr: str) -> list[Image]:
    """Parses envstr into a images.

    Parameters
    ----------
    envstr (str): The envstr to be parsed

    Returns
    -------
    list[Image]: The parsed images

    """
    log("Parsing image envstr: " + envstr, LogLevel.DEBUG)
    images = []

    for line in envstr.split("\n"):
        if not line:
            continue

        drvtype = line[0]
        if drvtype not in {"T", "S"}:
            log(f"Invalid derivation type {drvtype} while parsing", LogLevel.ERROR)

        parts = line[1:].split("\x1f")
        if len(parts) != 3:
            log("Malformed image env entry", LogLevel.ERROR)

        drv, ref, nref = parts
        if not drv or not ref or not nref:
            log("Empty field from parsing when expected non-empty", LogLevel.ERROR)

        images.append(Image(drvtype, drv, ref, nref))

    return images
