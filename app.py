from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check_blacklists():
    data = request.get_json()
    domain = data.get("domain")

    if not domain:
        return jsonify({"error": "Missing domain field"}), 400

    # Configure Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://mxtoolbox.com/blacklists.aspx")

        search_box = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ucToolhandler_txtToolInput")
        search_box.clear()
        search_box.send_keys(domain)
        search_box.send_keys(Keys.ENTER)

        # Wait for results to load
        time.sleep(10)  # adjust if needed

        rows = driver.find_elements(By.CSS_SELECTOR, ".ToolResultsContainer table tr")
        results = []

        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) >= 2:
                blacklist = columns[0].text.strip()
                status = columns[1].text.strip()
                if blacklist:
                    results.append({"blacklist": blacklist, "status": status})

        return jsonify({"domain": domain, "blacklist_status": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
