# Imagen base: ubuntu 24.04
FROM ubuntu:24.04

# Crear directorio de trabajo
WORKDIR /app

# Copiar el script al contenedor
COPY info.sh .

# Dar permisos de ejecución
RUN chmod +x info.sh && date -u "+%Y-%m-%d %H:%M UTC" > /app/construida.txt

# Ejecutar el script al arrancar
CMD ["./info.sh"]