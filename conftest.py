import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selene.support.shared import browser
from selene import Browser, Config
from utils import attach


@pytest.fixture(scope='function')
def setup_browser():
    selenoid_url = os.getenv("SELENOID_URL")

    if selenoid_url:
        driver = webdriver.Remote(
            command_executor=selenoid_url,
            desired_capabilities={
                "browserName": "chrome",
                "browserVersion": "128.0",
                "selenoid:options": {
                    "enableVNC": True,
                    "enableVideo": True
                }
            }
        )
        browser = Browser(Config(driver=driver))
    else:
        options = Options()
        if os.getenv("CI"):
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
        browser = Browser(Config(driver_options=options))

    yield browser

    attach.add_screenshot(browser)
    attach.add_logs(browser)
    attach.add_html(browser)
    if selenoid_url:
        attach.add_video(browser)
    browser.quit()