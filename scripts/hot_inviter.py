import os
import zipfile

# from seleniumwire import webdriver
from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent import futures
from selenium.webdriver.chrome.options import Options
import time
import random

PATH = "chomedriver.exe"
hot_tokens = "hot_tokens.txt"
proxies = "proxies.txt"
invite_link = "" #edit this to invite link

#Settings
workers = 10 # How Many Tasks Running at Once
close_on_finish = False

#CODE
directory = 'C:\\Users\\kacpe\\OneDrive\\Desktop\\discord-inviter-main' #edit this to your directory
f = open(os.path.join(directory, hot_tokens), "r")
nxt = f.readline()
tokens = []

while nxt != "":
    # print("Hot tokens added: " + nxt)
    nxt = nxt.replace("\n", "")
    tokens.append(nxt)
    nxt = f.readline()

if len(tokens) < 1:
    print("ERROR: No wallets found in Hot Tokens.txt")
    exit()

f.close()

f = open(os.path.join(directory, proxies), "r")
nxt = f.readline()
proxies = []

while nxt != "":
    proxies.append(nxt)
    nxt = f.readline()

f.close()

def new_instance(token):
    global invite_link

    try:
        
        good_proxy = False
        while not good_proxy:
            rand_proxy = proxies[random.randrange(0, len(proxies))].split(":")
            if len(rand_proxy) < 4:
                print("ERROR: Check proxy format")
                continue

            proxy_str = rand_proxy[2] + ":" + rand_proxy[3][:-1] + "@" + rand_proxy[0] + ":" + rand_proxy[1]
            # print(proxy_str)

            options = {
                'proxy': {
                    'http': 'http://' + proxy_str,
                    'https': 'https://' + proxy_str,
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }

            chrome_options = Options()
            # chrome_options.add_argument("--headless")
            try:
                # ser = Service(PATH)
                driver = webdriver.Chrome(PATH, options=chrome_options, seleniumwire_options=options)
                good_proxy = True
            except:
                pass

        driver.get("https://discord.com/login")

        # print(f"Signing into account [{token}]")
        driver.execute_script("function login(token) {setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `\"${token}\"`}, 50);setTimeout(() => {location.reload();}, 2500);}login(arguments[0]);", token)
    
        try:
            login_captcha = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#app-mount > div.app-1q1i1E > div > div > div > section > div > div.flexCenter-3_1bcw.flex-1O1GKY.justifyCenter-3D2jYp.alignCenter-1dQNNs > div > iframe"))
                )

            time.sleep(3)

            try:
                login_captcha.is_displayed()
                print("Login Captcha Detected")

                driver.execute_script("function login(token) {setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `\"${token}\"`}, 50);setTimeout(() => {location.reload();}, 2500);}login(arguments[0]);", token)

            except (TimeoutException):
                print("ERROR: Captcha not solved")
                # driver.close()
                return
        except (TimeoutException):
            pass

        try:
            # Note that the following XPATH/Selectors are based on the English version of Discord. Won't work if language for account is set to a diff languange
            add_server = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Add a Server']"))
            )
            time.sleep(1)
            add_server.click()
            join_server = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div/div/div[3]/button"))
            )
            join_server.click()

            invite_link_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[placeholder='https://discord.gg/hTKzmak']"))
            )

            join_server_final = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div/div/div/div[3]/button[1]"))
            )

            print(f"Ready for invite link {token}")
            
            if invite_link == "":
                invite_link = input('')

            invite_link_box.send_keys(invite_link)
            
            join_server_final.click()
            time.sleep(5)

            try:
                join_server_final.click()
                print("ERROR: Invite Link invalid")
                return
            except (NoSuchElementException, StaleElementReferenceException):
                print(f"Successfully joined server [{token}]")

                if close_on_finish:
                    time.sleep(1)
                    driver.close()
                else:
                    while True:
                        try:
                            _ = driver.window_handles
                        except BaseException as e:
                            # print("Browser closed")
                            break
                        time.sleep(0.5)
                return

        except (TimeoutException):
            # while True:
            #             try:
            #                 _ = driver.window_handles
            #             except BaseException as e:
            #                 # print("Browser closed")
            #                 break
            #             time.sleep(0.5)
            print(f"ERROR: Check token [{token}]")
            return

    except TimeoutException:
        print("Session Timed Out")  

# Threading Multiple instances
# Adjust max_workers to change how many drivers open
# Too many workers will lead to slower loads == more prone to error

# To edit whether browser closes on finish see variable above (close_on_finish)
# The purpose of leaving it open is to do verification needed for some servers

with futures.ThreadPoolExecutor(max_workers=workers) as executor:
    executor.map(new_instance, tokens)
      
print("END OF SCRIPT")

quit()