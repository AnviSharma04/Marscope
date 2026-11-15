#!/usr/bin/env bash
# Run once: generates Android scaffolding, adds permissions, installs deps.
set -e
cd "$(dirname "$0")/backend" && pip install -r requirements.txt && cd ../app
flutter create --platforms=android --project-name marscope --org app.marscope .
M=android/app/src/main/AndroidManifest.xml
grep -q INTERNET $M || sed -i 's#<application#<uses-permission android:name="android.permission.INTERNET"/>\n    <application android:usesCleartextTraffic="true"#' $M
flutter pub get
echo "Start backend:  python backend/app.py"
echo "Run app:        cd app && flutter run   (physical phone: flutter run --dart-define=API=http://<PC-IP>:5000)"
