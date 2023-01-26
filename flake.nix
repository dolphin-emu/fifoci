{
  description = "Continuous integration service running Dolphin FIFO logs to find graphics rendering regressions.";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";
  inputs.poetry2nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, flake-utils, poetry2nix }: {
    overlay = nixpkgs.lib.composeManyExtensions [
      poetry2nix.overlay
      (final: prev: {
        fifoci-frontend = prev.poetry2nix.mkPoetryApplication {
          src = prev.poetry2nix.cleanPythonSources { src = ./.; };
          projectDir = fifoci/frontend;

          sourceRoot = "source/fifoci/frontend";
        };

        fifoci-runner = prev.poetry2nix.mkPoetryApplication {
          src = prev.poetry2nix.cleanPythonSources { src = ./.; };
          projectDir = fifoci/runner;

          sourceRoot = "source/fifoci/runner";
        };
      })
    ];
  } // (flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ self.overlay ];
      };
    in rec {
      packages = { inherit (pkgs) fifoci-frontend fifoci-runner; };
      defaultPackage = pkgs.fifoci-runner;

      devShells.default = with pkgs; mkShell {
        buildInputs = [ dolphin-emu-beta pngcrush poetry postgresql ];
      };
    }
  ));
}
