from selenium.webdriver.common.by import By

from .client import Client

class LinkedIn:
    def __init__(self) -> None:
        self.client = Client()
        self._profile_name = None
        self._image_url = None

        self.get_2fa_callback = None

    def login(self, username=None, password=None, cookies=None):
        return self.client.login(username=username,password=password,cookies=cookies)

    def authenticate_2fa(self, pin, url, cookies):
        return self.client._authenticate_2fa(pin, url, cookies)


    @property
    def cookies(self):
        return self.client.get_cookies()

    @property
    def profile_name(self):
        if self._profile_name:
            return self._profile_name
        element  = self.client.find_element(By.CLASS_NAME,"feed-identity-module__actor-meta")
        self._profile_name =  element.find_element(By.TAG_NAME,'a').text
        return self._profile_name
    
    @property
    def image_url(self):
        if self._image_url:
            return self._image_url
        
        element  = self.client.find_element(By.CLASS_NAME,"feed-identity-module__actor-meta")
        self._image_url =  element.find_element(By.TAG_NAME,'a').get_attribute('href')
        return self._image_url

    def close(self):
        self.client.quit()