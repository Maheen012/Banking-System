# =========================================================
# Script: run_tests.sh
# Purpose: Automatically run the frontend_main.py program
#          on all test input files and generate output files.
#
# How it works:
#   - Reads each .txt file in the 'inputs/' directory.
#   - Runs the Python ATM frontend program for each input.
#   - Saves the daily transaction file (.atf) in 'outputs/'.
#   - Saves the terminal log (.out) in 'outputs/'.
#
# How to run:
#   chmod +x run_tests.sh
#   ./run_tests.sh
#
# Required files/directories:
#   - frontend_main.py         main Python program
#   - inputs/.txt              test input files
#   - current_accounts.txt     current bank account file
#   - outputs/                 directory where outputs will be stored
# =========================================================

#!/bin/bash

# Create outputs directory if it doesn't exist
mkdir -p outputs

# Loop through all test input files
for file in inputs/*.txt
do
    base=$(basename "$file" .txt)

    echo "Running test $base..."


    python frontend_main.py current_accounts.txt outputs/$base.atf < "$file" > outputs/$base.out

    # Compare output to expected result
    if [ -f expected/$base.etf ]; then
        if diff -q outputs/$base.atf expected/$base.etf > /dev/null; then
            echo "$base: PASS"
        else
            echo "$base: FAIL"
            diff outputs/$base.atf expected/$base.etf
        fi
    else
        echo "No expected output for $base, skipping comparison."
    fi

done

echo "All tests executed."
