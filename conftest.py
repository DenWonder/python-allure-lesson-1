import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selene.support.shared import browser
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
            "browserVersion": "128.0",
            "selenoid:options": {
                "enableVNC": True,
                "enableVideo": True
            }
        })

    if selenoid_url:
        driver = webdriver.Remote(
            command_executor=selenoid_url,
            options=options
        )
        browser.config.driver = driver
    else:
        browser.config.driver_options = options

    yield browser

    attach.add_screenshot(browser)
    attach.add_logs(browser)
    attach.add_html(browser)
    if os.getenv("SELENOID_URL"):
        attach.add_video(browser)
    browser.quit()