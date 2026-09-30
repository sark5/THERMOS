from datetime import datetime
def calculate_scene_score(
        cloud_cover,
        time_difference_hours
):
    cloud_score=max(
        0.0,1.0-(cloud_cover/100)
    )
    temporal_score=max(
        0.0,1.0-(min(time_difference_hours,72)
                 / 72.0
                 )
    )
    score=(cloud_score* 0.6+ temporal_score*0.4)
    return round(min(score,1.0),4)
def parse_scene(product):
    properties=product.get(
        "properties",{}
    )
    content_date=properties.get(
        "contentDate",{}
    )
    start=content_date.get("start")
    cloud_cover=properties.get("cloudCover",0)
    return {
        "id":product.get("id"),
        "name":product.get("name"),
        "acquired_at":start,
        "cloud_cover":cloud_cover
    }