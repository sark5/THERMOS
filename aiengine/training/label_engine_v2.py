"""
THERMOS Weak-Label Engine V2
Generates candidate labels and confidence scores based on multi-domain feature signatures:
- INDUSTRIAL_FLARE
- INDUSTRIAL_FIRE
- MINING
- AGRICULTURAL
- WILDFIRE
- UNCLASSIFIED
"""

from typing import Dict


def classify_row(row: Dict) -> Dict:
    # 1. Extract feature values with safe fallbacks
    persistence = float(row.get("persistence_score", 0) or 0)
    stability = float(row.get("stability_score", 0) or 0)
    industrial = float(row.get("industrial_context", 0) or 0)
    mining = float(row.get("mining_context", 0) or 0)

    dist_facility = float(row.get("distance_to_facility", 999) or 999)
    dist_refinery = float(row.get("distance_to_refinery", 999) or 999)
    dist_mine = float(row.get("distance_to_mine", 999) or 999)
    dist_flare = float(row.get("distance_to_flare", 999) or 999)

    frp_zscore = float(row.get("event_frp_zscore", 0) or 0)
    frp_vs_median = float(row.get("event_frp_vs_source_median", 1.0) or 1.0)
    intensity_dev = float(row.get("event_intensity_deviation", 0) or 0)

    forest_prob = float(row.get("forest_probability", 0) or 0)
    cropland_prob = float(row.get("cropland_probability", 0) or 0)
    bareland_prob = float(row.get("bareland_probability", 0) or 0)

    spread_rate = float(row.get("spread_rate_km_day", 0) or 0)
    seasonal_peak = float(row.get("seasonal_peak_score", 0) or 0)
    weather_risk = float(row.get("weather_fire_risk", 0) or 0)

    # Proximity scores (inverse distance bounded 0..1)
    refinery_prox = 1.0 if dist_refinery <= 4.0 else max(0.0, 1.0 - (dist_refinery - 4.0) / 10.0)
    flare_prox = 1.0 if dist_flare <= 3.0 else max(0.0, 1.0 - (dist_flare - 3.0) / 6.0)
    mine_prox = 1.0 if dist_mine <= 6.0 else max(0.0, 1.0 - (dist_mine - 6.0) / 12.0)
    facility_prox = 1.0 if dist_facility <= 4.0 else max(0.0, 1.0 - (dist_facility - 4.0) / 10.0)

    # 2. Signature Evidence Scores
    flare_score = (
        persistence * 0.30
        + stability * 0.25
        + max(refinery_prox, flare_prox, industrial * 0.8) * 0.35
        + max(0.0, 1.0 - frp_zscore / 4.0) * 0.10
    )

    industrial_fire_score = (
        facility_prox * 0.40
        + min(1.0, max(0.0, frp_zscore / 2.0)) * 0.30
        + min(1.0, max(0.0, (frp_vs_median - 1.0) / 2.0)) * 0.20
        + min(1.0, max(0.0, 1.0 - persistence)) * 0.10
    )

    mining_score = (
        mine_prox * 0.45
        + bareland_prob * 0.20
        + mining * 0.20
        + persistence * 0.15
    )

    agricultural_score = (
        cropland_prob * 0.40
        + seasonal_peak * 0.25
        + (1.0 - facility_prox) * 0.15
        + (1.0 - persistence) * 0.20
    )

    wildfire_score = (
        forest_prob * 0.40
        + min(1.0, spread_rate / 1.0) * 0.25
        + weather_risk * 0.20
        + (1.0 - facility_prox) * 0.15
    )

    candidates = {
        "INDUSTRIAL_FLARE": flare_score,
        "INDUSTRIAL_FIRE": industrial_fire_score,
        "MINING": mining_score,
        "AGRICULTURAL": agricultural_score,
        "WILDFIRE": wildfire_score,
    }

    ordered = sorted(candidates.items(), key=lambda item: item[1], reverse=True)
    best_label, best_score = ordered[0]
    second_score = ordered[1][1]
    margin = best_score - second_score

    # Threshold for UNCLASSIFIED candidate
    if best_score < 0.55 or margin < 0.08:
        return {
            "thermos_label": "UNCLASSIFIED",
            "label_score": round(best_score, 4),
            "label_margin": round(margin, 4),
            "label_quality": "UNRESOLVED",
        }

    quality = "STRONG" if best_score >= 0.75 else ("MODERATE" if best_score >= 0.62 else "WEAK")

    return {
        "thermos_label": best_label,
        "label_score": round(best_score, 4),
        "label_margin": round(margin, 4),
        "label_quality": quality,
    }