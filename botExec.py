from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from getpass import getpass
from termcolor import colored
import time
import os
os.system("")


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

def main():
    # LOAD LOGIN PAGE
    driver.get('https://cas.rutgers.edu/login?service=https%3A%2F%2Fsims.rutgers.edu%2Fwebreg%2Fj_spring_cas_security_check')

    logged_in = False

    while not logged_in:
        # USERNAME INFO
        usr = driver.find_element_by_id("username")
        usr_name = input(colored("Net ID:", 'white', attrs = ['underline']) + " ")
        usr.send_keys(usr_name)

        # PASSWORD INFO
        pwd = driver.find_element_by_id("password")
        usr_pwd = getpass(colored("Password:", 'white', attrs = ['underline']) + " ")
        pwd.send_keys(usr_pwd)
        driver.find_element_by_name("submit").click()

        # CHECK LOGIN STATE
        try:
            driver.find_element_by_class_name("semesterInputClass")
        except:
            print("\nInvalid Credentials, please try again\n")
            driver.find_element_by_id("username").clear()
            driver.find_element_by_id("password").clear()
            continue
        print("\nLogged in Successfully")
        logged_in = True

    # SET SECTIONS
    section_dict = {}
    number_sections = 0
    while True:
        number_sections = int(input("\nHow many sections would you like to snipe? Min 1 and Max 5 allowed: "))
        if number_sections <= 5 and number_sections >= 1:
            break
        else: print("Min 1 section and Max 5 sections allowed")
    for i in range(number_sections):
        section_dict[i] = input("Enter the INDEX number of Section " + str(i + 1) + ": ")

    # INFORMATION
    print("\nAttempting to snipe sections. This may take a while\n")
    print(colored("Important Information", 'yellow', attrs = ['bold', 'underline']))
    print("•Please leave this program running in the background, it will stop automatically if a section has been sniped or WebReg is closed at 2 am")
    print("•Once a section is sniped, no other selected sections can be sniped until you restart the program and re-enter the desired sections")

    # LOAD APPDATA
    driver.find_element_by_name("submit").click()
    driver.get('https://sims.rutgers.edu/webreg/courseLookup.htm?_flowId=lookup-flow')
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID,"iframe2")))
    driver.find_element_by_id("campus_NB").click()
    driver.find_element_by_id("level_U").click()
    driver.find_element_by_id("continueButton").click()

    # SEARCH OPEN SECTIONS ARRAY
    found = False
    refresh_count = 0
    section = ""
    sem = driver.execute_script("return AppData.selectedSemester;")
    time.sleep(5)
    array = driver.execute_script("return AppData.openSections;")
    while not(time.localtime(time.time()).tm_hour < 6 and time.localtime(time.time()).tm_hour >= 2):
        for key in section_dict:
            found = section_search(section_dict[key], array)
            if found: 
                section = section_dict[key]
                break
        if found: break
        driver.execute_script("CourseDownloadService.downloadCourses();")
        array = driver.execute_script("return AppData.openSections;")
        if refresh_count == 30:
            driver.refresh()
            time.sleep(1)
            driver.refresh()
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID,"iframe2")))
            driver.find_element_by_id("campus_NB").click()
            driver.find_element_by_id("level_U").click()
            driver.find_element_by_id("continueButton").click()
            refresh_count = 0
        refresh_count += 1
        time.sleep(10)

    # CHECK WEBREG STATUS
    if time.localtime(time.time()).tm_hour < 6 and time.localtime(time.time()).tm_hour >= 2:
        print("WebReg has closed, try sniping again tomorrow")
        return

    # ATTEMPT SECTION SNIPE
    print("\nAttempting to snipe section " + section)
    snipe(section, sem)

    # CLOSE DRIVERS
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.close()

def section_search(section, arr) -> bool:
    mid = int((len(arr) - 1) / 2)
    lower = 0
    higher = len(arr) - 1

    # BINARY SEARCH
    while lower <= higher:
        if section == arr[mid]:
            return True
        elif section > arr[mid]:
            lower = mid + 1
        else: higher = mid - 1
        mid = int((lower + higher) / 2)
    return False

def snipe(section, sem):
    # OPEN SNIPE WINDOW
    driver.execute_script("window.open()")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("http://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection=" + sem + "&indexList=" + section)
    driver.find_element_by_id("submit").click()

    # CHECK RESULT OF SNIPE ATTEMPT
    sniped_complete = False
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'info')))
    try:
        error_message = driver.find_element_by_class_name("error").text
    except:
        sniped_complete = True
    
    if sniped_complete:
        print(colored("\nSuccesfully sniped section " + section + "!", 'white', attrs = ['blink']))
    else:
        print(colored("\nThe following error occured: ", 'white', attrs = ['blink']))
        print(error_message)

main()