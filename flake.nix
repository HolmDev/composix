{
  description = "A podman-compose wrapper for loading OCI-images built with Nix";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.flake-parts.url = "github:hercules-ci/flake-parts";

  outputs =
    inputs@{
      self,
      flake-parts,
      nixpkgs,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {

      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem =
        { pkgs, ... }:
        {
          packages = rec {
            default = composix;
            composix = pkgs.callPackage (import ./composix.nix) { };
          };

          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              # For nix
              nixd
              nixfmt
              statix

              # For python
              ty
              ruff
            ];
          };
        };
      flake = {
        lib = import ./lib.nix { inherit self inputs; };

        templates = rec {
          hello = {
            path = ./templates/hello;
            description = "Minimal composix example";
          };

          hello-flake-parts = {
            path = ./templates/hello-flake-parts;
            description = "Minimal composix example using flake-parts";
          };

          default = hello;
        };
      };
    };
}
