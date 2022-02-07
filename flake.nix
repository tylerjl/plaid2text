{
  description = "plaid2text";
  inputs = {
    nixpkgs.url     = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    devshell.url    = "github:numtide/devshell";
    poetry2nix.url  = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, devshell, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        config = { allowUnfree = true; };
        overlays = [ devshell.overlay poetry2nix.overlay ];
      };
      app = pkgs.poetry2nix.mkPoetryEnv {
        projectDir = ./.;
      };
    in {
      devShell = app.env.overrideAttrs (old: {
        buildInputs = with pkgs ; [ poetry gcc pyright ];
        shellHook = ''
           export PYTHONPATH="./src/python"
        '';
      });
    });
}
