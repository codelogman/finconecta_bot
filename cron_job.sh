#!/bin/bash

# Define el directorio donde se encuentra el script
PROJECT_DIR="/workspace/RISP/challenge"
SCRAPER_SCRIPT="$PROJECT_DIR/scraper.py"
OUTPUT_CSV="$PROJECT_DIR/products.csv"
CRON_JOB="0 8 * * * /usr/bin/python3 $SCRAPER_SCRIPT >> $PROJECT_DIR/scraper.log 2>&1"

# Muestra el inicio de la ejecución
echo "Iniciando el scraper..."

# Verifica que el archivo del scraper existe
if [ ! -f "$SCRAPER_SCRIPT" ]; then
  echo "Error: El archivo scraper.py no existe en el directorio $PROJECT_DIR"
  exit 1
fi

# Ejecuta el scraper manualmente
/usr/bin/python3 $SCRAPER_SCRIPT

# Verifica si el archivo CSV se ha generado
if [ -f "$OUTPUT_CSV" ]; then
  echo "El scraper ha terminado con éxito. Los resultados se guardaron en $OUTPUT_CSV"
else
  echo "Error: No se ha generado el archivo de resultados CSV"
  exit 1
fi

# Agregar el cron job si no está presente
CRON_TAB_EXISTS=$(crontab -l | grep -F "$SCRAPER_SCRIPT")
if [ -z "$CRON_TAB_EXISTS" ]; then
  # Si el cron job no está ya en la lista, agregarlo
  (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  echo "Cron job agregado para ejecutar el scraper diariamente a las 8 AM."
else
  echo "El cron job ya está configurado."
fi

