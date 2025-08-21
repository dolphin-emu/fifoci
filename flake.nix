{
  description = "Continuous integration service running Dolphin FIFO logs to find graphics rendering regressions.";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";

  inputs.uv2nix.url = "github:pyproject-nix/uv2nix";
  inputs.uv2nix.inputs.nixpkgs.follows = "nixpkgs";
  inputs.uv2nix.inputs.pyproject-nix.follows = "pyproject-nix";

  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";

  inputs.pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";
  inputs.pyproject-build-systems.inputs.nixpkgs.follows = "nixpkgs";
  inputs.pyproject-build-systems.inputs.pyproject-nix.follows = "pyproject-nix";

  outputs = { self, nixpkgs, flake-utils, uv2nix, pyproject-nix, pyproject-build-systems }:
  let
    perSystem = flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Reusable helper: build a Python virtualenv from a uv2nix/pyproject-nix workspace.
        mkVenv =
          { workspaceRoot
          , venvName
          }:
          let
            workspace = uv2nix.lib.workspace.loadWorkspace { inherit workspaceRoot; };
            overlay = workspace.mkPyprojectOverlay {
              sourcePreference = "wheel";
            };
            python = pkgs.python310;
            pythonSet =
              (pkgs.callPackage pyproject-nix.build.packages { inherit python; })
              .overrideScope (pkgs.lib.composeManyExtensions [
                pyproject-build-systems.overlays.default
                overlay
              ]);
          in
            pythonSet.mkVirtualEnv venvName workspace.deps.default;

        frontendVenv = mkVenv { workspaceRoot = ./fifoci/frontend; venvName = "fifoci-frontend-env"; };
        runnerVenv = mkVenv { workspaceRoot = ./fifoci/runner; venvName = "fifoci-runner-env"; };
      in {
        packages.fifoci-frontend = frontendVenv;
        packages.fifoci-runner = runnerVenv;
        packages.default = runnerVenv;

        apps.fifoci-runner = {
          type = "app";
          program = "${runnerVenv}/bin/fifoci-runner";
        };

        apps.fifoci-frontend-manage = {
          type = "app";
          program = "${frontendVenv}/bin/fifoci-frontend-manage";
        };

        devShells.default = with pkgs; mkShell {
          packages = [ dolphin-emu-beta pngcrush postgresql sqlite uv ];
        };
      });
  in
    perSystem // {
      overlays.default = final: prev: {
        fifoci-frontend = self.packages.${final.system}.fifoci-frontend;
        fifoci-runner = self.packages.${final.system}.fifoci-runner;
      };
      overlay = self.overlays.default;
    };
}