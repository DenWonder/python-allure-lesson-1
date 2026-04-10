import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selene import Browser, Config
from utils import attach


@pytest.fixture(scope='function')
def setup_browser():
    options = Options()
    selenoid_url = os.getenv("SELENOID_URL")

    if os.getenv("CI"):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
    elif selenoid_url:
        options.capabilities.update({
            "browserName": "chrome",
            "browserVersion": "100.0",
            "selenoid:options": {
                "enableVNC": True,
                "enableVideo": True
            }
        })

    driver = webdriver.Remote(command_executor=selenoid_url, options=options) \
        if selenoid_url else webdriver.Chrome(options=options)

    browser = Browser(Config(driver))
    yield browser

    attach.add_screenshot(browser)
    attach.add_logs(browser)
    attach.add_html(browser)
    browser.quit()