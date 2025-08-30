@echo off
REM Script de comandos para EDUFACE
REM Facilita las tareas comunes de desarrollo

echo.
echo ===============================================
echo           EDUFACE - Sistema de Asistencia
echo ===============================================
echo.

:menu
echo Selecciona una opcion:
echo.
echo [1] Iniciar servidor de desarrollo
echo [2] Limpiar archivos innecesarios
echo [3] Instalar dependencias
echo [4] Ver estructura del proyecto
echo [5] Crear backup
echo [6] Docker - Construir imagen
echo [7] Docker - Ejecutar contenedor
echo [8] Docker - Detener contenedor
echo [9] Salir
echo.
set /p choice="Ingresa tu opcion (1-9): "

if "%choice%"=="1" goto start_server
if "%choice%"=="2" goto clean_project
if "%choice%"=="3" goto install_deps
if "%choice%"=="4" goto show_structure
if "%choice%"=="5" goto create_backup
if "%choice%"=="6" goto docker_build
if "%choice%"=="7" goto docker_run
if "%choice%"=="8" goto docker_stop
if "%choice%"=="9" goto exit
goto menu

:start_server
echo.
echo 🚀 Iniciando servidor de desarrollo...
echo URL: http://127.0.0.1:8002
echo Presiona Ctrl+C para detener
echo.
.\.venv_clean\Scripts\python.exe -m uvicorn app.main:app --reload --port 8002
goto menu

:clean_project
echo.
echo 🧹 Limpiando archivos innecesarios...
.\.venv_clean\Scripts\python.exe clean.py
echo.
pause
goto menu

:install_deps
echo.
echo 📦 Instalando dependencias...
.\.venv_clean\Scripts\python.exe -m pip install -r requirements.txt
echo.
echo ✅ Dependencias instaladas correctamente
pause
goto menu

:show_structure
echo.
echo 📁 Estructura del proyecto:
echo.
tree /F /A
echo.
pause
goto menu

:create_backup
echo.
echo 💾 Creando backup del proyecto...
set backup_name=EDUFACE_backup_%date:~-4,4%-%date:~-10,2%-%date:~-7,2%_%time:~0,2%-%time:~3,2%
set backup_name=%backup_name: =%
echo Nombre del backup: %backup_name%
powershell Compress-Archive -Path "." -DestinationPath "../%backup_name%.zip" -Exclude ".venv*", "__pycache__", "*.pyc", "*.log"
echo ✅ Backup creado: %backup_name%.zip
pause
goto menu

:docker_build
echo.
echo 🐳 Construyendo imagen Docker...
docker build -t eduface:latest .
echo.
echo ✅ Imagen Docker construida: eduface:latest
pause
goto menu

:docker_run
echo.
echo 🚀 Ejecutando contenedor Docker...
echo URL: http://localhost:8002
echo Presiona Ctrl+C para detener
echo.
docker-compose up -d
echo ✅ Contenedor iniciado
echo Para ver logs: docker-compose logs -f
pause
goto menu

:docker_stop
echo.
echo 🛑 Deteniendo contenedor Docker...
docker-compose down
echo ✅ Contenedor detenido
pause
goto menu

:exit
echo.
echo 👋 ¡Hasta luego!
echo.
pause
exit
