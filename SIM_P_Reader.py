import re
import json
from statistics import mean
from pathlib import Path
from enum import Enum

# --- Load airport configuration ---
config_path = "baseline_airport.json"
with open(config_path, "r") as f:
    airport_cfg = json.load(f)

GATES             = set(airport_cfg["gates"])
ARRIVAL_RUNWAYS   = set(airport_cfg["arrival_runways"])
DEPARTURE_RUNWAYS = set(airport_cfg["dept_runways"])

# --- Define Status Enum ---
class Status(Enum):
    Running = 0
    Success = 1
    Failed_Aircraft_Taxi_Time = 2
    Failed_Collision = 3
    Failed_No_Landing_Space = 4

def parse_single_run(lines):
    arrivals = {}
    arrival_pickups = {}
    arrival_startloads = {}
    dep_loading_compl = {}
    dep_pickups = {}
    departures = {}
    times = []
    min_tugs = None
    sim_status = Status.Running  # Default status

    event_re   = re.compile(r"-\s*(\d+):\s*(.*)", re.IGNORECASE)
    re_tugs    = re.compile(r"Number of tugs:\s*(\d+)", re.IGNORECASE)
    re_arrival = re.compile(r"Aircraft (\d+) arrived at (\d+)", re.IGNORECASE)
    re_pickup  = re.compile(r"Aircraft (\d+) picked up at (\d+) by tug \d+ going to (\d+)", re.IGNORECASE)
    re_start   = re.compile(r"Aircraft (\d+) started loading at (\d+)", re.IGNORECASE)
    re_comp    = re.compile(r"Aircraft (\d+) completed loading at (\d+)", re.IGNORECASE)
    re_depart  = re.compile(r"Aircraft (\d+) departing from (\d+)", re.IGNORECASE)
    re_status  = re.compile(r"reason:\s*Status\.(\w+)", re.IGNORECASE)

    for line in lines:
        # Check if simulation end reason is mentioned
        if (m := re_status.search(line)):
            status_str = m.group(1)
            try:
                sim_status = Status[status_str]
            except KeyError:
                sim_status = Status.Running  # fallback if unknown status

        m = re_tugs.search(line)
        if m:
            min_tugs = int(m.group(1))

        m = event_re.search(line)
        if not m:
            continue
        t, msg = int(m.group(1)), m.group(2)
        times.append(t)

        if (m2 := re_arrival.search(msg)):
            ac, _ = map(int, m2.groups())
            arrivals.setdefault(ac, t)
        elif (m2 := re_pickup.search(msg)):
            ac, loc, dest = map(int, m2.groups())
            if dest in GATES:
                arrival_pickups.setdefault(ac, t)
            if dest in DEPARTURE_RUNWAYS:
                dep_pickups.setdefault(ac, t)
        elif (m2 := re_start.search(msg)):
            ac, loc = map(int, m2.groups())
            if loc in GATES:
                arrival_startloads.setdefault(ac, t)
        elif (m2 := re_comp.search(msg)):
            ac, loc = map(int, m2.groups())
            if loc in GATES:
                dep_loading_compl.setdefault(ac, t)
        elif (m2 := re_depart.search(msg)):
            ac, rw = map(int, m2.groups())
            if rw in DEPARTURE_RUNWAYS:
                departures.setdefault(ac, t)

    waits_arr = [arrival_pickups[ac] - arrivals[ac] for ac in arrivals if ac in arrival_pickups]
    waits_dep = [dep_pickups[ac] - dep_loading_compl[ac] for ac in dep_loading_compl if ac in dep_pickups]
    taxis_arr = [arrival_startloads[ac] - arrival_pickups[ac] for ac in arrival_startloads if ac in arrival_pickups]
    taxis_dep = [departures[ac] - dep_pickups[ac] for ac in dep_pickups if ac in departures]
    busy_time = sum(taxis_arr) + sum(taxis_dep)
    sim_duration = max(times) - min(times) if times else 0
    util = busy_time / (min_tugs * sim_duration) if min_tugs and sim_duration > 0 else 0

    return {
        "min_tugs":     min_tugs,
        "avg_wait_arr": mean(waits_arr) if waits_arr else float("nan"),
        "avg_wait_dep": mean(waits_dep) if waits_dep else float("nan"),
        "avg_taxi_arr": mean(taxis_arr) if taxis_arr else float("nan"),
        "avg_taxi_dep": mean(taxis_dep) if taxis_dep else float("nan"),
        "util_pct":     util * 100,
        "status":       sim_status
    }

def parse_multiple_runs(path):
    results = []
    with open(path) as f:
        current_run = []
        for line in f:
            if "=== STARTING SIM RUN" in line:
                if current_run:
                    stats = parse_single_run(current_run)
                    results.append(stats)
                    current_run = []
            current_run.append(line)
        if current_run:
            stats = parse_single_run(current_run)
            results.append(stats)

    """
    # Print results
    for i, r in enumerate(results):
        print(f"\n--- Simulation Run {i} ---")
        print(f"1) Min tugs required        : {r['min_tugs']}")
        print(f"2) Avg waiting arrival      : {r['avg_wait_arr']:.2f} s")
        print(f"3) Avg waiting departure    : {r['avg_wait_dep']:.2f} s")
        print(f"4) Avg taxi time arrival    : {r['avg_taxi_arr']:.2f} s")
        print(f"5) Avg taxi time departure  : {r['avg_taxi_dep']:.2f} s")
        print(f"6) Tug utilization rate     : {r['util_pct']:.1f}%")
    """

    return results


