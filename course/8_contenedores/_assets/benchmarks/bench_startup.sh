#!/bin/bash
# bench_startup.sh — Mide latencia de arranque de contenedores (LAUNCH cost)
# Prueba: Docker vs Podman x Ubuntu vs Alpine + bare metal baseline
# Uso: bash bench_startup.sh [repeticiones]
# Salida: results/exp1_startup.csv
# Imagenes pineadas a ubuntu:24.04 y alpine:3.20, los tags exactos con los que se
# midio el CSV publicado. Sin tag fijo el benchmark no es reproducible: ubuntu:latest
# ya apunta a 26.04, y alpine:latest se mueve varias veces al ano.
set -e

REPS=${1:-10}
# La columna image del CSV guarda el nombre corto (ubuntu, alpine); el tag va aparte.
IMAGES=("ubuntu:24.04" "alpine:3.20")
OUTFILE="results/exp1_startup.csv"
mkdir -p results

echo "runtime,image,rep,startup_ms" > "$OUTFILE"

echo "=== Exp 1: Startup Latency ($REPS reps + 1 warm-up) ==="

# --- Bare metal baseline ---
echo "Midiendo bare metal..."
# Warm-up (descartado)
echo ok > /dev/null
for i in $(seq 1 "$REPS"); do
    start_ns=$(date +%s%N)
    echo ok > /dev/null
    end_ns=$(date +%s%N)
    ms=$(echo "scale=2; ($end_ns - $start_ns) / 1000000" | bc)
    echo "bare,none,$i,$ms" >> "$OUTFILE"
done
echo "  bare metal: listo"

# --- Docker ---
if command -v docker &>/dev/null; then
    for ref in "${IMAGES[@]}"; do
        image="${ref%%:*}"
        echo "Midiendo Docker + $ref..."
        docker pull -q "$ref" > /dev/null 2>&1 || true
        # Warm-up (descartado)
        docker run --rm "$ref" echo ok > /dev/null 2>&1
        for i in $(seq 1 "$REPS"); do
            start_ns=$(date +%s%N)
            docker run --rm "$ref" echo ok > /dev/null 2>&1
            end_ns=$(date +%s%N)
            ms=$(echo "scale=2; ($end_ns - $start_ns) / 1000000" | bc)
            echo "docker,$image,$i,$ms" >> "$OUTFILE"
        done
        echo "  docker/$image: listo"
    done
else
    echo "  docker: no disponible, saltando"
fi

# --- Podman ---
if command -v podman &>/dev/null; then
    for ref in "${IMAGES[@]}"; do
        image="${ref%%:*}"
        echo "Midiendo Podman + $ref..."
        podman pull -q "$ref" > /dev/null 2>&1 \
            || podman pull -q "docker.io/library/$ref" > /dev/null 2>&1 || true
        # Warm-up (descartado)
        podman run --rm "$ref" echo ok > /dev/null 2>&1
        for i in $(seq 1 "$REPS"); do
            start_ns=$(date +%s%N)
            podman run --rm "$ref" echo ok > /dev/null 2>&1
            end_ns=$(date +%s%N)
            ms=$(echo "scale=2; ($end_ns - $start_ns) / 1000000" | bc)
            echo "podman,$image,$i,$ms" >> "$OUTFILE"
        done
        echo "  podman/$image: listo"
    done
else
    echo "  podman: no disponible, saltando"
fi

echo "Resultados guardados en $OUTFILE"
