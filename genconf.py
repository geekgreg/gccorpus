import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

# Parameters
base_uri = "https://www.churchofjesuschrist.org"
output_path = "./output"
year_list = list(range(2000, 2023))
month_list = ["10", "04"]

# Ensure the output directory exists
os.makedirs(output_path, exist_ok=True)

# Loop over each year and month
for year in year_list:
    for month in month_list:
        page_url = f"{base_uri}/study/general-conference/{year}/{month}"
        page = requests.get(page_url).text
        soup = BeautifulSoup(page, 'html.parser')

        # Find the main body div
        body_div = soup.find('div', class_='body')

        # If the body div is found, find all links to conference talks on the page
        if body_div:
            links = [link.get('href') for link in body_div.find_all('a') 
                     if link.get('href') and 
                     f'/study/general-conference/{year}/{month}' in link.get('href') and
                     'session' not in link.get('href')]

            if links:
                print(f"Links present for {year} {month}: {len(links)}")

                # Loop over each link and download the talk details
                for link in links:
                    talk_url = f"{base_uri}{link}"
                    talk_page = requests.get(talk_url).text
                    talk_soup = BeautifulSoup(talk_page, 'html.parser')

                    try:
                        # Parse the data into the desired format
                        kicker_element = talk_soup.find('p', class_='kicker')
                        title_element = talk_soup.find('h1')
                        speaker_element = talk_soup.find('p', class_='author-name')
                        role_element = talk_soup.find('p', class_='author-role')
                        body_block_element = talk_soup.find('div', class_='body-block')

                        talk = {
                            'title': title_element.text if title_element else None,
                            'speaker': speaker_element.text.replace("By ", "") if speaker_element else None,
                            'speaker-role': role_element.text if role_element else None,
                            'kicker': kicker_element.text if kicker_element else None,
                            'body': [p.text for p in body_block_element.find_all('p')] if body_block_element else None,
                            'link': talk_url,
                            'sorting': link.split("/")[-1]
                        }

                        # Save the talk details to a JSON file
                        folder_path = os.path.join(output_path, f"{year}-{month}")
                        os.makedirs(folder_path, exist_ok=True)

                        # Parse url to remove query parameters and limit filename length
                        parsed_url = urlparse(talk['sorting'])
                        clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, None, None, None))
                        clean_filename = clean_url.replace('/', '_')
                        clean_filename = clean_filename[:200]  # Limit filename length

                        file_path = os.path.join(folder_path, f"{clean_filename}.json")

                        with open(file_path, 'w') as f:
                            json.dump(talk, f, indent=4)
                    except Exception as e:
                        print(f"Error processing link {talk_url}: {e}")
