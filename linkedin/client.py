import logging
from typing import Optional
from selenium.webdriver.remote.webelement import WebElement

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("undetected_chromedriver").setLevel(logging.CRITICAL)


class Client(uc.Chrome):
    LINKEDIN_URL = "https://www.linkedin.com/"
    default_timeout = 30

    def __init__(self, headless=True):
        super().__init__(headless=headless)
        self.get(self.LINKEDIN_URL)
        self.wait = WebDriverWait(self, self.default_timeout)
        self.wait.until(lambda x:self.execute_script("return document.readyState")=='complete')

    def _restore_login(self, cookies):
        self.delete_all_cookies()
        for cookie in cookies:
            self.add_cookie(cookie)
        self.refresh()

    def _authenticate_2fa(self, pin, url, cookies):
        self.delete_all_cookies()
        for cookie in cookies:
            self.add_cookie(cookie)

        self.get(url)

        try:
            # document.querySelector('input[name="pin"]')
            pin_ip = WebDriverWait(self, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="pin"]'))
            )

            # if element is present, then click on the element
            pin_ip.click()
            # fill the input field with the value
            pin_ip.send_keys(pin)
            
            # document.querySelector('button[type="submit"]')
            submit_btn = WebDriverWait(self, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[type="submit"]')
                )
            )
            # if element is present, then click on the element
            submit_btn.click()

            self.get(self.LINKEDIN_URL)

            self.refresh()

            # document.querySelector('span[title="Home"]')
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[title="Home"]'))
            )
            return {"status": "success", "cookies": self.get_cookies()}
        except Exception as e:
            logger.debug(e)
            return {"status": "error"}

    def _login(self, username, password):
        self.refresh()
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[name='session_key']")
                )
            )

            self.execute_script(
                f"document.getElementById('session_key').setAttribute('value','{username}')"
            )

            self.execute_script(
                f"document.getElementById('session_password').setAttribute('value', '{password}')"
            )

            self.execute_script(
                """document.querySelector('button[type="submit"]').click()"""
            )

            try:
                pin = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'input[name="pin"]')
                    )
                )
                return {
                    "status": "partial",
                    "current_url": self.current_url,
                    "cookies": self.get_cookies(),
                }

            except Exception as e:
                logger.debug(e)

                return {
                    "status": "success",
                    "cookies": self.get_cookies(),
                }

        except Exception as e:
            logger.debug(e)
            return {"status": "error"}
        

    def login(self, username=None, password=None, cookies=None):
        if cookies:
            self._restore_login(cookies)
        elif username and password:
            return self._login(username, password)
        else:
            raise Exception("Provide Valid Credentials")

