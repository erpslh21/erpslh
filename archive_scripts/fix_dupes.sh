#!/bin/bash
FILES=(
    "app/templates/index_modern.html"
    "app/templates/login_modern.html"
    "app/templates/flock_detail_modern.html"
    "app/templates/offline.html"
    "app/templates/login.html"
    "app/templates/base_tabler.html"
    "app/templates/flock_detail_readonly.html"
)
for file in "${FILES[@]}"; do
    # find lines with multiple class= and consolidate them
    # For simplicity, we can do python script to handle this cleanly
done
