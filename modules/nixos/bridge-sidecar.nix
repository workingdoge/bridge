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
  };

  config = lib.mkIf cfg.enable {
    systemd.services.bridge-sidecar = {
      description = "Bridge secret provider sidecar";
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" ];

      serviceConfig = {
        ExecStart = "${cfg.package}/bin/bridge-sidecar --catalog ${cfg.providerCatalog} --deployment ${cfg.deploymentProfile} --attestation ${cfg.attestationResult} --revocation ${cfg.revocationSnapshot} --mode ${cfg.modeState} --listen ${cfg.listenAddress}:${toString cfg.listenPort} --audit-log ${cfg.auditLogPath}";
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
