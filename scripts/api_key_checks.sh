#!/usr/bin/env bash
set -u

if [[ -z "${URL:-}" ]]; then
    printf '%s\n' "FAIL: URL is not set" >&2
    exit 2
fi

if [[ -z "${API_KEY:-}" ]]; then
    printf '%s\n' "FAIL: API_KEY is not set" >&2
    exit 2
fi

request_status() {
    local status
    status="$(curl --silent --output /dev/null --write-out '%{http_code}' \
        --max-time 10 --request POST \
        --header 'Content-Type: application/json' \
        --data '{"amount_usd":1500,"term_months":12,"monthly_income_usd":400}' \
        "$@" "$URL" 2>/dev/null)" || status=""
    printf '%s' "${status:-000}"
}

check_status() {
    local name="$1"
    local status="$2"
    local result=FAIL

    case "$name:$status" in
        no-key:401|wrong-key:401|wrong-key:403|valid-key:200) result=PASS ;;
    esac

    printf '%s %s %s\n' "$name" "$status" "$result"
    [[ "$result" == PASS ]]
}

failed=0
check_status no-key "$(request_status)" || failed=1
check_status wrong-key "$(request_status --header "X-API-Key: ${API_KEY}__invalid__")" || failed=1
check_status valid-key "$(request_status --header "X-API-Key: $API_KEY")" || failed=1

exit "$failed"
