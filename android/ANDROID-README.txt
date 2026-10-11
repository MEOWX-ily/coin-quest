ILYSHOOT for Android
====================

This project packages the Pygame game as an Android APK. It includes
on-screen movement, jump, and fire controls for touchscreens.

Build requirements
------------------
Build the APK on Linux (Ubuntu is recommended) with Java, the Android SDK/NDK,
and Buildozer installed. Buildozer does not build Android APKs directly on
Windows. The first build downloads the Android build tools and may take a while.

Build
-----
1. Copy this folder to a Linux computer, or into an Ubuntu WSL environment.
2. Open a terminal in this folder.
3. Install Buildozer if it is not already installed:
       python3 -m pip install --user buildozer
4. Build a debug APK:
       buildozer android debug
5. Find the APK in the generated bin/ folder and copy it to your Android phone.
6. Open the APK on the phone to install it. Android may ask you to allow
   installation from that source.

The generated debug APK is for testing and sideloading; it is not a Play Store
release. A signed release build is required for publishing.

Controls
--------
Use the left and right buttons to move, JUMP to jump, and FIRE to shoot.
The keyboard controls remain available on desktop.
