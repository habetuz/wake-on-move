{
  description = "An empty flake template that you can adapt to your own environment";

  # Flake inputs
  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1"; # unstable Nixpkgs

  # Flake outputs
  outputs =
    { self, ... }@inputs:

    let
      # The systems supported for this flake
      supportedSystems = [
        "x86_64-linux" # 64-bit Intel/AMD Linux
        "aarch64-linux" # 64-bit ARM Linux
        "x86_64-darwin" # 64-bit Intel macOS
        "aarch64-darwin" # 64-bit ARM macOS
      ];

      # Helper to provide system-specific attributes
      forEachSupportedSystem =
        f:
        inputs.nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import inputs.nixpkgs { inherit system; };
          }
        );
    in
    {
      devShells = forEachSupportedSystem (
        { pkgs }:
        {
          default = pkgs.mkShellNoCC {
            # The Nix packages provided in the environment
            # Add any you need here
            packages = with pkgs; [
              uv
              black
              # System libraries required by OpenCV
              xorg.libxcb
              xorg.libX11
              xorg.libXext
              libGL
              glib
              stdenv.cc.cc.lib
              # Qt libraries for cv2.imshow (--show-video)
              qt5.qtbase
              qt5.qtwayland
              xorg.libXi
              xorg.libXrender
              xorg.libXrandr
              xorg.libXcursor
              xorg.libXinerama
              xorg.libXtst
              xorg.xcbutil
              xorg.xcbutilimage
              xorg.xcbutilkeysyms
              xorg.xcbutilrenderutil
              xorg.xcbutilwm
              fontconfig
              freetype
            ];

            # Set any environment variables for your dev shell
            env = {
              LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
                pkgs.stdenv.cc.cc
                pkgs.xorg.libxcb
                pkgs.xorg.libX11
                pkgs.xorg.libXext
                pkgs.libGL
                pkgs.glib
                pkgs.qt5.qtbase
                pkgs.qt5.qtwayland
                pkgs.xorg.libXi
                pkgs.xorg.libXrender
                pkgs.xorg.libXrandr
                pkgs.xorg.libXcursor
                pkgs.xorg.libXinerama
                pkgs.xorg.libXtst
                pkgs.xorg.xcbutil
                pkgs.xorg.xcbutilimage
                pkgs.xorg.xcbutilkeysyms
                pkgs.xorg.xcbutilrenderutil
                pkgs.xorg.xcbutilwm
                pkgs.fontconfig
                pkgs.freetype
              ];
              QT_PLUGIN_PATH = "${pkgs.qt5.qtbase}/lib/qt-${pkgs.qt5.qtbase.version}/plugins";
              QT_QPA_PLATFORM_PLUGIN_PATH = "${pkgs.qt5.qtbase}/lib/qt-${pkgs.qt5.qtbase.version}/plugins/platforms";
              # Force X11 backend for Qt/OpenCV
              QT_QPA_PLATFORM = "xcb";
            };

            # Add any shell logic you want executed any time the environment is activated
            shellHook = ''
              echo "Development environment loaded with OpenCV dependencies"
            '';
          };
        }
      );
    };
}