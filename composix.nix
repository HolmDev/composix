{
  lib,
  python3Packages,
}:

python3Packages.buildPythonApplication {
  pname = "composix";
  version = "0.1.0";

  src = ./composix;

  pyproject = true;
  build-system = with python3Packages; [ setuptools ];

  meta = {
    description = "A podman-compose wrapper for loading OCI-images built with Nix";
    homepage = "https://github.com/HolmDev/composix";
    license = lib.licenses.lgpl3Plus;
    platforms = lib.platforms.unix;
  };
}
