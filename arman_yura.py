from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get("http://tylerpaw.co.fort-bend.tx.us/PublicAccess/default.aspx")

# click on Criminal Case Records
driver.find_element(By.LINK_TEXT, "Criminal Case Records").click()

# fill in the form (last name, first name, dob) and submit
last = "Candler"; first = "James"; birth = "07/23/1954"

try:
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "LastName")))
    ln = driver.find_element(By.ID, "LastName")
    ln.clear()
    ln.send_keys(last)

    fn = driver.find_element(By.ID, "FirstName")
    fn.clear()
    fn.send_keys(first)

    dob = driver.find_element(By.ID, "DateFiledOnAfter")
    dob.clear()
    dob.send_keys(birth)

    driver.find_element(By.ID, "SearchSubmit").click()

finally:
    time.sleep(3)
    driver.quit()

driver.find_element(By.XPATH, "/html/body/table[4]/tbody/tr[3]/td[1]/a").click()