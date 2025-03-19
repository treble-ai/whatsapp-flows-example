import phonenumbers

from app.utils.features import COUNTRY_FEATURES, FEATURES


def get_country_features(country: str) -> list[dict[str, str | bool]]:
    feature_ids = COUNTRY_FEATURES.get(country, COUNTRY_FEATURES["DEFAULT"])

    return [
        {
            "id": feature_id,
            "title": FEATURES[feature_id],
            "enabled": feature_id in feature_ids,
        }
        for feature_id in FEATURES
    ]


def get_country_by_code(country_code: str) -> str:
    country_codes = phonenumbers.region_codes_for_country_code(int(country_code))
    return country_codes[0]
