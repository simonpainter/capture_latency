#!/bin/bash

# Check if a URL argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <https_url>"
    exit 1
fi

URL=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PCAP_FILE="capture_${TIMESTAMP}.pcap"
OUTPUT_DIR="latency_test_${TIMESTAMP}"

# Check if tcpdump and tshark are installed
if ! command -v tcpdump &> /dev/null || ! command -v tshark &> /dev/null; then
    echo "Error: This script requires tcpdump and tshark (wireshark-cli) to be installed"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Start packet capture in background
echo "Starting packet capture..."
sudo tcpdump -i any -w "$OUTPUT_DIR/$PCAP_FILE" 'tcp port 443' &
TCPDUMP_PID=$!

# Wait for tcpdump to initialize
sleep 2

# Perform downloads
echo "Performing downloads..."
for i in $(seq 1 100); do
    echo "Download $i/100"
    wget --no-check-certificate "$URL" -O /dev/null 2>&1
    sleep 0.5
done

# Stop packet capture
echo "Stopping packet capture..."
sudo kill -SIGTERM $TCPDUMP_PID
sleep 2

# Extract timing information using tshark - focusing on TCP-level data
echo "Analyzing packet capture..."
tshark -r "$OUTPUT_DIR/$PCAP_FILE" -T fields \
    -e frame.time_epoch \
    -e tcp.stream \
    -e tcp.flags \
    -e tcp.len \
    -e ip.src \
    -e tcp.srcport \
    -Y "tcp.len > 0" \
    > "$OUTPUT_DIR/timing_data.txt"

echo "Analysis complete. Files saved in $OUTPUT_DIR/"
