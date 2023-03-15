from bs4.element import Tag
from typing import Optional

def extract_string_from_listing(
        listing: Tag,
        html_tag: str,
        html_attribute: str,
        attribute_value: str
    ) -> Optional[str]:
    attribute_value = getattr(
        listing.find(html_tag, attrs={html_attribute: attribute_value}),
        'string',
        None
    )
    return attribute_value

def extract_ad_price(listing):
    price = getattr(
        listing.find("span", attrs={"data-aut-id":"itemPrice"}),
        'string',
        None
    )
    if price:
        return price.split()[1].replace(",", "")
    return price

def extract_kms_year(listing):
    km_year = getattr(
        listing.find("span", attrs={"data-aut-id": "itemDetails"}),
        'string',
        None
    )
    if km_year:
        km_year = km_year.split(" - ")
        model_year = km_year[0]
        kms_driven = km_year[1].split()[0].replace(",", "")
        return kms_driven, model_year
    return "", ""

def extract_city(location: str) -> str:
    burst_location = location.split(", ")
    city = burst_location[1]
    return city