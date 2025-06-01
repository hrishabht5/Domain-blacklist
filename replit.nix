{ pkgs }: {
  deps = [
    pkgs.firefox
    pkgs.geckodriver
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
  ];
}
