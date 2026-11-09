#!/bin/bash
# Pipeline completo, retomável. Uso: ./run_all.sh
cd "$(dirname "$0")"; export PYTHONPATH=src; PY=.venv/bin/python
for i in 1 2; do $PY -m reqgen.cli generate; done
$PY -m reqgen.cli judge --fidelity
$PY -m reqgen.cli judge --fidelity
for g in deepseek-v4.1-flash gpt-6-luna claude-haiku-5.5; do $PY -m reqgen.cli multiagent --gen $g; done
$PY -m reqgen.cli analyze --ma
$PY -m reqgen.cli plots
echo PIPELINE_DONE
