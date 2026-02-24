#!/bin/bash

# Create outputs directory if it doesn't exist
mkdir -p outputs

# Loop through all test input files
for file in inputs/*.txt
do
    base=$(basename "$file" .txt)

    echo "Running test $base..."

    python3 frontend_main.py current_accounts.txt outputs/$base.atf \
        < "$file" > outputs/$base.out

done

echo "All tests executed."