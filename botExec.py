from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

def main():
    # LOAD LOGIN PAGE
    driver.get('https://cas.rutgers.edu/login?service=https%3A%2F%2Fsims.rutgers.edu%2Fwebreg%2Fj_spring_cas_security_check')

    # USERNAME INFO
    usr = driver.find_element_by_id("username")
    usr_name = input("Net ID: ")
    usr.send_keys(usr_name)

    # PASSWORD INFO
    pwd = driver.find_element_by_id("password")
    usr_pwd = input("Password: ")
    pwd.send_keys(usr_pwd)
    driver.find_element_by_name("submit").click()

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
    print('\033[1m' + '\033[4m' + "\nImportant Information" + '\033[0m')
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
    section = ""
    time.sleep(5)
    array = driver.execute_script("return AppData.openSections;")
    while True:
        for key in section_dict:
            if section_dict[key] in array: 
                section = section_dict[key]
                found = True
                break
        if found: break
        driver.execute_script("CourseDownloadService.downloadCourses();")
        array = driver.execute_script("return AppData.openSections;")
        time.sleep(10)

    # ATTEMPT SECTION SNIPE
    print('\033[1m' + "\nAttempting to snipe section " + section + '\033[0m')
    snipe(section)

    # CLOSE DRIVERS
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.close()


def snipe(section):
    # OPEN SNIPE WINDOW
    driver.execute_script("window.open()")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("http://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection=92021&indexList=" + section)
    driver.find_element_by_id("submit").click()

    # CHECK RESULT OF SNIPE ATTEMPT
    sniped_complete = False
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'info')))
    try:
        error_message = driver.find_element_by_class_name("error").text
    except:
        sniped_complete = True
    
    if sniped_complete:
        print('\033[1m' + "\nSuccesfully sniped " + section + "!" + '\033[0m')
    else:
        print('\033[1m' + "\nThe following error occured: " + '\033[0m')
        print(error_message)

main()