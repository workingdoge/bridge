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
        bridgeSidecar = import ./modules/nixos/bridge-sidecar.nix { inherit self; };
        bridgeAgentService = import ./modules/nixos/bridge-agent-service.nix;
      };

      darwinModules = {
        bridgeSidecar = import ./modules/darwin/bridge-sidecar.nix { inherit self; };
      };

      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonEnv = pkgs.python3.withPackages (ps: with ps; [ jsonschema hypothesis ]);
          bridgeSidecarRuntime = pkgs.runCommand "bridge-sidecar-runtime" {} ''
            mkdir -p "$out/share/bridge-sidecar"
            cp -R ${./specs/secrets/secret-0003/python} "$out/share/bridge-sidecar/python"
            cp -R ${./specs/secrets/secret-0003/schemas} "$out/share/bridge-sidecar/schemas"
          '';

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

          bridgeSidecar = pkgs.writeShellApplication {
            name = "bridge-sidecar";
            runtimeInputs = [ pythonEnv ];
            text = ''
              runtime=${bridgeSidecarRuntime}/share/bridge-sidecar
              export PYTHONPATH="$runtime/python''${PYTHONPATH:+:$PYTHONPATH}"
              exec python3 "$runtime/python/reference_sidecar_server.py" --schema-dir "$runtime/schemas" "$@"
            '';
          };
        in
        {
          inherit bridgeConformanceCheck bridgePropertyCheck referencePlanner bridgeSidecar;
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
        bridge-sidecar = {
          type = "app";
          program = "${self.packages.${system}.bridgeSidecar}/bin/bridge-sidecar";
        };
        default = self.apps.${system}.bridge-conformance-check;
      });

      checks = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          bridgeAgentEval = nixpkgs.lib.nixosSystem {
            system = "x86_64-linux";
            modules = [
              self.nixosModules.bridgeSidecar
              self.nixosModules.bridgeAgentService
              ({ pkgs, ... }: {
                system.stateVersion = "25.05";
                services.bridgeSidecar = {
                  enable = true;
                  listenAddress = "127.0.0.1";
                  listenPort = 8181;
                  providerCatalog = ./specs/secrets/secret-0003/examples/example.provider-catalog.json;
                  deploymentProfile = ./specs/secrets/secret-0003/examples/example.deployment-profile.json;
                  attestationResult = ./specs/secrets/secret-0003/examples/example.attestation-result.ok.json;
                  revocationSnapshot = ./specs/secrets/secret-0003/examples/example.revocation-snapshot.clear.json;
                  modeState = ./specs/secrets/secret-0003/examples/example.mode-state.normal.json;
                };
                services.bridgeAgentService = {
                  enable = true;
                  package = pkgs.hello;
                  executable = "hello";
                };
              })
            ];
          };
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

          bridge-sidecar-help = pkgs.runCommand "bridge-sidecar-help" {
            nativeBuildInputs = [ self.packages.${system}.bridgeSidecar ];
          } ''
            bridge-sidecar --help >/dev/null
            touch "$out"
          '';

          bridge-agent-service-eval = pkgs.writeText "bridge-agent-service-execstart" (
            bridgeAgentEval.config.systemd.services.bridge-agent.serviceConfig.ExecStart + "\n"
          );
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
