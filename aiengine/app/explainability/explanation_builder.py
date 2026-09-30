"""
THERMOS SHAP Explanation & UI Attribution Builder
Maps SHAP feature importance values and raw values into structured human-readable explanations.
"""

import numpy as np
try:
    from training.model_features import FEATURE_COLUMNS
except ModuleNotFoundError:
    try:
        from aiengine.training.model_features import FEATURE_COLUMNS
    except ModuleNotFoundError:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
        from training.model_features import FEATURE_COLUMNS

DISPLAY_NAMES = {
    # 1. Thermal
    "frp": "Fire Radiative Power (FRP)",
    "bright_ti4": "VIIRS Brightness TI4 (High Temp)",
    "bright_ti5": "VIIRS Background Temp TI5",
    "confidence_score": "Hotspot Confidence Score",
    "scan": "Satellite Scan Pixels",
    "track": "Satellite Track Pixels",
    "day_night_numeric": "Nighttime Observation Indicator",
    "firms_type": "FIRMS Hotspot Category",

    # 2. Temporal Source Baseline
    "observation_count": "Historical Observations Count",
    "active_days": "Total Active Observation Days",
    "span_days": "Total Historical Span (Days)",
    "active_day_ratio": "Active Day Persistence Ratio",
    "mean_frp": "Source Mean FRP Baseline",
    "median_frp": "Source Median FRP Baseline",
    "max_frp": "Historical Peak FRP",
    "min_frp": "Historical Minimum FRP",
    "frp_stddev": "FRP Historical Variance",
    "frp_cv": "FRP Coefficient of Variation",
    "persistence_score": "Multi-Month Persistence Score",
    "stability_score": "Thermal Stability Score",
    "anomaly_score": "Source Peak Anomaly Score",
    "flare_signature_score": "Refinery Flare Signature Index",

    # 3. Event-vs-History Anomaly
    "event_frp_vs_source_mean": "FRP vs Source Mean Ratio",
    "event_frp_vs_source_median": "FRP vs Source Median Ratio",
    "event_frp_zscore": "Event FRP Historical Z-Score",
    "event_frp_percentile": "Event Intensity Percentile",
    "event_intensity_deviation": "Intensity Baseline Deviation",

    # 4. Spatial Infrastructure
    "distance_to_facility": "Distance to Nearest Industrial Site",
    "distance_to_powerplant": "Distance to Thermal Powerplant",
    "distance_to_refinery": "Distance to Oil/Gas Refinery",
    "distance_to_mine": "Distance to Open-Pit Mine",
    "distance_to_quarry": "Distance to Mineral Quarry",
    "distance_to_flare": "Distance to Flare Stack Infrastructure",
    "inside_facility_boundary": "Inside Industrial Boundary",
    "nearest_facility_count_500m": "Nearby Facilities (500m)",
    "nearest_facility_count_1km": "Nearby Facilities (1km)",
    "industrial_facility_density": "Industrial Facility Spatial Density",
    "industrial_context": "Industrial Proximity Score",
    "mining_context": "Mining Proximity Score",

    # 5. Spatial Spread & Clustering
    "cluster_size": "Spatial Cluster Event Count",
    "neighbor_count_1km": "Neighboring Hotspots (1km)",
    "neighbor_count_5km": "Neighboring Hotspots (5km)",
    "spatial_extent_km": "Cluster Footprint Extent (km)",
    "convex_hull_area": "Cluster Spatial Area (sq km)",
    "event_density": "Cluster Hotspot Spatial Density",
    "spread_rate_km_day": "Fire Front Spread Rate (km/day)",
    "front_direction": "Fire Front Direction Angle",
    "centroid_shift_km": "Hotspot Centroid Shift (km)",
    "cluster_growth_rate": "24h Cluster Expansion Rate",

    # 6. Land Cover & Context
    "forest_probability": "Forest Land Cover Probability",
    "cropland_probability": "Cropland Land Cover Probability",
    "grassland_probability": "Grassland Probability",
    "shrubland_probability": "Shrubland Probability",
    "builtup_probability": "Built-up Infrastructure Probability",
    "bareland_probability": "Barren/Mining Land Probability",
    "water_probability": "Water Body Proximity Probability",
    "forest_context": "Dense Forest Vegetation Context",
    "agricultural_context": "Agricultural Field Context",
    "vegetation_context": "Total Vegetation Coverage Score",
    "builtup_context": "Urban/Industrial Built-up Context",
    "bare_land_context": "Barren Land Soil Context",

    # 7. Seasonality
    "month": "Month of Year",
    "day_of_year": "Day of Year (1..365)",
    "week_of_year": "Calendar Week",
    "season": "Climatic Season Index",
    "seasonal_activity_score": "Regional Seasonal Burning Curve",
    "source_month_activity": "Historical Same-Month Activity",
    "seasonal_peak_score": "Agricultural Crop Burning Peak Index",

    # 8. Multi-Spectral & Weather / Exposure
    "ndvi_mean": "Mean Vegetation Health (NDVI)",
    "ndvi_std": "NDVI Heterogeneity",
    "ndmi_mean": "Mean Vegetation Moisture (NDMI)",
    "ndmi_std": "NDMI Moisture Variability",
    "swir_intensity": "SWIR Band Heat Intensity Ratio",
    "night_light_mean": "VIIRS Night-time Lights Intensity",
    "industrial_nightlight_score": "Industrial Nightlight Index",
    "temperature": "Surface Air Temperature",
    "relative_humidity": "Relative Atmospheric Humidity",
    "wind_speed": "Surface Wind Velocity (m/s)",
    "weather_fire_risk": "Weather Fire Risk Index",
    "population_1km": "Population Exposure (1km)",
    "distance_to_settlement": "Distance to Nearest Human Settlement"
}


def build_explanation(feature_values, shap_values, top_n=5):
    values = np.asarray(shap_values).reshape(-1)
    rows = []
    for index, shap_value in enumerate(values):
        if index < len(FEATURE_COLUMNS):
            feature = FEATURE_COLUMNS[index]
            val = float(feature_values[index]) if index < len(feature_values) else 0.0
            rows.append({
                "feature": feature,
                "display_name": DISPLAY_NAMES.get(feature, feature.replace("_", " ").title()),
                "value": round(val, 4),
                "shap_value": round(float(shap_value), 4),
                "direction": "SUPPORTS" if shap_value > 0 else "OPPOSES"
            })

    rows.sort(key=lambda item: abs(item["shap_value"]), reverse=True)
    return rows[:top_n]
