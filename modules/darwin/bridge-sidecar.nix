{ self }:
{ config, lib, pkgs, ... }:
let
  cfg = config.services.bridgeSidecar;
in
{
  options.services.bridgeSidecar = {
    enable = lib.mkEnableOption "bridge provider sidecar";

    package = lib.mkOption {
      type = lib.types.package;
      default = self.packages.${pkgs.stdenv.hostPlatform.system}.bridgeSidecar;
      defaultText = lib.literalExpression "inputs.bridge.packages.${pkgs.stdenv.hostPlatform.system}.bridgeSidecar";
      description = "Package providing the bridge-sidecar binary.";
    };

    providerCatalog = lib.mkOption {
      type = lib.types.path;
      description = "Path to provider catalog JSON.";
    };

    deploymentProfile = lib.mkOption {
      type = lib.types.path;
      description = "Path to deployment profile JSON.";
    };

    attestationResult = lib.mkOption {
      type = lib.types.path;
      description = "Path to authoritative attestation result JSON.";
    };

    revocationSnapshot = lib.mkOption {
      type = lib.types.path;
      description = "Path to authoritative revocation snapshot JSON.";
    };

    modeState = lib.mkOption {
      type = lib.types.path;
      description = "Path to current mode state JSON.";
    };

    listenAddress = lib.mkOption {
      type = lib.types.str;
      default = "127.0.0.1";
      description = "Listen address for the reference sidecar.";
    };

    listenPort = lib.mkOption {
      type = lib.types.port;
      default = 8181;
      description = "Listen port for the reference sidecar.";
    };

    auditLogPath = lib.mkOption {
      type = lib.types.str;
      default = "/var/lib/bridge-sidecar/audit-events.jsonl";
      description = "Audit log path used by the reference sidecar.";
    };

    workingDirectory = lib.mkOption {
      type = lib.types.str;
      default = "/var/lib/bridge-sidecar";
      description = "Working directory for the launchd daemon.";
    };

    stdoutPath = lib.mkOption {
      type = lib.types.str;
      default = "/var/log/bridge-sidecar.out.log";
      description = "Path for launchd stdout.";
    };

    stderrPath = lib.mkOption {
      type = lib.types.str;
      default = "/var/log/bridge-sidecar.err.log";
      description = "Path for launchd stderr.";
    };
  };

  config = lib.mkIf cfg.enable {
    launchd.daemons.bridge-sidecar = {
      serviceConfig = {
        ProgramArguments = [
          "${cfg.package}/bin/bridge-sidecar"
          "--catalog" (toString cfg.providerCatalog)
          "--deployment" (toString cfg.deploymentProfile)
          "--attestation" (toString cfg.attestationResult)
          "--revocation" (toString cfg.revocationSnapshot)
          "--mode" (toString cfg.modeState)
          "--listen" "${cfg.listenAddress}:${toString cfg.listenPort}"
          "--audit-log" cfg.auditLogPath
        ];
        KeepAlive = true;
        RunAtLoad = true;
        StandardOutPath = cfg.stdoutPath;
        StandardErrorPath = cfg.stderrPath;
        WorkingDirectory = cfg.workingDirectory;
      };
    };
  };
}
