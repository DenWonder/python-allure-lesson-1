import pytest
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selene import Browser, Config

from utils import attach

@pytest.fixture(scope='function')
def setup_browser(request):
    options = Options()
    selenoid_capabilities = {
        "browserName": "chrome",
        "browserVersion": "100.0",
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": True
        }
    }
    options.capabilities.update(selenoid_capabilities)
    if os.getenv("CI"):  # GitHub Actions автоматически выставляет CI=true
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
    # driver = webdriver.Remote(
    #     # command_executor=f"https://user1:1234@selenoid.autotests.cloud/wd/hub",
    #     options=options
    # )
    driver = webdriver.Chrome(options=options)

    browser = Browser(Config(driver))
    yield browser

    attach.add_screenshot(browser)
    attach.add_logs(browser)
    attach.add_html(browser)
    # attach.add_video(browser)

    browser.quit()