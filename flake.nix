{
  description = "text-contextifyer dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python311
            poetry
            docker
            minikube
            kubectl
          ];

          shellHook = ''
            export POETRY_VIRTUALENVS_IN_PROJECT=true
            echo "Run 'poetry install' to set up the project."
          '';
        };
      });
}
