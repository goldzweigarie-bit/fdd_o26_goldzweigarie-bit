#!/bin/bash
# bench_oci.sh — Mide el arranque fijando TODO menos el runtime OCI.
# Desarma el mito del "2x": la diferencia Docker/Podman no es velocidad,
# es qué runtime trae cada uno por default (Podman trae crun, Docker runc).
# Misma imagen, mismo comando, misma máquina, misma tanda.
# Uso: bash bench_oci.sh [repeticiones]
# Salida: results/exp5_oci.csv
# Imagen pineada a ubuntu:24.04 por la misma razón que exp3: ubuntu:latest
# ya apunta a 26.04 y cambia el piso de la medición.
set -e

REPS=${1:-20}
OUTFILE="results/exp5_oci.csv"
mkdir -p results

echo "brazo,rep,startup_ms" > "$OUTFILE"

cronometra() {   # cronometra <etiqueta> <comando...>
    local etiqueta="$1"; shift
    local ini fin
    ini=$(date +%s%N)
    "$@" > /dev/null 2>&1
    fin=$(date +%s%N)
    echo "$etiqueta,$rep,$(( (fin - ini) / 1000000 ))" >> "$OUTFILE"
}

echo "=== Exp 5: mismo trabajo, distinto runtime OCI ($REPS reps + warm-up) ==="

# Warm-up: el primer arranque de cada brazo paga cachés frías de page cache.
for rt in crun runc; do
    podman run --rm --runtime "$rt" ubuntu:24.04 echo ok > /dev/null 2>&1 || true
done
docker run --rm ubuntu:24.04 echo ok > /dev/null 2>&1 || true

for rep in $(seq 1 "$REPS"); do
    if command -v podman &>/dev/null; then
        command -v crun &>/dev/null && cronometra podman-crun podman run --rm --runtime crun ubuntu:24.04 echo ok
        command -v runc &>/dev/null && cronometra podman-runc podman run --rm --runtime runc ubuntu:24.04 echo ok
    fi
    command -v docker &>/dev/null && cronometra docker-runc docker run --rm ubuntu:24.04 echo ok
done

echo "Resultados guardados en $OUTFILE"
