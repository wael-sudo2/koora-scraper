import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from retry import retry
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime
import csv
import os
from typing import Union
BASE_URL = "https://kooora.live-kooora.com/"



def send_requests(default_url: str) -> str:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        # 'referer': 'https://kooora.live-kooora.com/',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    }

    response = requests.get(default_url, headers=headers)
    return response.text

def parse_categroy_links() -> list:
    """ Parse home page category links"""
    content = send_requests(default_url=BASE_URL)
    soup = BeautifulSoup(content, 'html5lib')
    category_links = [item.find('a').get('href') for item in  soup.select_one('ul[class^="AY-Dtab"]').find_all('li')]
    return category_links

def parse_landingpage(default_content: str) -> Union[dict, None]:
    """ Parse Matchs landing pages"""
    meta_data = list()
    soup = BeautifulSoup(default_content, 'html5lib')
    parent_element = soup.select_one('div[id^="ayala-"]')
    no_data = soup.find('p', class_="no-data__msg")
    if no_data:
        print("No matches found")
        return []

    if(parent_element):
        matches_elements = parent_element.select('div[class^="AY_Match"]')
        for element in matches_elements:
            meta_data.append(
                {
                    "title": element.find('a').get('title') if element.find('a') else None,
                    "href": element.find('a').get('href') if element.find('a') else None,
                    "team_1": element.find('div', class_="MT_Team TM1").text.strip(),
                    "team_2": element.find('div', class_="MT_Team TM2").text.strip(),
                    "match-status": " ".join(element.get('class', [])).split(' ')[-1]
                }
            )
    else:
        raise Exception('Error parsing landing page!!')
    return meta_data


def switch_to_iframe(driver, timeout=10) -> bool:
    """ Switches to an available iframe if present """
    try:
        # Some brodcasts frame contain mulitiple empty frames
        # Attempt to fetch targeted frame
        try:
            second =WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[allowfullscreen='true']")
            )
            )
        except Exception:
            second = False
            pass
        if second:
            return True
        iframe = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        return True
    except:
        return False


@retry(tries=5, delay=2)
def check_feed(driver) -> bool:
    print('Looking for video frame...')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "aplr-player-content"))
    )
    for attempt in range(3):  # try up to 3 iframes (Based on the tracked behaviour nested feed is inside 3 framees )
        if not switch_to_iframe(driver):
            break  # no more iframes available
        print(f"Switched to frame {attempt + 1}")
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "live-info"))
            )
            if element.get_attribute("textContent").strip().lower() == 'live':
                return True
        except:
            continue  # no "live-info" found, try the next iframe
    
    return False


def take_screenshot(default_url, default_title):
    brodcast, reported = False, False
    date_str = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    screenshot_path = f'{default_title}_{date_str}.png'
    screenshot_dir = "/opt/airflow/dags/src/screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)

    full_screenshot_path = os.path.join(screenshot_dir, screenshot_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    selenium_url = 'http://selenium:4444/wd/hub'
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['platform'] = "ANY"
    capabilities['version'] = ""
    selenium_url = 'http://selenium:4444/wd/hub'
    driver = webdriver.Remote(
        command_executor=selenium_url,
        options=options,
        keep_alive=True
    )

    driver.get(default_url)
    driver.set_page_load_timeout(60)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "aplr-player-content"))
        )
        try:
            if check_feed(driver):
                brodcast = True
                print("Video Brodcast Live !!!!!!!!!!")
            else:
                reported = True
                print("VVideo Brodcast Reported !!!!!!!!")
        except Exception:
            print('Failed Scanning video feed !!', e)
        driver.save_screenshot(full_screenshot_path)
        print("Screenshot saved successfully!")
        return brodcast, reported, full_screenshot_path.split('opt/airflow/')[-1]
    except Exception as e:
        print("Parent Video Element Not Found !!", e)
    finally:
        driver.quit()

    return None


def parse_sectionpage(default_content:str) -> dict:

    table_row = {
        "league": None,
        "channel": None,
        "match-date": None,
        "match-time": None,
        "commentator": None,
        "match-score":None,
        "brodcast_link": None,
        "brodcasted": None,
        "reported": None,
        "screenshot_url": None,
    }
    soup = BeautifulSoup(default_content, 'html5lib')
    table_rows = soup.find('table', class_='table table-bordered').find_all('tr') if soup.find('table', class_='table table-bordered') else None
    for row in table_rows:
        if row.find('th').text == 'البطولة': table_row['league'] = row.find('td').text
        if row.find('th').text == 'اسم القناة': table_row['channel'] = row.find('td').text
        if row.find('th').text == 'تاريخ المباراة': table_row['match-date'] = row.find('td').text
        if row.find('th').text == 'توقيت المباراة': table_row['match-time'] = row.find('td').text
        if row.find('th').text == 'المعلق': table_row['commentator'] = row.find('td').text
        if row.find('th').text == 'نتيجة المباراة': table_row['match-score'] = row.find('td').text
    if soup.find('div', class_='video-serv'): 
        brodcast_element = soup.find('div', class_='video-serv').find('a',href=True).get('href')
        if brodcast_element: 
            table_row['brodcast_link'] = brodcast_element
 
    return table_row


def save_dict_as_csv(data_dict, filename_prefix="kooora__"):
    timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    file_dir = "/opt/airflow/dags/src/output"
    os.makedirs(file_dir, exist_ok=True)
    filename = os.path.join(file_dir, f"{filename_prefix}{timestamp}.csv")
    keys = data_dict[0].keys() if data_dict else []
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data_dict)

    print(f"CSV saved as {filename}")
    return filename


def scraper() -> dict:
    urls = parse_categroy_links()
    data = list()
    for url in urls:
        print('-------------------------Scraping page:-----------------------', url)
        content = send_requests(default_url=url)
        data_dict = parse_landingpage(default_content=content)
        for item in data_dict:
            print('******************************************')
            print('scraping match: ', item.get('title'))
            response = send_requests(default_url=item.get('href'))
            item.update(parse_sectionpage(default_content=response))
            if item.get('match-status') == 'live':
                brodcasted, reported, image_url = take_screenshot(default_url=item.get('brodcast_link'),default_title=f"{item.get('team_1')}vs{item.get('team_2')}")
                if image_url: 
                    item['screenshot_url'] = image_url
                    item['brodcasted'] = brodcasted
                    item['reported'] = reported
            print('******************************************')
        data.extend(data_dict)
    return data


if __name__ == '__main__':
    data = scraper()
    save_dict_as_csv(data_dict=data)