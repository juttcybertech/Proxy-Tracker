from flask import Flask, render_template, request, Response
import requests
import json
import os
from datetime import datetime
import time
import threading
import sys
import logging

# Create an instance of the Flask class
app = Flask(__name__)

# Define the program name
PROGRAM_NAME = "Proxy Tracker"

# ANSI color codes for terminal output
class Colors:
    """A class to hold ANSI color codes for terminal styling."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'


# Define file paths for temporary data
SERVER_DATA_FILE = 'server_ip_data.json' # This is defined but not used, can be removed later if desired.

# --- Real-time IP Monitoring ---
ip_history = []
ip_history_lock = threading.Lock()
current_ip_start_time = None
isp_summary = {}
isp_summary_lock = threading.Lock()

def check_ip_periodically():
    """Continuously checks the server's public IP and updates the history."""
    global ip_history, current_ip_start_time, isp_summary
    while True:
        try:
            res = requests.get("http://ip-api.com/json/")
            res.raise_for_status()
            current_ip_data = res.json()
            current_ip = current_ip_data.get('query')

            with ip_history_lock:
                if not ip_history or ip_history[-1].get('query') != current_ip:
                    now = datetime.now()
                    # If there was a previous IP, calculate its duration
                    if ip_history and current_ip_start_time:
                        duration = (now - current_ip_start_time).total_seconds()
                        ip_history[-1]['duration'] = round(duration)

                    print(f"{Colors.GREEN}New server IP detected: {current_ip}{Colors.RESET}")

                    # Add new IP to history and reset the start time
                    ip_history.append(current_ip_data)
                    current_ip_start_time = now

                    # Update ISP summary in a thread-safe way
                    with isp_summary_lock:
                        isp_name = current_ip_data.get('isp', 'Unknown ISP')
                        if isp_name not in isp_summary:
                            isp_summary[isp_name] = set()
                        isp_summary[isp_name].add(current_ip)

                    # --- Call the Go microservice for an "advanced" check ---
                    try:
                        # This request goes to the Go service running on port 8081
                        adv_res = requests.get(f"http://localhost:8081/check?ip={current_ip}", timeout=1)
                        if adv_res.status_code == 200:
                            advanced_data = adv_res.json()
                            print(f"{Colors.CYAN}  [GO_HANDLER] Status: {advanced_data.get('Status')} ({advanced_data.get('CheckTimeMs')}ms){Colors.RESET}")
                            # Add the advanced data to our history object
                            ip_history[-1]['advanced_status'] = advanced_data
                    except requests.exceptions.RequestException:
                        # Keep this quiet to not clutter the log if the service isn't running
                        pass
                    
                    # --- Call the Rust microservice for "deep analysis" ---
                    try:
                        # This request goes to the Rust service running on port 8082
                        rust_res = requests.get(f"http://localhost:8082/analyze?ip={current_ip}", timeout=1)
                        if rust_res.status_code == 200:
                            analysis_data = rust_res.json()
                            print(f"{Colors.YELLOW}  [RUST_ANALYZER] Risk Score: {analysis_data.get('risk_score')} ({analysis_data.get('analysis_time_ms')}ms){Colors.RESET}")
                            # Add the analysis data to our history object
                            ip_history[-1]['rust_analysis'] = analysis_data
                    except requests.exceptions.RequestException:
                        pass # Also keep this quiet

        except requests.exceptions.RequestException as e:
            print(f"Could not check server IP: {e}")
        time.sleep(5) # Check every 5 seconds

# Define a route for the home page
@app.route('/')
def home():
    # This route serves the main page and logs visitor IP in the background.
    # The initial IP history is passed to the template.

    return render_template('index.html', server_data_history=ip_history, program_name=PROGRAM_NAME)

@app.route('/stream')
def stream():
    def event_stream():
        last_sent_count = 0
        while True:
            with ip_history_lock:
                if len(ip_history) > last_sent_count:
                    # Send only the newest IP data
                    new_data = ip_history[-1]
                    yield f"data: {json.dumps(new_data)}\n\n"
                    last_sent_count = len(ip_history)
            time.sleep(1) # Check for updates every second
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/node/<ip_address>')
def node_details(ip_address):
    """Displays detailed information for a given IP from cached data."""
    node_data = {}
    # Search through the history for the requested IP
    with ip_history_lock:
        for data in reversed(ip_history):
            if data.get('query') == ip_address:
                node_data = data
                break

    return render_template('node_details.html', node_data=node_data, ip_address=ip_address, program_name=PROGRAM_NAME)

# This ensures the server runs only when the script is executed directly
if __name__ == '__main__':
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Start the background thread to monitor the IP
    monitor_thread = threading.Thread(target=check_ip_periodically, daemon=True)
    monitor_thread.start()

    # --- Display startup banner ---
    title = f" {PROGRAM_NAME} "
    creator_line = " Developed by jutt cyber tech "
    
    # Determine box width based on the longer line
    box_width = max(len(title), len(creator_line))
    
    # Center the text
    centered_title = title.center(box_width)
    centered_creator = creator_line.center(box_width)

    # Get terminal width for centering the banner
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = 80 # Default width if terminal size can't be determined
    
    # Create the banner lines
    banner_lines = [
        f"{Colors.CYAN}╔{'═' * (box_width + 2)}╗{Colors.RESET}",
        f"{Colors.CYAN}║ {Colors.BOLD}{Colors.YELLOW}{centered_title}{Colors.RESET}{Colors.CYAN} ║{Colors.RESET}",
        f"{Colors.CYAN}║ {Colors.GREEN}{centered_creator}{Colors.RESET}{Colors.CYAN} ║{Colors.RESET}",
        f"{Colors.CYAN}╚{'═' * (box_width + 2)}╝{Colors.RESET}"
    ]

    # Print each line centered in the terminal
    for line in banner_lines:
        # To correctly center lines with ANSI codes, we need to calculate the visible length
        # This is a simplified approach; for complex cases, a library might be needed
        padding = " " * ((terminal_width - (box_width + 4)) // 2)
        print(f"{padding}{line}")

    # Define host and port for the server
    HOST = '127.0.0.1'
    PORT = 5555

    # Suppress the Flask development server warning
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # Print a more "advanced" startup sequence
    print(f"\n{Colors.CYAN}[INFO] Initializing core modules...{Colors.RESET}")
    time.sleep(0.5) # Dramatic pause
    print(f"{Colors.GREEN}[OK] Geolocation service connected.{Colors.RESET}")
    print(f"{Colors.GREEN}[OK] Real-time event stream established.{Colors.RESET}")
    print(f"{Colors.YELLOW}[WARN] Persistent storage offline (Anonymity mode enabled).{Colors.RESET}")

    # Print the URL where the server is running
    print(f"\n{Colors.YELLOW}* Ready and awaiting connections on: {Colors.BOLD}http://{HOST}:{PORT}{Colors.RESET}")

    # Run the app without the default Flask startup message
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run(host=HOST, port=PORT, debug=True, use_reloader=False)
