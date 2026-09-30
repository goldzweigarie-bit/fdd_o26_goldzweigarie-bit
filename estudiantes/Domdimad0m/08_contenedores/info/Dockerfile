# Imagen base: ubuntu 24.04
FROM ubuntu:24.04
ARG BUILD_DATE
ENV BUILD_DATE=$BUILD_DATE

# Crear directorio de trabajo
WORKDIR /app

# Copiar el script al contenedor
COPY info.sh .

# Dar permisos de ejecución
RUN chmod +x info.sh

# Ejecutar el script al arrancar
CMD ["./info.sh"]
