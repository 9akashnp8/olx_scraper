import pandas as pd
from typing import List

from .utils import extract_city

class Analyzer():
    """
    class that provides various methods that performs data analysis on scraped data
    and returns the result of the analysis.

    Args:
        scraped_data (List[List[str]]): a list of list containing data from
        Scraper()'s .scrape() method
    """
    def __init__(self, scraped_data: List[List[str]]) -> None:
        self.df = self._initialize_dataframe(scraped_data)

    def _initialize_dataframe(self, scraped_data: List[List[str]]) -> pd.DataFrame:
        """
        converts the list of list into workable pandas DataFrame

        Args:
            scraped_data (List[List[str]])

        Returns:
            pd.DataFrame
        """
        df = pd.DataFrame(
            data=scraped_data,
            columns=['ad_id', 'price', 'year', 'kms', 'title', 'location', 'link']
        )
        df['price'] = pd.to_numeric(df['price'])
        df = df[df.price >= 100000]
        df['kms'] = pd.to_numeric(df['kms'])
        df['city'] = df['location'].apply(extract_city)
        return df

    def get_avg_price_by_city(self) -> dict:
        return self.df.groupby('city')['price'].mean().to_dict()
    
    def get_avg_price_by_year(self) -> dict:
        return self.df.groupby('year')['price'].mean().to_dict()
    
    def get_top_5_cities_with_ads(self) -> dict:
        return self.df['city'].value_counts().nlargest(5).to_dict()
    
