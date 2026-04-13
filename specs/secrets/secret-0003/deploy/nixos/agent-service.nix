{ config, lib, pkgs, ... }:
{
  systemd.services.example-agent = {
    description = "Example agent workload using bridge sidecar";
    wantedBy = [ "multi-user.target" ];
    after = [ "bridge-sidecar.service" ];
    serviceConfig = {
      ExecStart = "${pkgs.bash}/bin/bash -lc 'exec /run/current-system/sw/bin/example-agent --bridge unix:///run/bridge-sidecar/bridge.sock'";
      Restart = "on-failure";
      DynamicUser = true;
      NoNewPrivileges = true;
      PrivateTmp = true;
      ProtectSystem = "strict";
      ProtectHome = true;
      ProtectProc = "invisible";
      CapabilityBoundingSet = "";
      RestrictAddressFamilies = [ "AF_UNIX" ];
    };
  };
}
