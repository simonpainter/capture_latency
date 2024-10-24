#!/usr/bin/python3

import pandas as pd
import numpy as np

def analyze_ttfb(filename):
    # Read the timing data
    df = pd.read_csv(filename, sep='\s+', header=None,
                     names=['timestamp', 'stream', 'tcp_flags', 'tcp_len', 'ip_addr', 'port'])
    
    # Group by stream and calculate TTFB
    stream_stats = []
    
    for stream_id, stream_data in df.groupby('stream'):
        stream_data = stream_data.sort_values('timestamp')
        
        # Identify client and server IPs
        client_port = stream_data.iloc[0]['port']
        client_packets = stream_data[stream_data['port'] == client_port]
        server_packets = stream_data[stream_data['port'] == 443]
        
        if client_packets.empty or server_packets.empty:
            continue
            
        # Get server IP (destination) for this stream
        server_ip = server_packets.iloc[0]['ip_addr']
        
        # Find first request and response
        request_time = client_packets.iloc[0]['timestamp']
        response_time = server_packets.iloc[0]['timestamp']
        
        ttfb = response_time - request_time
        
        stream_stats.append({
            'stream': stream_id,
            'server_ip': server_ip,
            'request_time': request_time,
            'response_time': response_time,
            'ttfb': ttfb,
            'request_size': client_packets.iloc[0]['tcp_len'],
            'response_size': server_packets.iloc[0]['tcp_len']
        })
    
    stats_df = pd.DataFrame(stream_stats)
    
    # Group statistics by server IP
    for server_ip, ip_data in stats_df.groupby('server_ip'):
        print(f"\n=== Statistics for {server_ip} ===")
        print(f"Total streams: {len(ip_data)}")
        print(f"\nTTFB Statistics (seconds):")
        print(f"Average TTFB: {ip_data['ttfb'].mean():.3f}")
        print(f"Minimum TTFB: {ip_data['ttfb'].min():.3f}")
        print(f"Maximum TTFB: {ip_data['ttfb'].max():.3f}")
        print(f"Median TTFB: {ip_data['ttfb'].median():.3f}")
        print(f"95th percentile TTFB: {ip_data['ttfb'].quantile(0.95):.3f}")
        print(f"Standard Deviation: {ip_data['ttfb'].std():.3f}")
        
        print("\nFirst few TTFB measurements:")
        for _, row in ip_data.head(3).iterrows():
            print(f"Stream {row['stream']}: {row['ttfb']:.3f} seconds")
            print(f"  Request size: {row['request_size']} bytes")
            print(f"  Response size: {row['response_size']} bytes")
    
    # Overall summary
    print("\n=== Overall Summary ===")
    print(f"Total number of servers: {len(stats_df['server_ip'].unique())}")
    print(f"Total streams analyzed: {len(stats_df)}")
    
    # Create summary table
    summary_table = stats_df.groupby('server_ip').agg({
        'ttfb': ['count', 'mean', 'median', 'std', 'min', 'max']
    }).round(3)
    
    print("\nSummary Table (all times in seconds):")
    print(summary_table)
    
    return stats_df

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: ./analyze_ttfb.py timing_data.txt")
        sys.exit(1)
    
    analyze_ttfb(sys.argv[1])
