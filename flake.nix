{
  description = "BuchDashboard";

  inputs = {
    # Import the Nixpkgs repository, which contains the Python environment and packages
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    # This brings in the flake-utils to help with the build process
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachSystem [
    "x86_64-linux" "aarch64-linux"
  ] (system: {
    # Python development environment with Flask
    devShell = nixpkgs.legacyPackages.${system}.mkShell {
      buildInputs = with nixpkgs.legacyPackages.${system}; [
        python3
        python3Packages.flask
        python3Packages.pip
      ];

      shellHook = ''
	exec zsh
      '';
    };

    # Python package with Flask
    packages.default = nixpkgs.legacyPackages.${system}.python3Packages.buildPythonPackage rec {
      pname = "buchdashboard";
      version = "1.0";

      src = ./.;

      nativeBuildInputs = [ nixpkgs.legacyPackages.${system}.python3Packages.setuptools ];

      meta = with nixpkgs.lib; {
        description = "buchdashboard";
        license = licenses.mit;
        platforms = platforms.all;
      };
    };
  });
}

