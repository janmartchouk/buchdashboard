{
  description = "BuchDashboard";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;
        pythonPackages = python.pkgs;
      in {
        # Dev shell for development
        devShell = pkgs.mkShell {
          buildInputs = with pythonPackages; [
            flask
            waitress
            pip
            requests
            beautifulsoup4
          ];

          shellHook = ''exec zsh'';
        };

        # Properly build Python application
        packages.default = pythonPackages.buildPythonApplication rec {
          pname = "buchdashboard";
          version = "1.0";
          src = ./.;

          # Runtime dependencies
          propagatedBuildInputs = with pythonPackages; [
            flask
            waitress
            requests
            beautifulsoup4
          ];

          # Disable automatic tests
          doCheck = false;

          meta = with pkgs.lib; {
            description = "buchdashboard";
            license = licenses.mit;
            platforms = platforms.all;
          };
        };
      }
    );
}

