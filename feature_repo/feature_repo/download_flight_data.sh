#!/bin/bash

# Set variables
YEAR=2023
CONTAINER="feast-container"
TEMP_DIR="flight_data_temp"
BASE_URL="https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present"

# Create temporary directory
mkdir -p $TEMP_DIR
cd $TEMP_DIR

# Function to handle errors
handle_error() {
    echo "Error: $1"
    cd ..
    rm -rf $TEMP_DIR
    exit 1
}

# Function to process each month
process_month() {
    local month=$(printf "%02d" $1)
    local filename="${YEAR}_${month}.zip"
    local url="${BASE_URL}_${YEAR}_${month}.zip"
    
    echo "Downloading data for ${YEAR}-${month}..."
    
    # Download the file
    if ! curl -k -o "$filename" "$url"; then
        handle_error "Failed to download $filename"
    fi
    
    # Create a directory for extracted files
    mkdir -p "data/${YEAR}/${month}"
    
    # Unzip the file
    if ! unzip -q "$filename" -d "data/${YEAR}/${month}"; then
        handle_error "Failed to unzip $filename"
    fi
    
    # Remove the zip file to save space
    rm "$filename"
}

# Process all months
for month in {1..12}; do
    process_month $month
done

# Source OpenRC file for Swift authentication
if ! source openrc; then
    handle_error "Failed to source openrc file"
fi

# Upload to Swift object storage
echo "Uploading data to Swift container: $CONTAINER"
if ! swift --os-auth-type v3applicationcredential upload --changed --segment-size 4831838208 "$CONTAINER" data; then
    handle_error "Failed to upload to Swift container"
fi

# Cleanup
cd ..
rm -rf $TEMP_DIR

echo "Process completed successfully!"
