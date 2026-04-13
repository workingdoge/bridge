{ config, lib, pkgs, ... }:
let
  cfg = config.launchd.daemons.bridge-sidecar;
in
{
  launchd.daemons.bridge-sidecar = {
    serviceConfig = {
      ProgramArguments = [
        "/usr/local/bin/bridge-sidecar"
        "--catalog" "/etc/bridge/provider-catalog.json"
        "--deployment" "/etc/bridge/deployment-profile.json"
      ];
      KeepAlive = true;
      RunAtLoad = true;
      StandardOutPath = "/var/log/bridge-sidecar.out.log";
      StandardErrorPath = "/var/log/bridge-sidecar.err.log";
      WorkingDirectory = "/var/lib/bridge-sidecar";
    };
  };
}
