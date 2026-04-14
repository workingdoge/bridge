{
  description = "bridge: canonical bridge and secret domain contracts with repo-owned conformance surfaces";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [
        "aarch64-darwin"
        "x86_64-darwin"
        "aarch64-linux"
        "x86_64-linux"
      ];

      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f system);
    in
    {
      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt-rfc-style);

      nixosModules = {
        bridgeSidecar = import ./modules/nixos/bridge-sidecar.nix;
      };

      darwinModules = {
        bridgeSidecar = import ./modules/darwin/bridge-sidecar.nix;
      };

      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonEnv = pkgs.python3.withPackages (ps: with ps; [ jsonschema hypothesis ]);

          bridgeConformanceCheck = pkgs.writeShellApplication {
            name = "bridge-conformance-check";
            runtimeInputs = [
              pkgs.jq
              pkgs.python3Minimal
              pkgs.ripgrep
            ];
            text = ''
              exec ${./scripts/bridge-conformance-check.sh} --repo ${self} "$@"
            '';
          };

          bridgePropertyCheck = pkgs.writeShellApplication {
            name = "bridge-property-check";
            runtimeInputs = [ pythonEnv ];
            text = ''
              exec ${./scripts/bridge-property-check.sh} --repo ${self} "$@"
            '';
          };

          referencePlanner = pkgs.writeShellApplication {
            name = "reference-planner";
            runtimeInputs = [ pythonEnv ];
            text = ''
              exec python3 ${./specs/secrets/secret-0002/python/reference_planner.py} "$@"
            '';
          };
        in
        {
          inherit bridgeConformanceCheck bridgePropertyCheck referencePlanner;
          default = bridgeConformanceCheck;
        });

      apps = forAllSystems (system: {
        bridge-conformance-check = {
          type = "app";
          program = "${self.packages.${system}.bridgeConformanceCheck}/bin/bridge-conformance-check";
        };
        bridge-property-check = {
          type = "app";
          program = "${self.packages.${system}.bridgePropertyCheck}/bin/bridge-property-check";
        };
        reference-planner = {
          type = "app";
          program = "${self.packages.${system}.referencePlanner}/bin/reference-planner";
        };
        default = self.apps.${system}.bridge-conformance-check;
      });

      checks = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          bridge-conformance-check = pkgs.runCommand "bridge-conformance-check" {
            nativeBuildInputs = [ self.packages.${system}.bridgeConformanceCheck ];
          } ''
            bridge-conformance-check >/dev/null
            touch "$out"
          '';

          bridge-property-check = pkgs.runCommand "bridge-property-check" {
            nativeBuildInputs = [ self.packages.${system}.bridgePropertyCheck ];
          } ''
            bridge-property-check >/dev/null
            touch "$out"
          '';

          reference-planner-help = pkgs.runCommand "reference-planner-help" {
            nativeBuildInputs = [ self.packages.${system}.referencePlanner ];
          } ''
            reference-planner --help >/dev/null
            touch "$out"
          '';
        });

      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonEnv = pkgs.python3.withPackages (ps: with ps; [ jsonschema hypothesis ]);
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.jq
              pkgs.python3Minimal
              pythonEnv
              pkgs.ripgrep
            ];
          };
        });
    };
}
