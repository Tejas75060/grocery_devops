#!/usr/bin/env bash
# Generate CPU load against the app to watch the HPA scale up.
# Run `kubectl -n grocery get hpa -w` in another terminal to observe.
set -euo pipefail
URL="${1:-http://grocery.localhost/api/inventory}"
echo "Hammering $URL — Ctrl-C to stop. Watch: kubectl -n grocery get hpa -w"
kubectl -n grocery run loadgen --rm -it --restart=Never --image=busybox -- \
  /bin/sh -c "while true; do wget -q -O- ${URL} >/dev/null; done"
