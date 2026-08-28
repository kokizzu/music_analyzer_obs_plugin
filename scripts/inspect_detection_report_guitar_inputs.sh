#!/bin/sh
set -eu

printf '%s\n' '== existing GuitarSet parser =='
sed -n '1260,1315p' scripts/write_detection_accuracy_report.py
printf '%s\n' '== report input signature =='
sed -n '1685,1715p' scripts/write_detection_accuracy_report.py
sed -n '1715,1765p' scripts/write_detection_accuracy_report.py
sed -n '1765,1825p' scripts/write_detection_accuracy_report.py
printf '%s\n' '== report input loading =='
sed -n '2108,2130p' scripts/write_detection_accuracy_report.py
printf '%s\n' '== GuitarSet report section =='
sed -n '2548,2575p' scripts/write_detection_accuracy_report.py
printf '%s\n' '== parser and invocation =='
sed -n '4778,4795p' scripts/write_detection_accuracy_report.py
sed -n '4868,4890p' scripts/write_detection_accuracy_report.py
sed -n '4890,4965p' scripts/write_detection_accuracy_report.py
