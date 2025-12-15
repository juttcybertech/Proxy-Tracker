# Proxy Tracker

## Overview

**Proxy Tracker** is a sophisticated, multi-language application designed to monitor your public IP address in real-time, visualize its geolocation on an interactive map, and perform advanced analysis using high-performance microservices written in Go and Rust. Built with anonymity in mind, all collected data is temporary and stored only in memory.

This project showcases a polyglot microservice architecture, where a central Python Flask application orchestrates specialized tasks performed by Go and Rust services, providing a robust and extensible system.

## Features

-   **Real-time IP Monitoring**: Continuously tracks and updates your public IP address.
-   **Geolocation Visualization**: Displays the current and historical IP locations on an interactive Leaflet map.
-   **Historical Tracking**: Maintains a history of all detected IP changes, including duration for each IP.
-   **Microservice Integration (Go)**: Utilizes a Go microservice for rapid, "advanced status" checks on new IP addresses.
-   **Microservice Integration (Rust)**: Leverages a Rust microservice for high-performance "deep analysis" and risk scoring of IP addresses.
-   **Temporary Data Storage**: All IP history and analysis data is stored in memory and is lost upon application shutdown, ensuring anonymity.
-   **Interactive Map**: Features multiple base layers (Hybrid Satellite, Dark Mode, Street Map), marker clustering, and pulsating markers for active IPs.
-   **Detailed Node View**: Click on any IP marker to view detailed geolocation and analysis data.
-   **Clean Terminal Interface**: Custom startup banner and structured logging for a professional user experience.

## Technologies Used

-   **Python**:
    -   **Flask**: Web framework for the main application and API.
    -   **Requests**: For making HTTP requests to external APIs and microservices.
    -   **Threading**: For background IP monitoring.
    -   **`ip-api.com`**: External API for geolocation data.
-   **Go (Golang)**:
    -   **`net/http`**: For building a high-performance microservice to perform "advanced status" checks.
-   **Rust**:
    -   **Actix Web**: A powerful, fast, and flexible web framework for the "deep analysis" microservice.
    -   **Serde**: For efficient JSON serialization/deserialization.
-   **Frontend**:
    -   **HTML/CSS/JavaScript**: For the web interface.
    -   **Leaflet.js**: Interactive mapping library.
    -   **Leaflet.markercluster**: For grouping nearby markers.
    -   **Server-Sent Events (SSE)**: For real-time updates from the Python backend to the browser.

## Setup and Installation

To run this application, you will need Python, Go, and Rust installed on your system. While the Python app can run independently, the Go and Rust microservices provide enhanced functionality.

### Prerequisites

-   **Python 3.x**: Download from python.org
-   **Go (Golang)**: Download from go.dev/dl/
-   **Rust**: Install via `rustup` from rustup.rs

### 1. Clone the Repository

```bash
git clone https://github.com/juttcybertech/Proxy-Tracker.git
cd proxy-tracker
```

### 2. Install Python Dependencies

```bash
pip install Flask requests
```

### 3. Build and Run the Go Microservice

Open a **new terminal** and navigate to the `proxy_checker` directory:

```bash
cd proxy_checker
go run main.go
```
You should see output similar to: `Go microservice listening on http://localhost:8081`

### 4. Build and Run the Rust Microservice

Open a **second new terminal** and navigate to the `rust_analyzer` directory:

```bash
cd rust_analyzer
cargo run
```
The first time you run this, Cargo will download and compile dependencies, which might take a moment. You should see output similar to: `INFO RUST_ANALYZER: Rust microservice listening on http://localhost:8082`

### 5. Run the Python Application

Open a **third new terminal** and navigate back to the root `proxy-tracker` directory:

```bash
python app.py
```

The terminal will display a custom banner and a startup sequence, including the URL where the application is running (e.g., `http://127.0.0.1:5555`).

## Usage

1.  **Access the Web Interface**: Open your web browser and navigate to `http://127.0.0.1:5555`.
2.  **Real-time Map**: The map will automatically update with your current public IP's location. New IPs will appear with a red pulsating marker, and previous IPs with a green one.
3.  **Node Details**: Click on any marker on the map to see a popup with basic IP information and a link to view full details on a separate page.
4.  **Terminal Output**: Observe the terminal where `app.py` is running for real-time logs, including calls to the Go and Rust microservices.

## Anonymity Note

This application is designed for temporary data storage. All IP history and analysis data is held in memory and is not persisted to disk. When the `app.py` process is terminated, all collected data is lost.

## Developed by

Jutt Cyber Tech
