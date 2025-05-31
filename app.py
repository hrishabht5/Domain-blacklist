# app.py
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check_blacklists():
    data = request.get_json()
    domain = data.get("domain")
    if not domain:
        return jsonify({"error": "No domain provided"}), 400

    # Configure Selenium with Chromium
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://mxtoolbox.com/blacklists.aspx")
        time.sleep(3)

        input_box = driver.find_element("id", "ctl00_ContentPlaceHolder1_ucToolhandler_txtToolInput")
        input_box.clear()
        input_box.send_keys(domain)

        go_button = driver.find_element("id", "ctl00_ContentPlaceHolder1_ucToolhandler_btnAction")
        go_button.click()

        time.sleep(10)  # wait for results to load

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_ucToolhandler_pnlToolResult"})
        result_text = table.get_text(strip=True) if table else "No result table found."

        return jsonify({"domain": domain, "result": result_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
