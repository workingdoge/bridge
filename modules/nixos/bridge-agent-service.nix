{ config, lib, ... }:
let
  cfg = config.services.bridgeAgentService;
  sidecarCfg = config.services.bridgeSidecar;
in
{
  options.services.bridgeAgentService = {
    enable = lib.mkEnableOption "reference workload using the bridge sidecar";

    package = lib.mkOption {
      type = lib.types.package;
      description = "Package providing the reference workload binary.";
    };

    executable = lib.mkOption {
      type = lib.types.str;
      description = "Executable name under package/bin.";
    };

    arguments = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [];
      description = "Additional arguments passed to the workload executable.";
    };

    bridgeFlag = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = "--bridge-url";
      description = "Flag used to pass the bridge URL. Set to null to rely only on BRIDGE_SIDECAR_URL.";
    };

    bridgeUrl = lib.mkOption {
      type = lib.types.str;
      default = "http://${sidecarCfg.listenAddress}:${toString sidecarCfg.listenPort}";
      defaultText = lib.literalExpression ''"http://${config.services.bridgeSidecar.listenAddress}:${toString config.services.bridgeSidecar.listenPort}"'';
      description = "HTTP base URL for the reference bridge sidecar.";
    };

    environment = lib.mkOption {
      type = lib.types.attrsOf lib.types.str;
      default = {};
      description = "Additional environment variables for the workload service.";
    };

    serviceName = lib.mkOption {
      type = lib.types.str;
      default = "bridge-agent";
      description = "Systemd service name for the reference workload.";
    };
  };

  config = lib.mkIf cfg.enable {
    assertions = [
      {
        assertion = sidecarCfg.enable;
        message = "services.bridgeAgentService requires services.bridgeSidecar.enable = true";
      }
    ];

    systemd.services.${cfg.serviceName} = {
      description = "Reference agent workload using bridge sidecar";
      wantedBy = [ "multi-user.target" ];
      after = [ "bridge-sidecar.service" ];
      requires = [ "bridge-sidecar.service" ];
      environment = cfg.environment // {
        BRIDGE_SIDECAR_URL = cfg.bridgeUrl;
      };
      serviceConfig = {
        ExecStart = lib.escapeShellArgs (
          [ "${cfg.package}/bin/${cfg.executable}" ]
          ++ cfg.arguments
          ++ lib.optionals (cfg.bridgeFlag != null) [ cfg.bridgeFlag cfg.bridgeUrl ]
        );
        Restart = "on-failure";
        DynamicUser = true;
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ProtectProc = "invisible";
        CapabilityBoundingSet = "";
        RestrictAddressFamilies = [ "AF_UNIX" "AF_INET" "AF_INET6" ];
      };
    };
  };
}
