import sys
import time
import math
import logging
from datetime import datetime, timezone
import httpx
from config import SIMULATOR_INTERVAL_SECONDS, API_BASE_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("simulator")

# Bounded coordinate zones for the seeded equipment across Indian sites
EQUIPMENT_PROFILES = {
    # EQX1001: Low Utilization / High Idle (Bailadila Iron Ore Complex Deposit 14)
    "EQX1001": {
        "base_lat": 18.7180, "base_lng": 81.2580,
        "radius_deg": 0.0006,
        "engine_hours": 16.0, "idle_hours": 14.2,
        "engine_step": 0.010, "idle_step": 0.009,
        "fuel": 82.0, "fuel_depletion": 0.02,
        "angle": 0.0,
    },
    # EQX1002: Missing Operator / Stationary Staging (Navi Mumbai International Airport T1)
    "EQX1002": {
        "base_lat": 18.9894, "base_lng": 73.0648,
        "radius_deg": 0.0001,
        "engine_hours": 2.0, "idle_hours": 1.8,
        "engine_step": 0.001, "idle_step": 0.001,
        "fuel": 95.0, "fuel_depletion": 0.005,
        "angle": 0.0,
    },
    # EQX1003: Active Normal (Bailadila Iron Ore Extraction)
    "EQX1003": {
        "base_lat": 18.7185, "base_lng": 81.2590,
        "radius_deg": 0.0008,
        "engine_hours": 28.5, "idle_hours": 4.2,
        "engine_step": 0.014, "idle_step": 0.001,
        "fuel": 68.0, "fuel_depletion": 0.08,
        "angle": 1.5,
    },
    # EQX1004: Generator (Stationary Power at Navi Mumbai Airport)
    "EQX1004": {
        "base_lat": 18.9900, "base_lng": 73.0655,
        "radius_deg": 0.0000,
        "engine_hours": 34.0, "idle_hours": 2.1,
        "engine_step": 0.014, "idle_step": 0.001,
        "fuel": 45.0, "fuel_depletion": 0.12,
        "angle": 0.0,
    },
    # EQX1005: High-Use Bulldozer (Active Grading at Navi Mumbai Airport)
    "EQX1005": {
        "base_lat": 18.9890, "base_lng": 73.0640,
        "radius_deg": 0.0010,
        "engine_hours": 48.0, "idle_hours": 2.4,
        "engine_step": 0.016, "idle_step": 0.001,
        "fuel": 32.0, "fuel_depletion": 0.15,
        "angle": 3.0,
    },
    # EQX1006: Overdue Scissor Lift (Kallambella Wind Energy Corridor)
    "EQX1006": {
        "base_lat": 13.6067, "base_lng": 76.9033,
        "radius_deg": 0.0004,
        "engine_hours": 22.0, "idle_hours": 3.5,
        "engine_step": 0.008, "idle_step": 0.002,
        "fuel": 74.0, "fuel_depletion": 0.04,
        "angle": 4.2,
    },
    # EQX1007: Unassigned / Yard Storage (Kallambella Staging Area)
    "EQX1007": {
        "base_lat": 13.6075, "base_lng": 76.9045,
        "radius_deg": 0.0002,
        "engine_hours": 0.0, "idle_hours": 0.0,
        "engine_step": 0.000, "idle_step": 0.000,
        "fuel": 100.0, "fuel_depletion": 0.00,
        "angle": 0.0,
    },
}


def sync_initial_state_from_backend(client: httpx.Client):
    """Optionally sync current state from backend to continue increments from live values."""
    for eq_id in list(EQUIPMENT_PROFILES.keys()):
        try:
            res = client.get(f"{API_BASE_URL}/api/v1/equipment/{eq_id}/telemetry/latest", timeout=3.0)
            if res.status_code == 200:
                data = res.json()
                profile = EQUIPMENT_PROFILES[eq_id]
                profile["engine_hours"] = data.get("engine_hours", profile["engine_hours"])
                profile["idle_hours"] = data.get("idle_hours", profile["idle_hours"])
                profile["fuel"] = data.get("fuel_pct", profile["fuel"])
                logger.info(f"Synchronized {eq_id} state from backend (engine={profile['engine_hours']}h)")
        except Exception:
            pass


