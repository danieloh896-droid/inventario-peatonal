#!/bin/bash
set -e
mkdir -p www/lib
cp node_modules/leaflet/dist/leaflet.js node_modules/leaflet/dist/leaflet.css www/lib/
cp -r node_modules/leaflet/dist/images www/lib/
cp node_modules/jszip/dist/jszip.min.js node_modules/sql.js/dist/sql-wasm.js node_modules/sql.js/dist/sql-wasm.wasm www/lib/
DEST=android/app/src/main/java/co/edu/univalle/inventariopeatonal
mkdir -p "$DEST"
cp android-overrides/*.java "$DEST"/
M=android/app/src/main/AndroidManifest.xml
sed -i 's#<application#<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />\n    <uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />\n    <application android:usesCleartextTraffic="true"#' "$M"
echo "Manifiesto preparado:"; grep -n -E "ClearText|cleartext|NETWORK_STATE" "$M"

# Icono de la aplicación (si existe la carpeta android-res con los iconos ya generados)
if [ -d android-res ]; then
  cp -r android-res/* android/app/src/main/res/
  echo "Iconos copiados"
fi
