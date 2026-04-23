import os
import allure
from allure_commons.types import AttachmentType

selenoid_url = os.getenv("SELENOID_URL")

def add_screenshot(browser):
    png = browser.driver.get_screenshot_as_png()
    allure.attach(body=png, name='screenshot', attachment_type=AttachmentType.PNG, extension='.png')


def add_logs(browser):
    log = "".join(f'{text}\n' for text in browser.driver.get_log(log_type='browser'))
    allure.attach(log, 'browser_logs', AttachmentType.TEXT, '.log')


def add_html(browser):
    html = browser.driver.page_source
    allure.attach(html, 'page_source', AttachmentType.HTML, '.html')


def add_video(browser):

    # Берём базовый URL без /wd/hub и credentials
    if "@" in selenoid_url:
        # https://user1:1234@selenoid.autotests.cloud/wd/hub -> https://selenoid.autotests.cloud
        base = selenoid_url.split("@")[1].replace("/wd/hub", "")
        protocol = selenoid_url.split("://")[0]
        video_url = f"{protocol}://{base}/video/{browser.driver.session_id}.mp4"
    else:
        # http://selenoid:4444/wd/hub -> http://selenoid:4444
        base = selenoid_url.replace("/wd/hub", "")
        video_url = f"{base}/video/{browser.driver.session_id}.mp4"

    html = "<html><body><video width='100%' height='100%' controls autoplay><source src='" \
           + video_url \
           + "' type='video/mp4'></video></body></html>"
    allure.attach(html, 'video_' + browser.driver.session_id, AttachmentType.HTML, '.html')