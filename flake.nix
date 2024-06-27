{
  description = "statistics tracker aimed at gw2 gvgs";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs = { self, nixpkgs, treefmt-nix }:

    let
      treefmtEval = treefmt-nix.lib.evalModule pkgs
        {
          # Used to find the project root
          projectRootFile = "flake.nix";

          programs = {
            black.enable = true;
            isort.enable = true;
            prettier.enable = true;
            nixpkgs-fmt.enable = true;
          };
        };

      pkgs = import nixpkgs {
        system = "x86_64-linux";
      };
      pyPkgs = pythonPackages: with pythonPackages; [
        debugpy
        plotly
      ];
    in
    {
      formatter.x86_64-linux = treefmtEval.config.build.wrapper;

      devShells.x86_64-linux = {
        default = pkgs.mkShell {
          buildInputs = with pkgs; [
            treefmtEval.config.build.wrapper

            (python3.withPackages pyPkgs)
            streamlit

            # tools
            black
            pylint
            pyright
            ruff
          ];
        };
      };
    };
}
