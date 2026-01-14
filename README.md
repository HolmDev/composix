# `composix`: A `podman-compose` wrapper for loading OCI-images built with Nix
## Background
This was written to satisfy my need to manage my `podman-compose` using a Nix flake, using my tarball artifacts generated from [`dockerTools`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-dockerTools), without having to reload the tarballs and update my `compose.yml` every update. It was also a great excuse to not have to deal with YAML. I tried the amazing [Arion from Hercules CI](https://docs.hercules-ci.com/arion/), but they had yet to implement direct loading of tarball derivations, which I very much desired.

I currently use it deploy compositions on my homelab and other devices.
## Example Usage
If you wish to dive right in, you can begin by creating a new flake from a template.
```
$ nix flake init -t github:HolmDev/composix#hello
wrote: "/.../flake.nix"
$ nix shell
$ composix config
[composix] INFO: Running podman-compose
name: hello-world
services:
  hello:
    image: localhost/composix/hello:nhp636afr3ibp5dw7nkr304izqqf4hr5-latest

$ composix up    
[composix] INFO: Pulling image derivations
Loaded image: localhost/hello:latest
[composix] INFO: Running podman-compose
[hello] | Hello, world!
```
You could also run it without dropping into a Nix shell using `nix run . -- <args>`, but I find this painfully slow.
#### Exporting artifacts
If your target machine does not run Nix, or `podman` for that matter, you can export the config to another machine using the `podman-compose` command `config`. To export the retagged images, you can use the wrapped `save` command, which wraps `podman image save` with the image derivations.
```
$ composix config | tee compose.yml
[composix] INFO: Running podman-composename: hello-world
services:
  hello:
    image: localhost/composix/hello:nhp636afr3ibp5dw7nkr304izqqf4hr5-latest
$ composix save -o images.tar 
[composix] INFO: Pulling image derivations
Loaded image: localhost/hello:latest
[composix] INFO: Saving image derivations
Copying blob f5f21e25f166 done   | 
Copying blob cb33eacb58d9 done   | 
Copying blob 14142b511b40 done   | 
Copying blob e7442e9fb6d1 done   | 
Copying blob 662d1059f1ad done   | 
Copying blob f0d1ba7ec9ec done   | 
Copying config 150f3a4b84 done   | 
Writing manifest to image destination
```
## Documentation
### Wrapper overview
The wrapper is not very complicated, it simply wraps `podman-compose`, loading the `dockerTools` image derivations if deemed necessary, and allows the exporting of those images using `save`.

I choose to write it in `python3`, since `podman-compose` already depends on that.
### Library functions
The following is the documentation for the library output of the flake.
#### `lib.isCompose`
Takes: An attrset.
Returns: If the attrset naively looks like `compose.yml` spec.
Example:
```
nix-repl> lib.isCompose { services = {}; }
true
```
#### `lib.isImage`
Takes: A derivation
Returns: If the derivation looks like an image
Example:
```
nix-repl> lib.isImage pkgs.dockerTools.examples.helloOnRoot
true
```
#### `lib.localImageName`
Takes: A derivation of an image from `dockerTools`
Returns: The retagged local name for the image
Example:
```
nix-repl> lib.localImageName dockerTools.examples.helloOnRoot
"localhost/composix/hello"
```
#### `lib.localImageTag`
Takes: A derivation of an image from `dockerTools`
Returns: The retagged local tag for the image
Example:
```
nix-repl> lib.localImageTag dockerTools.examples.helloOnRoot  
"nhp636afr3ibp5dw7nkr304izqqf4hr5-latest"
```
#### `lib.localImageRef`
Takes: A derivation of an image from `dockerTools`
Returns: The retagged local reference (name + tag) for the image
Example:
```
nix-repl> lib.localImageRef dockerTools.examples.helloOnRoot 
"localhost/composix/hello:nhp636afr3ibp5dw7nkr304izqqf4hr5-latest"
```
#### `lib.mkWrapper`
Takes: An attrset with the attributes:
- `pkgs` containing the package set used
- `compose` containing the attrset of the `compose.yml` file.
- `images` containing a attrset of image derivations used in the compose file.
Returns: Package for the wrapper using images and compose structure and package set
```
nix-repl> lib.mkWrapper rec {
> inherit pkgs;
> images.hello = pkgs.dockerTools.examples.helloOnRoot;
> compose = {
> name = "hello-world";
> services.hello.image = lib.localImageRef images.hello;
> };
> };
«derivation /nix/store/03j4v567fdvjfcjz177ciz2jk96rb4g6-composix.drv»
```
## A [brasklapp](https://en.wiktionary.org/wiki/brasklapp) to end with
This was a project initially created over a weekend, and the code quality reflects this. If you are interested in a project that does something similar way better, check out [Arion from Hercules CI](https://docs.hercules-ci.com/arion/), it's really cool.

While I have attempted to write as cleanly as possible, I have not attempted to test this against different use cases besides my own, and bugs may arise for other configurations. I am quite new to Nix and this is the first "project" I have written in it. I may add more features and fix flaws if *I need it*, but otherwise nothing will change, but may also change drastically if I require it. I will of course enthusiastically accept any in-spirit improvements others make.