def discover_new_equipment(client: httpx.Client):
    """
    Fetch the full equipment list from the API and register any unknown IDs
    with a default 'yard storage' profile (stationary, full fuel).
    This allows newly added equipment to receive simulator telemetry without
    restarting or modifying source code.
    ponytail: profiles are lost on simulator restart — fine for demo use.
    """
    try:
        res = client.get(f"{API_BASE_URL}/api/v1/equipment", timeout=5.0)
        if res.status_code != 200:
            return
        for eq in res.json():
            eq_id = eq.get("id")
            if eq_id and eq_id not in EQUIPMENT_PROFILES:
                EQUIPMENT_PROFILES[eq_id] = {
                    "base_lat": 18.7180, "base_lng": 81.2580,
                    "radius_deg": 0.0000,
                    "engine_hours": 0.0, "idle_hours": 0.0,
                    "engine_step": 0.000, "idle_step": 0.000,
                    "fuel": 100.0, "fuel_depletion": 0.00,
                    "angle": 0.0,
                }
                logger.info(f"[SIMULATOR] Registered new equipment profile: {eq_id} (yard default)")
    except Exception as e:
        logger.warning(f"[SIMULATOR] Could not discover equipment: {e}")


def step_simulation(client: httpx.Client) -> int:
    """Execute one simulation step across all assets and send telemetry via HTTP."""
    success_count = 0
    now = datetime.now(timezone.utc)

    for eq_id, profile in EQUIPMENT_PROFILES.items():
        # 1. Bounded GPS drift (circular/elliptical orbital pattern inside site bounds)
        profile["angle"] = (profile["angle"] + 0.15) % (2 * math.pi)
        d_lat = profile["radius_deg"] * math.sin(profile["angle"])
        d_lng = profile["radius_deg"] * math.cos(profile["angle"]) * 1.2
        cur_lat = round(profile["base_lat"] + d_lat, 6)
        cur_lng = round(profile["base_lng"] + d_lng, 6)

        # 2. Runtime & fuel increments
        profile["engine_hours"] = round(profile["engine_hours"] + profile["engine_step"], 3)
        profile["idle_hours"] = round(profile["idle_hours"] + profile["idle_step"], 3)
        # Ensure idle never exceeds engine
        if profile["idle_hours"] > profile["engine_hours"]:
            profile["idle_hours"] = profile["engine_hours"]

        profile["fuel"] = max(5.0, round(profile["fuel"] - profile["fuel_depletion"], 1))

        payload = {
            "equipment_id": eq_id,
            "timestamp": now.isoformat(),
            "latitude": cur_lat,
            "longitude": cur_lng,
            "engine_hours": profile["engine_hours"],
            "idle_hours": profile["idle_hours"],
            "fuel_pct": profile["fuel"],
        }

        try:
            res = client.post(f"{API_BASE_URL}/api/v1/telemetry", json=payload, timeout=4.0)
            if res.status_code == 201:
                success_count += 1
                logger.info(
                    f"[SIMULATOR] {eq_id} telemetry sent: lat={cur_lat}, lng={cur_lng}, "
                    f"engine={profile['engine_hours']}h, idle={profile['idle_hours']}h, fuel={profile['fuel']}%"
                )
            else:
                logger.warning(f"[SIMULATOR] {eq_id} server rejected: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"[SIMULATOR] Failed to send telemetry for {eq_id}: {e}")

    return success_count


def run_simulator(once: bool = False, max_iterations: int = -1):
    logger.info(f"Starting RentSense Telemetry Simulator (Target Interval: {SIMULATOR_INTERVAL_SECONDS}s, URL: {API_BASE_URL})")
    
    with httpx.Client(timeout=10.0) as client:
        sync_initial_state_from_backend(client)
        discover_new_equipment(client)
        iteration = 0

        while True:
            iteration += 1
            start_time = time.time()
            step_simulation(client)

            if once or (max_iterations > 0 and iteration >= max_iterations):
                logger.info(f"Simulator completed {iteration} iteration(s). Exiting.")
                break

            elapsed = time.time() - start_time
            sleep_time = max(0.5, SIMULATOR_INTERVAL_SECONDS - elapsed)
            time.sleep(sleep_time)


if __name__ == "__main__":
    once_flag = "--once" in sys.argv
    run_simulator(once=once_flag)
