#!/usr/bin/env bash

cd $(dirname $0)

protocol=./protocol
ports="$RAMPART_PORT1 $RAMPART_PORT2"

rampart  --verbose --protocol $protocol --ports $ports