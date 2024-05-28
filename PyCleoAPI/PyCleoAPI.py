from functools import partial
from flask import Flask, jsonify, request, abort
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from chromedriver_py import binary_path
from flask_cors import CORS, cross_origin

import time

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def init_driver():
    chrome_options = Options()
    
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    chrome_service = ChromeService(executable_path=binary_path)  # Set the path to your ChromeDriver
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.set_window_size(1080,800)
    return driver

def getSummary(summaryType, url):
    if summaryType == 'weekly':
        driver = init_driver()
        driver.get(url)

        try:
            time.sleep(5)
        
            driver.find_element(By.XPATH, '//button[@data-test="1w"]').click()
        
            time.sleep(5)

            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(5)
        
            spans = soup.find_all("span", {"class": "mr-3"})

            lines = [span.get_text() for span in spans]
        
            print(lines)
        
            result = lines[1]

        finally:
            driver.quit()
            
    elif summaryType == 'monthly':
        driver = init_driver()
        driver.get(url)

        try:
            time.sleep(5)
        
            driver.find_element(By.XPATH, '//button[@data-test="1mo"]').click()
        
            time.sleep(5)

            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(5)
        
            spans = soup.find_all("span", {"class": "mr-3"})

            lines = [span.get_text() for span in spans]
        
            print(lines)
        
            result = lines[1]

        finally:
            driver.quit()

    return result
    

def scrape_weekly_analysis(url):
    
    results = {}
    
    results['weekly'] = getSummary('weekly', url)
    results['monthly'] = getSummary('monthly', url)

    return results

@app.route('/scrape/<instrument>', methods=['GET'])
@cross_origin()
def scrape(instrument):
    base_url = '' #enter base url here
    full_url = base_url + str(instrument)
    print('Full URL: ' + full_url)
    url = request.args.get('url', full_url)
    
    results = scrape_weekly_analysis(url)
    if not results:
        abort(500, description="Failed to scrape the analysis")

    return jsonify(results)

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)