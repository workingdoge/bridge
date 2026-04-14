{ config, lib, ... }:
let
  cfg = config.services.bridgeSidecar;
in
{
  options.services.bridgeSidecar = {
    enable = lib.mkEnableOption "bridge provider sidecar";

    package = lib.mkOption {
      type = lib.types.package;
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
          "--catalog"
          (toString cfg.providerCatalog)
          "--deployment"
          (toString cfg.deploymentProfile)
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
