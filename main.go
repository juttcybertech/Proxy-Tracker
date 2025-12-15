package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

// CheckResponse defines the structure for the JSON response.
type CheckResponse struct {
	IPAddress   string `json:"ip_address"`
	Status      string `json:"status"`
	CheckTimeMs int64  `json:"check_time_ms"`
}

// checkIPHandler handles requests to the /check endpoint.
func checkIPHandler(w http.ResponseWriter, r *http.Request) {
	// Get the IP address from the query parameters (e.g., /check?ip=8.8.8.8)
	ip := r.URL.Query().Get("ip")
	if ip == "" {
		http.Error(w, "Missing 'ip' query parameter", http.StatusBadRequest)
		return
	}

	log.Printf("GO_HANDLER: Received check request for IP: %s", ip)

	// --- Simulate a fast, complex check ---
	startTime := time.Now()
	time.Sleep(50 * time.Millisecond) // Simulate network/processing latency
	duration := time.Since(startTime).Milliseconds()
	// --- End simulation ---

	// Create the response object.
	response := CheckResponse{
		IPAddress:   ip,
		Status:      "OK_ANONYMOUS", // A fictional status for demonstration
		CheckTimeMs: duration,
	}

	// Set the content type to JSON and send the response.
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/check", checkIPHandler)
	port := 8081
	fmt.Printf("Go microservice listening on http://localhost:%d\n", port)
	if err := http.ListenAndServe(fmt.Sprintf(":%d", port), nil); err != nil {
		log.Fatalf("Failed to start Go microservice: %v", err)
	}
}