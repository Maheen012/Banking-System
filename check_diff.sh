# =========================================================
# Script: check_diff.sh
# Purpose: Compare actual outputs from frontend_main.py 
#          against expected outputs.
#
# How it works:
#   - Checks the daily transaction files (.atf) against expected (.etf).
#   - Checks the terminal log files (.out) against expected.
#   - Prints whether each test PASSED or FAILED along with the differences, if failed.
#
# How to run:
#   chmod +x check_diff.sh
#   ./check_diff.sh
#
# Required files/directories:
#   - outputs/*.out           actual terminal log files
#   - expected/*.out          expected terminal log files
# =========================================================

#!/bin/bash

# Check terminal logs
for file in expected/*.out
do
    base=$(basename "$file" .out)
    echo "Checking terminal log for test $base..."
    diff outputs/$base.out expected/$base.out
    if [ $? -eq 0 ]; then
        echo "Terminal log $base PASSED"
    else
        echo "Terminal log $base FAILED"
    fi
    echo "----------------------------------"

done

echo "Validation complete."