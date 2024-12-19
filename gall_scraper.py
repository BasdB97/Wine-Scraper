import requests
from bs4 import BeautifulSoup
import json

def scrape_page(url):
    wine_list = []
    try:
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        results = soup.find("div", {"class": "product-grid__wrapper"})
        
        
        if not results:
            return None
            
        wine_cards = results.find_all("div", {"class": "ptile"})
        
        for wine_card in wine_cards:
            
            wine_name = wine_card.find("strong", {"itemprop": "name"})
            desc_element = wine_card.find("p", {"class": "ptile_desc"})
            
            # Initialize variables
            wine_country = None
            wine_year = None
            wine_volume = None
            
            # Only process if desc_element exists
            if desc_element:
                # Extract country
                try:
                    country_span = desc_element.find("span", {"class": "ptile_country"})
                    if country_span:
                        wine_country = country_span.text
                except AttributeError:
                    pass
                    
                # Extract year if available
                try:
                    spans = desc_element.find_all("span")
                    if len(spans) > 1:
                        wine_year = int(spans[1].text)
                except (ValueError, AttributeError, IndexError):
                    pass
                        
                # Extract volume
                try:
                    volume_element = desc_element.find("i")
                    if volume_element:
                        wine_volume = volume_element.text
                except AttributeError:
                    pass

            # Extract price
            try:
                price_element = wine_card.find("span", {"class": "price-value"})
                if price_element:
                    price_main = price_element.text.strip(".")
                    price_decimals = price_element["data-decimals"]
                    wine_price_total = float(f"{price_main}.{price_decimals}")
            except (AttributeError, KeyError, ValueError):
                wine_price_total = None
            
            print(wine_name.text, wine_price_total)
            
            wine = {
                "name": wine_name.text if wine_name else None,
                "country": wine_country,
                "year": wine_year,
                "volume": wine_volume,
                "price": wine_price_total
            }
            
            wine_list.append(wine)
        
        return wine_list
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_all_pages(base_url, max_pages=5):
    all_wines = []
    page_num = 0
    current_page = 0
    
    while current_page < max_pages:
        # Construct URL for current page
        url = base_url if page_num == 0 else f"{base_url}?start={page_num}"
        
        # Scrape current page
        page_results = scrape_page(url)
        
        # Break if no results found
        if not page_results:
            break
            
        all_wines.extend(page_results)
        page_num += 12
        current_page += 1
        print(f"Scraped page {current_page} of {max_pages}")
        
    return all_wines

# Main execution
base_url = "https://www.gall.nl/wijn/rode-wijn/"
all_wines = scrape_all_pages(base_url, max_pages=10)  # Will scrape only first 5 pages

# Save results to JSON
with open('wines.json', 'w', encoding='utf-8') as f:
    json.dump(all_wines, f, ensure_ascii=False, indent=2)
