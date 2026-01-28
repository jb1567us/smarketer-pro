#!/bin/bash

# Start Tor in background
echo "Starting Tor..."
tor --SocksPort 0.0.0.0:9050 --ControlPort 9051 --CookieAuthentication 0 > /dev/null &

# Wait for Tor to bootstrap (naive check)
sleep 5

# Start Proxy Background Worker (Visible in Logs)
echo "Starting Background Proxy Worker..."
mkdir -p logs
python src/background_proxy_worker.py --verbose > logs/proxy_worker.log 2>&1 &
echo "Background Proxy Worker Started (PID $!) details in logs/proxy_worker.log"

# Start Streamlit
echo "Starting Streamlit App..."
# Wait for worker to release initial DB locks (Docker/Windows volume fix)
sleep 5
streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
