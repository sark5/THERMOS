import numpy as np
def calculate_normalized_differnence(
        band_a,band_b
):
    denominator=band_a+band_b
    result=np.divide(
        band_a-band_b,
        denominator,
        out=np.zeros_like(
        denominator,dtype=float
    ),
    where=denominator!=0
    )
    return result
def calculate_optical_features(
        red,nir,swir
):
    ndvi=calculate_normalized_differnence(nir,swir)
    ndmi=calculate_normalized_differnence(nir,swir)
    return {
        "ndvi_mean":float(
            np.nanmean(ndvi)
        ),
        "ndmi_std":float(
            np.nanstd(ndvi)
        ),
        "ndvi_mean":float(
        np.nanmean(ndmi)
        ),
        "ndmi_std":float(
            np.nanstd(ndmi)
        )
    }

