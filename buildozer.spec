[app]
title = Mia App
package.name = miaapp
package.domain = com.esempio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1

[buildozer]
log_level = 2

[app:android]
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
