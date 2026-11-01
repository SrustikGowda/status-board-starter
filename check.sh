#!/bin/bash
if curl -fs example.com >/dev/null
then echo "$(date) UP"
else echo "$(date) DOWN"
fi
