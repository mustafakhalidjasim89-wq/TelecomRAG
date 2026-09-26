WEIGHTS = {
    "Generator fuel leakage observed": 50,
    "Generator oil leakage observed": 45,
    "Battery swelling observed": 50,
    "Grounding cable disconnected": 50,
    "Fire extinguisher missing": 40,
    "Tower obstruction light not working": 40,
    "Dry grass near generator": 25,
    "Dry grass near cabinet": 25,
    "Battery cabinet not locked": 20,
    "Battery terminal corrosion observed": 20,
    "Disorganized feeder cables on tower": 20,
    "Missing tower bolts": 35,
    "Rust observed on tower members": 30,
    "Tray cover is not closed properly": 10,
    "PVC tray inside cabinet without cover": 10,
    "Gas piping without cable trays": 25,
    "Cables routed outside tray": 15,
    "Disorganized cables in cabinet": 15,
    "Commercial power cables disorganized": 20,
    "Cabinet door damaged": 20,
    "Water leakage inside cabinet": 45,
    "Shelter AC not operational": 35,
    "Required image not provided": 15,
    "Tower equipment image unclear": 10,
    "Technician did not capture close-up image": 10,
    "No issue observed": 0
}

def calculate_audit_score(findings):
    total_penalty = sum(WEIGHTS.get(item, 5) for item in findings)
    
    # Calculate health index score (100 is perfect)
    health_score = max(0, 100 - total_penalty)
    
    if total_penalty >= 70:
        priority = "CRITICAL"
    elif total_penalty >= 30:
        priority = "HIGH"
    elif total_penalty > 0:
        priority = "MEDIUM"
    else:
        priority = "LOW / COMPLIANT"
        
    return {
        "penalty_points": total_penalty,
        "health_score": health_score,
        "priority": priority
    }
