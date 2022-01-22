from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import warnings
from datetime import datetime
warnings.filterwarnings("ignore", category=DeprecationWarning)

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get("http://tylerpaw.co.fort-bend.tx.us/PublicAccess/default.aspx")

# click on Criminal Case Records
driver.find_element(By.LINK_TEXT, "Criminal Case Records").click()

# fill in the form (last name, first name, dob) and submit
last = "Candler"
first = "James"
birth = "07/23/1954"
Internal_ID = "0436D707-7660-444E-84E4-3F7F89675B60"


WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "LastName")))
ln = driver.find_element(By.ID, "LastName")
ln.clear()
ln.send_keys(last)

fn = driver.find_element(By.ID, "FirstName")
fn.clear()
fn.send_keys(first)

dob = driver.find_element(By.ID, "DateOfBirth")
dob.clear()
dob.send_keys(birth)

driver.find_element(By.ID, "SearchSubmit").click()
driver.implicitly_wait(5)

# Constructing the dictionary
results = {"primary": {}, "aliases": {}, 'info': {}}
results["primary"]['First_Name'] = first
results["primary"]['Last_Name'] = last
results["primary"]['Date_of_Birth'] = birth[:-4] + birth[0:2] + birth[3:5]
results["primary"]['State_Abbreviation'] = "TX"
results["primary"]['Area'] = "Fort Bend"
results["primary"]['today'] = datetime.today()
results["primary"]['Internal_ID'] = Internal_ID
results["primary"]['Source_Site'] = "https://www.fortbendcountytx.gov/government/courts/court-records-research"
results["primary"]['DATA_SOURCE'] = "TX_FORT_BEND"
results["primary"]['status'] = "Complete"
results["primary"]['Result_Not_Found'] = 'false'
results["primary"]['Search_Type'] = "CRIMINAL"

if int(driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr[1]/td[2]/b").text) == 0:

    print('No cases for that person found')
    results["primary"]['Result_Not_Found'] = 'true'
    # driver.quit()

else:
    rows = driver.find_elements(By.XPATH, "/html/body/table[4]/tbody/tr")

    for i in range(3, len(rows) + 1):
        driver.find_element(By.XPATH, f"/html/body/table[4]/tbody/tr[{i}]/td[1]/a").click()
        driver.implicitly_wait(2)
        all_page_tables = driver.find_elements(By.XPATH, "/html/body/table")
        results["info"][f"case_{i - 2}"] = {}
        results["info"][f"case_{i - 2}"]['City'] = driver.find_element(By.XPATH, "/html/body/table[5]/tbody/tr[3]/td").text.replace(" ", "").split(',')[0]
        results["info"][f"case_{i - 2}"]['State'] = driver.find_element(By.XPATH, "/html/body/table[5]/tbody/tr[3]/td").text.replace(" ", "").split(',')[1][:2]
        results["info"][f"case_{i - 2}"]['Zip'] = driver.find_element(By.XPATH, "/html/body/table[5]/tbody/tr[3]/td").text.replace(" ", "").split(',')[1][2:]

        # FIXME dzel date i format@
        results["info"][f"case_{i - 2}"]['CaseFileDate'] = driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr/td/table/tbody/tr[2]/td/b").text
        results["info"][f"case_{i - 2}"]['CaseNumber'] = driver.find_element(By.XPATH, "/html/body/div[2]/span").text
        results["info"][f"case_{i - 2}"]['Category'] = "CRIMINAL"
        results["info"][f"case_{i - 2}"]['CourtJurisdiction'] = 'FORT BEND'

        # time.sleep(2)

            # driver.back()

#  webDriver.findElement(By.xpath("//a[@href='/docs/configuration']")).click();