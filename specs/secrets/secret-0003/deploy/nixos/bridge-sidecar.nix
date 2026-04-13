{ config, lib, pkgs, ... }:
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
  };

  config = lib.mkIf cfg.enable {
    systemd.services.bridge-sidecar = {
      description = "Bridge secret provider sidecar";
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" ];
      serviceConfig = {
        ExecStart = "${cfg.package}/bin/bridge-sidecar --catalog ${cfg.providerCatalog} --deployment ${cfg.deploymentProfile}";
        Restart = "on-failure";
        DynamicUser = true;
        NoNewPrivileges = true;
        PrivateTmp = true;
        PrivateDevices = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ProtectControlGroups = true;
        ProtectKernelTunables = true;
        ProtectKernelModules = true;
        ProtectProc = "invisible";
        LockPersonality = true;
        MemoryDenyWriteExecute = true;
        RestrictSUIDSGID = true;
        CapabilityBoundingSet = "";
        RestrictAddressFamilies = [ "AF_UNIX" "AF_INET" "AF_INET6" ];
        RuntimeDirectory = "bridge-sidecar";
        StateDirectory = "bridge-sidecar";
        CacheDirectory = "bridge-sidecar";
      };
    };
  };
}
