# Kooora Live Scraper

This project scrapes live match data from [Kooora](https://kooora.live-kooora.com/) and captures broadcast information, including screenshots when a match is live.

## Features
- Parses category links from the home page.
- Extracts match details from landing pages.
- Checks if a match is live using Selenium.
- Captures screenshots of live match broadcasts.
- Saves match data in CSV format.
- Supports automated execution with Airflow using Docker.

## Installation

### Local Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows use: myenv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the scraper:
   ```bash
   python main.py
   ```

### Docker & Airflow Setup
1. Build and start the Docker containers:
   ```bash
   docker build . --tag extending_airflow:latest
   docker-compose up --build -d
   ```

2. Access Airflow Web UI:
   - Navigate to `http://localhost:8080` in your browser.
   - Use the default credentials (username: `airflow`, password: `airflow`).


## Functions Breakdown
### 1. `send_requests(default_url: str) -> str`
Sends an HTTP request and retrieves the page content.

### 2. `parse_categroy_links() -> list`
Extracts category links from the homepage.

### 3. `parse_landingpage(default_content: str) -> Union[dict, None]`
Extracts match information from landing pages.

### 4. `switch_to_iframe(driver, timeout=10) -> bool`
Handles iframe switching to locate live broadcasts.

### 5. `check_feed(driver) -> bool`
Verifies if a match is live by checking for a "live" status.

### 6. `take_screenshot(default_url, default_title)`
Captures a screenshot of the broadcast stream.

### 7. `parse_sectionpage(default_content: str) -> dict`
Extracts detailed match information such as league, channel, and commentators.

### 8. `save_dict_as_csv(data_dict, filename_prefix="kooora__")`
Saves the extracted match data as a CSV file.

### 9. `scraper() -> dict`
Main function that runs the scraper, processes match data, and saves it.

## Scheduled Execution
The script can be scheduled to run automatically using Apache Airflow or a cron job. For example, to run it every hour using cron:

```bash
0 * * * * /usr/bin/python3 /path/to/scraper.py
```

## Notes
- The script uses **Selenium Grid** (`http://selenium:4444/wd/hub`) for remote WebDriver execution.
- If using a local ChromeDriver, update the `webdriver.Chrome()` initialization accordingly.
- The scraper includes retry mechanisms for handling network or element loading failures.


