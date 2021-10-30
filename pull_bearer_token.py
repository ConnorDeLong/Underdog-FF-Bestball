"""
Module is responsible for pulling a bearer token that can be used to scrape the API
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json


def create_webdriver(url, chromedriver_path, username, password):

    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        
    driver = webdriver.Chrome(chromedriver_path)
    driver.get(url)
    
    elem = driver.find_elements_by_class_name('styles__field__3fmc7')[0]
    elem.clear()
    elem.send_keys(username)
    elem.send_keys(Keys.RETURN)
    
    elem = driver.find_elements_by_class_name('styles__field__3fmc7')[1]
    elem.clear()
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)
    
    return driver


def pull_bearer_token(url, chromedriver_path, username, password):
    
    driver = create_webdriver(url, chromedriver_path, username, password)
    
    time.sleep(5)
    logs = driver.get_log("performance")

    for log in logs:
        try:
            log_dict = json.loads(log['message'])
            bearer_token = log_dict['message']['params']['response']['headers']['authorization']
            
            if bearer_token[:6] == "Bearer":
                break
            
        except:
            pass
        
    driver.close()
    driver.quit()
        
    return bearer_token


if __name__ == '__main__':
    
    import underdog_login_credentials
    
    url = "https://underdogfantasy.com/lobby"    
    chromedriver_path = r"C:\Users\conde\chromedriver\chromedriver.exe"
    username = underdog_login_credentials.USERNAME
    password = underdog_login_credentials.PASSWORD

    bearer_token = pull_bearer_token(url, chromedriver_path, username, password)

    print(bearer_token)