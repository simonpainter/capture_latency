# HTTPS Inspection Performance Testing Scripts

## Background and Rationale

When measuring network security appliance performance, particularly for HTTPS inspection and filtering, traditional network testing tools fall short. While `ping` is useful for basic network connectivity testing, it only measures ICMP echo request/reply times, which doesn't reflect the complexity of HTTPS traffic inspection. Similarly, TCP ping tools can measure TCP handshake times but don't account for the additional overhead of TLS negotiation and application-layer inspection.

For firewalls performing FQDN (Fully Qualified Domain Name) filtering on HTTPS traffic, the crucial metric is the time taken from initial request to receiving the first byte of application data. This Time To First Byte (TTFB) measurement includes:
1. TCP connection establishment
2. TLS handshake
3. SNI (Server Name Indication) inspection by the firewall
4. FQDN filtering policy evaluation
5. Initial HTTP request transmission
6. First response byte receipt

## Project Purpose

This toolkit provides a methodology for measuring and comparing the performance impact of different firewall solutions performing HTTPS inspection and FQDN filtering. The scripts capture and analyze network traffic to measure TTFB across multiple connections, providing statistical analysis of latency patterns.

## Components

### Capture Script (`capture_latency.sh`)
- Initiates packet capture using tcpdump
- Performs configurable number of HTTPS requests to specified endpoints
- Captures full packet data for detailed timing analysis
- Extracts relevant timing information using tshark

### Analysis Script (`analyse_ttfb_by_ip.py`)
- Processes packet capture data to calculate TTFB metrics
- Analyzes results separately by destination IP address
- Provides statistical analysis including:
  - Mean and median latency
  - Standard deviation
  - Maximum values
  - Per-endpoint breakdowns

#### Why Analyze by IP?

The script analyzes performance metrics grouped by destination IP address because:
1. Modern web services often use multiple endpoints (e.g., CDN edge nodes)
2. DNS round-robin may distribute requests across different servers
3. Cloud services might route to different regional endpoints
4. Performance characteristics may vary by endpoint

This approach ensures that:
- Performance variations between different backend servers are visible
- CDN edge node performance can be compared
- Any routing or regional differences are captured
- Anomalies in specific endpoints can be identified

## Usage

1. Capture traffic:
```bash
./capture_latency.sh <https_url> <request_count>
```

2. Analyze results:
```bash
python3 analyse_ttfb_by_ip.py <timing_data.txt>
```

## Methodology Notes

The scripts use the following approach to ensure accurate measurements:

1. **Full Packet Capture**: Rather than just timing HTTP requests, we capture all packets to analyze the exact timing of TCP and TLS handshakes.

2. **Stream Analysis**: TCP streams are tracked to accurately associate request and response packets.

3. **First Data Packet**: We specifically identify the first data-carrying packet after the handshake to measure true application-layer latency.

4. **Statistical Aggregation**: Multiple requests provide robust statistical data to account for network variations.

5. **IP-based Grouping**: Results are grouped by destination IP to account for:
   - CDN edge nodes
   - DNS round-robin
   - Regional routing differences
   - Backend server variations

## Requirements

- Linux environment with:
  - tcpdump
  - tshark (Wireshark command-line tools)
  - Python 3 with pandas
- Appropriate permissions for packet capture (sudo/root)
- Network environment configured to route test traffic through the firewall under test

## Implementation Details

The timing measurement focuses on identifying the first application data packet after the TLS handshake is complete. This approach was chosen because:

1. It reflects the actual impact on application performance
2. It captures the full overhead of security processing
3. It provides consistent measurements across different firewall implementations
4. It matches real-world application behavior patterns

By analyzing results by IP address, we can:
1. Identify performance variations between different backend servers
2. Account for CDN edge node distribution
3. Detect any regional or routing-based performance differences
4. Provide more accurate comparisons when testing against distributed services
