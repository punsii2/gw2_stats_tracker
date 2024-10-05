{
  description = "statistics tracker aimed at gw2 gvgs";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs = { self, nixpkgs, treefmt-nix }:

    let
      system = "x86_64-linux";
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
        inherit system;
      };
      pythonEnv = pkgs.python3.withPackages (
        ps: with ps; [
          debugpy
          plotly
          streamlit
        ]
      );

      streamlitRun = pkgs.writeShellApplication {
        name = "streamlitRun";
        runtimeInputs = [ pythonEnv ];
        text = "${pythonEnv}/bin/python3 -m streamlit run app.py";
      };
    in
    {
      apps.${system} = {
        default = {
          type = "app";
          program = "${streamlitRun}/bin/streamlitRun";
        };
      };

      devShells.${system} = {
        default = pkgs.mkShell {
          buildInputs = with pkgs; [
            treefmtEval.config.build.wrapper

            pythonEnv

            # tools
            black
            pylint
            pyright
            ruff
          ];
        };
      };

      formatter.${system} = treefmtEval.config.build.wrapper;
    };
}

