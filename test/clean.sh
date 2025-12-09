#!/bin/bash

# Print what we're about to do
echo "This script will delete everything in the current directory EXCEPT:"
echo "- run_spot"
echo "- run_rapid"
echo "- clean.sh (this script)"
echo ""
echo "Press Enter to continue or Ctrl+C to abort..."
read

# Find and delete all regular files except the ones we want to keep
echo "Removing files..."
find . -maxdepth 1 -type f ! -name "run_spot" ! -name "run_rapid" ! -name "clean.sh" -print -delete

# Find and delete all directories
echo "Removing directories and their contents..."
find . -maxdepth 1 -type d ! -name "." ! -name ".." -print -exec rm -rf {} \;

echo "Cleanup complete. Only 'run_spot', 'run_rapid', and 'clean.sh' remain."
