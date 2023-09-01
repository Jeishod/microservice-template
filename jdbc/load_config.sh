#! /usr/bin/env sh

until curl -s ${KAFKA_CONNECT_HOST} >/dev/null && echo "# =======================               Success!              ======================= #" ; do
  >&2 echo "# =======================   Waiting for service to connect..  ======================= #"
  sleep 2
done
envsubst < /configs/config.json > /root/sconfig.json
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" "${KAFKA_CONNECT_HOST}/connectors/" -d @/jdbc_sink/jdbc-config.json
