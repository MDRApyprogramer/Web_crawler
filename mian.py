#Web Crawler

import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp

async def get_all_links(session, url):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a') if link.get('href')]
            return links
    except Exception as e:
        print(f"Error fetching URL: {url} -- {e}")
        return []

def find_word_on_webpage(url, word):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text()
        if word in text_content:
            return True
        else:
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return False

async def is_site_available(url: str, session: aiohttp.ClientSession) -> bool:
    try:
        async with session.head(url, timeout=5, allow_redirects=True) as response:
            if response.status < 400:
                return True
    except asyncio.TimeoutError:
        return True
    except aiohttp.ClientError:
        pass
    return False

async def bounded_is_site_available(link, session, semaphore):
    async with semaphore:
        return await is_site_available(link, session)

async def main(urls, domain):
    if type(urls) != list:
        urls = [urls]
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(get_all_links(session, url)) for url in urls]
        all_results = await asyncio.gather(*tasks)
        all_links = [link for result in all_results for link in result]

        availability_tasks = [asyncio.create_task(is_site_available(domain + link, session)) for link in all_links]
        availability_results = await asyncio.gather(*availability_tasks)
        valid_links = [link for i, link in enumerate(all_links) if availability_results[i]]

        return valid_links

if __name__ == '__main__':
    site_url = input("Enter the URL of the website: ")
    word = input("Enter the word you want to find: ")

    # Get site and loading links of site
    links = list(set([site_url + link for link in asyncio.run(main(site_url, site_url))]))
    all_links = [f'{site_url}/']
    print('process home page')
    if links:
        new_links = asyncio.run(main(links, site_url))
    else:
        print("No links found or an error occurred.")
        new_links = False

    if new_links:
        print(f"i found {len((new_links))} links : \n", new_links)
        for link in new_links:
            if link not in all_links:
                all_links.append(link)
    else:
        print("No links found or an error occurred!")

    all_links = list(set(all_links))  # Remove repetitive data and convert to link set
    print(f"i removed Repetitive  links : {len((all_links)) - len(new_links)} \n", all_links)

    # Get links of site that have key word
    site_specific_links = []
    trueLink = []

    for i in all_links:
        if 'http' == i[:4] and i[:len(site_url)] != site_url: pass
        else:
            if "http" == i[:4]: site_specific_links.append(i)
            else: site_specific_links.append(site_url + i)

    print(f'i removed invalid links : {len(site_specific_links) - len(all_links)} \n', site_specific_links)
    print('searcing in the links for key word')

    for link in site_specific_links:
        print(site_specific_links.index(link) , " _ ", link, ' :::: searched')
        if find_word_on_webpage(link, word):
            trueLink.append(link)

    print(f'i searched: {len(all_links)} page')
    print(f'i found: {len(trueLink)} links')
    for i in trueLink:
        print(i)