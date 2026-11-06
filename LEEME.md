# Inventario Peatonal Univalle - Fase 1 (lectura del receptor)

Esta fase solo muestra el estado del E300 Pro por WiFi. Sirve para comprobar la conexión antes de agregar el formulario.

## Obtener el APK (sin instalar nada)
1. Crea una cuenta en github.com y un repositorio nuevo (privado o público), por ejemplo `inventario-peatonal`.
2. Sube el contenido de esta carpeta: "Add file" > "Upload files" y arrastra los archivos y carpetas.
3. El archivo `.github/workflows/apk.yml` es obligatorio. Si el arrastre no sube la carpeta `.github`, usa "Add file" > "Create new file", escribe `.github/workflows/apk.yml` como nombre y pega el contenido.
4. Abre la pestaña "Actions" > "Compilar APK" > "Run workflow". Tarda unos 5 a 10 minutos.
5. Al terminar, entra a la ejecución y descarga `inventario-peatonal-apk` (queda en un .zip con `app-debug.apk`).
6. Pásalo al móvil e instálalo (hay que permitir "instalar apps desconocidas").

## Si falla la compilación
Copia el texto del error del paso que salió en rojo y envíamelo.
