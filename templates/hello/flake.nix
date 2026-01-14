{
  description = "Minimal composix example";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.composix = {
    url = "github:HolmDev/composix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    { nixpkgs, composix, ... }:
    let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
      inherit (pkgs.stdenv.hostPlatform) system;
    in
    {
      packages.${system}.default = composix.lib.mkWrapper rec {
        inherit pkgs;
        images.hello = pkgs.dockerTools.examples.helloOnRoot;
        compose = {
          name = "hello-world";
          services.hello.image = composix.lib.localImageRef images.hello;
        };
      };
    };
}
