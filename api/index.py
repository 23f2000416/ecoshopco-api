from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Sample telemetry data (replace with actual bundle if needed)
telemetry_data = {
    "amer": [{"latency": 150, "uptime": 0.99}, {"latency": 160, "uptime": 1.0}, {"latency": 155, "uptime": 0.98}],
    "emea": [{"latency": 170, "uptime": 0.97}, {"latency": 165, "uptime": 0.99}, {"latency": 160, "uptime": 1.0}],
}

@app.post("/metrics")
async def compute_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    response = {}

    for region in regions:
        data = telemetry_data.get(region, [])
        if not data:
            response[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": 0}
            continue

        latencies = np.array([d["latency"] for d in data])
        uptimes = np.array([d["uptime"] for d in data])
        breaches = int((latencies > threshold).sum())

        response[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": breaches
        }

    return response