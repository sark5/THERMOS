def calculate_satellite_confirmation(
        ndvi_mean,ndmi_mean,cloud_score,temporal_score
):
    optical_quality=(cloud_score*0.4+ temporal_score*0.6)
    environemntal_signal=(abs(ndvi_mean)*0.5+abs(ndmi_mean)*0.5)
    confidence=(optical_quality*0.7+min(environemntal_signal,1.0))
    return round(min(confidence,1.0),4)
    

