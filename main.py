import json
import os

from linkedin import LinkedIn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_cookies(username):
    cookies_path = os.path.join(BASE_DIR, "cookies", f"{username}.json")
    if os.path.exists(cookies_path):
        with open(cookies_path, "r") as f:
            cookies = json.load(f)
            return cookies


def save_cookies(username, cookies):
    cookies_path = os.path.join(BASE_DIR, "cookies", f"{username}.json")
    with open(cookies_path, "w") as f:
        json.dump(cookies, f, indent=4)


def login(username: str, password: str, callback):
    linkedin = LinkedIn()
    linkedin.get_2fa_callback = callback

    cookies = get_cookies(username)

    # checks whether the user is already logged in
    if cookies:
        linkedin.login(cookies=cookies)
        return linkedin

    else:
        login_result = linkedin.login(username, password)
        if login_result["status"] == "error":
            raise Exception("login error")
        elif login_result["status"] == "partial":
            if linkedin.get_2fa_callback:
                pin = linkedin.get_2fa_callback()
                login_result = linkedin.authenticate_2fa(
                    pin, login_result["current_url"], login_result["cookies"]
                )
                if login_result["status"] == "error":
                    raise Exception("2fa authentication error")
                else:
                    save_cookies(username, login_result["cookies"])
            else:
                raise Exception("'get_2fa_callback' is not handled")
        elif login_result["status"] == "success":
            save_cookies(username, login_result["cookies"])

        return linkedin


if __name__ == "__main__":

    def get_otp():
        return input("enter otp: ")

    linkedin = login("<email/username>", "<password>", get_otp)
    linkedin.client.save_screenshot("check.png")
    print(linkedin.image_url)
    print(linkedin.profile_name)
    linkedin.close()
