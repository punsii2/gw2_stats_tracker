{
  description = "statistics tracker aimed at gw2 gvgs";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-23.05";

  outputs = { self, nixpkgs }:
    let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
      };
      pyPkgs = pythonPackages: with pythonPackages; [
        debugpy
        plotly
      ];
    in
    {
      devShells.x86_64-linux = {
        default = pkgs.mkShell {
          buildInputs = with pkgs; [
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
