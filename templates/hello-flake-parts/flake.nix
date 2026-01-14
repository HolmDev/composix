{
  description = "Minimal composix example using flake-parts";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    composix = {
      url = "github:HolmDev/composix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-parts.follows = "flake-parts";
    };

    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    inputs@{
      flake-parts,
      nixpkgs,
      composix,
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
          packages.default = composix.lib.mkWrapper rec {
            inherit pkgs;
            images.hello = pkgs.dockerTools.examples.helloOnRoot;
            compose = {
              name = "hello-world";
              services.hello.image = composix.lib.localImageRef images.hello;
            };
          };
        };
    };
}
