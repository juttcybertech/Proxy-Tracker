use actix_web::{get, web, App, HttpServer, Responder, HttpResponse};
use serde::{Deserialize, Serialize};
use std::time::Instant;

// Define the structure for the incoming query parameters (e.g., /analyze?ip=x.x.x.x)
#[derive(Deserialize)]
struct AnalyzeRequest {
    ip: String,
}

// Define the structure for the JSON response we'll send back.
#[derive(Serialize)]
struct AnalyzeResponse {
    ip_address: String,
    risk_score: f64,
    analysis_time_ms: u128,
}

// This function will handle GET requests to the /analyze endpoint.
#[get("/analyze")]
async fn analyze_ip(info: web::Query<AnalyzeRequest>) -> impl Responder {
    log::info!("RUST_ANALYZER: Received analysis request for IP: {}", info.ip);

    let start_time = Instant::now();

    // --- Simulate a CPU-intensive analysis ---
    // This is where you would put a complex, performance-critical algorithm.
    // We'll just simulate it by calculating a dummy risk score.
    let risk_score = (info.ip.len() % 10) as f64 * 7.5; // Fictional calculation
    let duration = start_time.elapsed().as_millis();
    // --- End simulation ---

    let response = AnalyzeResponse {
        ip_address: info.ip.clone(),
        risk_score,
        analysis_time_ms: duration,
    };

    // Return the response as JSON
    HttpResponse::Ok().json(response)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    std::env::set_var("RUST_LOG", "info");
    env_logger::init();

    let port = 8082;
    log::info!("Rust microservice listening on http://localhost:{}", port);

    HttpServer::new(|| App::new().service(analyze_ip))
        .bind(("127.0.0.1", port))?
        .run()
        .await
}