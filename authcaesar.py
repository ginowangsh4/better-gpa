from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.keys import Keys

def authenticate(driver, username, password):
    print("=============")
    print("Starting Caesar Log In")

    url = "https://caesar.ent.northwestern.edu/";
    driver.get(url)

    delay = 30;
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'IDToken1')))
    except TimeoutException:
        print "Loading took too much time!"

    inputElement = driver.find_element_by_id("IDToken1")
    inputElement.send_keys(username)
    inputElement = driver.find_element_by_id("IDToken2")
    inputElement.send_keys(password + '\n');

    # Sleeping until 2FA page loaded
    sleep(0.1);

    twoFactorLoaded = False;
    while twoFactorLoaded == False:
        buttons = driver.find_elements_by_tag_name("input");
        for button in buttons:
            if (button.get_attribute('name') == "Login.Submit"):
                twoFactorLoaded = True;
                break;
        sleep(0.5);

    for _ in range(5):
        try:
            driver.execute_script("LoginSubmit('Continue'); return false;");
        except:
            pass;
        sleep(1);

    print("Waiting for 2FA approval...")

    delay = 60;
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'PTNUI_LAND_WRK_GROUPBOX14$PIMG')))
    except TimeoutException:
        print "Loading took too much time!"

    print("2FA Successful!");
    print("Logged into Caesar");
