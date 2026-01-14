{ self, inputs, ... }:
let
  inherit (inputs.nixpkgs) lib;
in
rec {
  # Returns if the argument looks like a compose attrset
  isCompose = compose: (lib.isAttrs compose && compose ? services && lib.isAttrs compose.services);

  # Returns if the argument looks like an image
  isImage = image: (lib.isDerivation image && image ? imageName && image ? imageTag);

  # Returns the retagged local name for an image
  localImageName =
    image:
    assert isImage image;
    "localhost/composix/${image.imageName}";

  # Returns the retagged local tag for an image
  localImageTag =
    image:
    assert isImage image;
    let
      contentHash = builtins.elemAt (builtins.split "-" (baseNameOf image.outPath)) 0;
    in
    "${contentHash}-${image.imageTag}";

  # Returns the retagged local reference (name + tag) for an image
  localImageRef =
    image:
    assert isImage image;
    "${localImageName image}:${localImageTag image}";

  # Creates package output for the wrapper using images and compose structure and package set
  mkWrapper =
    {
      pkgs,
      compose ? {
        services = { };
      },
      images ? { },
    }:
    assert isCompose compose;

    assert lib.isAttrs images;
    let
      imageDrvs = lib.attrValues images;
    in
    assert lib.all isImage imageDrvs;
    let
      # This way of represeting the data structure may break
      # if i.e. the store path contains a unit sep, but that feels
      # like it should not happen accidentally. Fix if something breaks
      imageEnvStr = lib.join "\n" (
        lib.map (
          image:
          let
            # Figure out if we need to stream the image.
            type = if image ? streamScript then "S" else "T";

            ref = "${image.imageName}:${image.imageTag}";
            nref = localImageRef image;

            us = builtins.fromJSON ''"\u001f" ''; # This is a stupid hack
          in
          lib.join us [
            (type + image)
            ref
            nref
          ]
        ) imageDrvs
      );

      # A naive YAML dump of composition. I do not plan to check the validity of the
      # attribute set, besides the assertion above
      composeFile = pkgs.writeText "compose.yml" (pkgs.lib.generators.toYAML { } compose);
    in
    pkgs.stdenv.mkDerivation rec {
      name = "composix";

      dontUnpack = true;

      src = self.packages.${pkgs.stdenv.hostPlatform.system}.composix;

      nativeBuildInputs = [
        pkgs.makeWrapper
      ];

      installPhase = ''
        mkdir -p $out/bin

        makeWrapper $src/bin/${src.pname} $out/bin/${src.pname} \
          --set COMPOSIX_COMPOSE_FILE "${composeFile}" \
          --set COMPOSIX_IMAGES "${imageEnvStr}" \
          --prefix PATH ":" ${
            lib.makeBinPath [
              pkgs.podman
              pkgs.podman-compose
            ]
          }'';
    };
}
