from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import time
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "MXToolbox Blacklist API is running."

@app.route("/check", methods=["POST"])
def check_blacklists():
    try:
        data = request.get_json()
        domain = data.get("domain")
        if not domain:
            return jsonify({"error": "Missing 'domain' in request body."}), 400

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service("/usr/bin/geckodriver")  # path for Geckodriver in Render

        driver = webdriver.Firefox(service=service, options=options)

        driver.get("https://mxtoolbox.com/blacklists.aspx")
        time.sleep(3)

        input_box = driver.find_element("id", "ctl00_ContentPlaceHolder1_ucToolhandler_txtToolInput")
        input_box.clear()
        input_box.send_keys(domain)

        search_button = driver.find_element("id", "ctl00_ContentPlaceHolder1_ucToolhandler_btnAction")
        search_button.click()

        time.sleep(10)  # wait for results to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        results_table = soup.find("table", id="ctl00_ContentPlaceHolder1_gridResults")
        if not results_table:
            return jsonify({"error": "Could not find results table. Check domain or try again."}), 500

        # Optional: parse rows for cleaner output
        results = []
        for row in results_table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                blacklist = cols[0].get_text(strip=True)
                status = cols[1].get_text(strip=True)
                results.append({"blacklist": blacklist, "status": status})

        return jsonify({
            "domain": domain,
            "blacklist_results": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        try:
            driver.quit()
        except:
            pass
