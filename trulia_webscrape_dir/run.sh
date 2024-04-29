#!/bin/bash

base_url="https://www.trulia.com/for_rent/Urbana,IL/"
delay=10
output_file="trulia_rentals_dataset.csv"
scraped_pages_file="scraped_pages.txt"
skipped_pages_file="skipped_pages.txt"

for (( start_page=1; start_page<=5; start_page++ )); do
    end_page=$start_page
    
    echo "Scraping page $start_page..."

    # Run the Python script with the current page number
    python trulia_webscrape.py \
        --base_url "$base_url" \
        --start_page "$start_page" \
        --end_page "$end_page" \
        --delay "$delay" \
        --output_file "$output_file" \
        --scraped_pages_file "$scraped_pages_file" \
        --skipped_pages_file "$skipped_pages_file"

    # Wait for 60 seconds before moving to the next page
    # Different than delay
    echo "Waiting 60 seconds..."
    sleep 60
done

echo "Completed loop through all pages. Starting over..."