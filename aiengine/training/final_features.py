"""
THERMOS Final Canonical Feature Space & Label Enums
"""

FEATURES = [
    # 1. Thermal
    "frp", "bright_ti4", "bright_ti5", "confidence_score", "scan", "track", "day_night_numeric", "firms_type",
    # 2. Temporal Source Baseline
    "observation_count", "active_days", "span_days", "active_day_ratio",
    "mean_frp", "median_frp", "max_frp", "min_frp", "frp_stddev", "frp_cv",
    "persistence_score", "stability_score", "anomaly_score", "flare_signature_score",
    # 3. Event-vs-History Anomaly
    "event_frp_vs_source_mean", "event_frp_vs_source_median", "event_frp_zscore",
    "event_frp_percentile", "event_frp_ratio_previous", "event_frp_change", "event_intensity_deviation",
    # 4. Spatial Infrastructure
    "distance_to_facility", "distance_to_powerplant", "distance_to_refinery", "distance_to_mine",
    "distance_to_quarry", "distance_to_flare", "inside_facility_boundary",
    "nearest_facility_count_500m", "nearest_facility_count_1km", "industrial_facility_density",
    "industrial_context", "mining_context",
    # 5. Spatial Spread & Clustering
    "cluster_size", "neighbor_count_1km", "neighbor_count_5km", "spatial_extent_km",
    "convex_hull_area", "event_density", "spread_rate_km_day", "front_direction",
    "centroid_shift_km", "cluster_growth_rate",
    # 6. Land Cover & Context
    "forest_probability", "cropland_probability", "grassland_probability", "shrubland_probability",
    "builtup_probability", "bareland_probability", "water_probability",
    "forest_context", "agricultural_context", "vegetation_context", "builtup_context", "bare_land_context",
    # 7. Seasonality
    "month", "day_of_year", "week_of_year", "season", "seasonal_activity_score",
    "source_month_activity", "seasonal_peak_score",
    # 8. Multi-Spectral & Weather / Exposure
    "ndvi_mean", "ndvi_std", "ndmi_mean", "ndmi_std", "swir_intensity",
    "night_light_mean", "industrial_nightlight_score",
    "temperature", "relative_humidity", "wind_speed", "weather_fire_risk",
    "population_1km", "distance_to_settlement"
]

TARGET = "gold_label"

CLASSES = [
    "INDUSTRIAL_FLARE",
    "INDUSTRIAL_FIRE",
    "MINING",
    "AGRICULTURAL",
    "WILDFIRE",
    "UNCLASSIFIED",
]