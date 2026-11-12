#!/usr/bin/env bash
# Usage: bash collect_evidence.sh <your-name>/loan-api:1.0.0
# Runs common checks and saves the commands and their output to evidence.txt.
# Paste the parts you need into CHECKLIST.md (match them to your requirements table).
IMAGE="${1:?Usage: bash collect_evidence.sh <name>/loan-api:1.0.0}"
OUT=evidence.txt
: > "$OUT"

run() {
  echo "### \$ $*" | tee -a "$OUT"
  "$@" 2>&1 | tee -a "$OUT"
  echo | tee -a "$OUT"
}

run docker images "$IMAGE"
run docker run --rm --entrypoint id "$IMAGE"
run docker run --rm --entrypoint env "$IMAGE"
run docker history --no-trunc=false "$IMAGE"

echo "### start the container and check the health check" | tee -a "$OUT"
docker rm -f loan-evidence >/dev/null 2>&1
docker run -d --name loan-evidence -p 8000:8000 "$IMAGE" | tee -a "$OUT"
sleep 15
run docker inspect --format "health: {{.State.Health.Status}}" loan-evidence
run curl -s http://localhost:8000/health
run curl -s -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d '{"amount_usd":1500,"term_months":12,"monthly_income_usd":400}'
docker rm -f loan-evidence >/dev/null 2>&1

if command -v trivy >/dev/null 2>&1; then
  run trivy image --severity HIGH,CRITICAL "$IMAGE"
else
  echo "trivy not installed: install it (see your lesson) and run: trivy image --severity HIGH,CRITICAL $IMAGE" | tee -a "$OUT"
fi
echo "Saved to $OUT"
