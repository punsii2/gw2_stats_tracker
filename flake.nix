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
      pyPkgs = pythonPackages: with pythonPackages; [
        debugpy
        plotly
      ];

      streamlitRun = pkgs.writeShellApplication {
        name = "streamlitRun";
        runtimeInputs = with pkgs; [
          (python3.withPackages pyPkgs)
          streamlit
        ];
        text = "${pkgs.streamlit}/bin/streamlit run app.py";
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

      formatter.${system} = treefmtEval.config.build.wrapper;
    };
}

