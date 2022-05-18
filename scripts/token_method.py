import os
import zipfile

# from seleniumwire import webdriver
from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent import futures
import time
import random

PATH = "chromedriver.exe"

workers = 5 # Tasks Amount
invite_link = "https://discord.gg/yRS5wG2J"
channel_link = 'https://discord.com/channels/914243808017932321/914245613179256872'
verify_button = '//*[@id="message-reactions-934973236121337887"]/div[1]/div/div/div' #Copy XPATH of react button. Found with inspect element
invite_count = 25
invited = 0
needs_verify = True 
close_on_finish = False


tokens = "tokens.txt"
proxies = "proxies.txt"

directory = 'C:\\Users\\kacpe\\OneDrive\\Desktop\\discord-inviter-main' #edit this to your directory where the file is located.
f = open(os.path.join(directory, tokens), "r")
nxt = f.readline()
tokens = []

while nxt != "":
    # print("Token added: " + nxt)
    nxt = nxt.replace("\n", "")
    tokens.append(nxt)
    nxt = f.readline()

if len(tokens) < 1:
    print("ERROR: No tokens found in tokens.txt")
    exit()
elif len(tokens) < invite_count:
    print("ERROR: Not enough tokens in tokens.txt")
    exit()

f.close()

# redeemed_file = open('tokens/bad_tokens.txt')
# tokens_redeemed = {}

# while nxt != "":
#     parts = nxt.split(":")
#     tok = parts[0]
#     invite = parts[1]
#     tok_lst = tokens_redeemed[invite]
#     if not tok_lst:
#         tok_lst = []
#     tokens_redeemed[invite] = tok_lst.append(tok)

f = open(os.path.join(directory, proxies), "r")
nxt = f.readline()
proxies = []

while nxt != "":
    proxies.append(nxt)
    nxt = f.readline()

f.close()

def new_instance(token):
    global invite_count
    global invited

    if invited >= invite_count:
        print("Invite count set has been met. Quitting...")
        return

    try:
        # if token in tokens_redeemed and tokens_redeemed[token] == invite_link:
        #     print(f"{token} already joined server")
        #     return

        good_proxy = False

        while not good_proxy:
            rand_proxy = proxies[random.randrange(0, len(proxies))].split(":")
            if len(rand_proxy) < 4:
                print("ERROR: Check proxy format")
                continue

            # Proxy needs to be in user:pass@ip:port
            proxy_str = rand_proxy[2] + ":" + rand_proxy[3][:-1] + "@" + rand_proxy[0] + ":" + rand_proxy[1]
            # print(proxy_str)

            options = {
                'proxy': {
                    'http': 'http://' + proxy_str,
                    'https': 'https://' + proxy_str,
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }
            try:
                # ser = Service(PATH)
                driver = webdriver.Chrome(PATH, seleniumwire_options = options)
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
            add_server = WebDriverWait(driver, 10).until(
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

            invite_link_box.send_keys(invite_link)
            join_server_final = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div/div/div/div[3]/button[1]"))
            )
            time.sleep(1)
            join_server_final.click()
            time.sleep(5)

            try:
                join_server_final.click()
                print("ERROR: Invite Link invalid")
                return
            except (NoSuchElementException, StaleElementReferenceException):
                print(f"Successfully joined server [{token}]")
                invited += 1

                # DO STUFF HERE AFTER JOIN (Verification via react)

                if needs_verify:
                    try:
                        time.sleep(2)
                        driver.get(channel_link)
                        time.sleep(1)
                        verify_react = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, verify_button))
                        )
                        verify_react.click()
                        time.sleep(1)
                        
                        # Handling for rules pop up (Checkbox and submit)
                        try:
                            complete_button = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@id="app-mount"]/div[4]/div[3]/div/div/div[2]/div[1]/div[1]/div/div/div/div[3]/div/label/input'))
                            )
                            complete_button.click()
                            time.sleep(1)

                            submit_button = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@id="app-mount"]/div[4]/div[2]/div/div/div[2]/div[2]/button'))
                            )
                            submit_button.click()
                            time.sleep(1)
                            verify_react.click()

                        except (NoSuchElementException, TimeoutException):
                            # print("No extra verification")
                            pass
                        
                        print(f"Verified [{token}]")

                    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                        print(f"Could not find verify [{token}]")
                        pass
                    

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
            print(f"ERROR: Check token [{token}]")
            return

    except TimeoutException:
        print("Session Timed Out")  

# Threading Multiple instances
# Adjust max_workers to change how many drivers open
# Too many workers will lead to slower loads == more prone to error

# To edit whether browser closes on finish see variable above (close_on_finish)
# The purpose of leaving it open is to do stuff needed for some servers

with futures.ThreadPoolExecutor(max_workers=workers) as executor:
    executor.map(new_instance, tokens)
      

print(f"Successfully joined server with {invited} accounts.")
print("END OF SCRIPT")

quit()