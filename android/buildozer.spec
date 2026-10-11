[app]

title = ILYSHOOT
package.name = ilyshoot
package.domain = org.ilyquest
source.dir = .
source.include_exts = py,txt
version = 1.0.0
requirements = python3,pygame
orientation = landscape
fullscreen = 1

android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
