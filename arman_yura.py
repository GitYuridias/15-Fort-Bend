from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import warnings
import json
from datetime import datetime
warnings.filterwarnings("ignore", category=DeprecationWarning)

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get("http://tylerpaw.co.fort-bend.tx.us/PublicAccess/default.aspx")

# click on Criminal Case Records
driver.find_element(By.LINK_TEXT, "Criminal Case Records").click()

# fill in the form (last name, first name, dob) and submit
# Fixme: try this for "Lee, Derrick Tinnell" who has 2 charges; also fix inconsistencies in XPATH
# last = "Candler"
# first = "James"
# middle = ""
# birth = "07/23/1954"

# last = "Candler"
# first = "James"
# middle = ""
# birth = "07/23/1954"

last = "Williams"
first = "Willie"
middle = "Charles"
birth = ""

Internal_ID = "0436D707-7660-444E-84E4-3F7F89675B60"

WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "LastName")))
ln = driver.find_element(By.ID, "LastName")
ln.clear()
ln.send_keys(last)

fn = driver.find_element(By.ID, "FirstName")
fn.clear()
fn.send_keys(first)

mid = driver.find_element(By.ID, "MiddleName")
mid.clear()
mid.send_keys(middle)

dob = driver.find_element(By.ID, "DateOfBirth")
dob.clear()
dob.send_keys(birth)

driver.find_element(By.ID, "SearchSubmit").click()
driver.implicitly_wait(5)

# Constructing the dictionary
results = {"primary": {}, "aliases": {}, 'info': {}}
results["primary"]['First_Name'] = first
results["primary"]['Last_Name'] = last
results["primary"]['Middle_Name'] = middle
results["primary"]['Date_of_Birth'] = birth[:-4] + birth[0:2] + birth[3:5]
results["primary"]['State_Abbreviation'] = "TX"
results["primary"]['Area'] = "Fort Bend"
results["primary"]['today'] = str(datetime.today())
results["primary"]['Internal_ID'] = Internal_ID
results["primary"]['Source_Site'] = "https://www.fortbendcountytx.gov/government/courts/court-records-research"
results["primary"]['DATA_SOURCE'] = "TX_FORT_BEND"
results["primary"]['status'] = "Complete"
results["primary"]['Result_Not_Found'] = 'false'
results["primary"]['Search_Type'] = "CRIMINAL"

if int(driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr[1]/td[2]/b").text) == 0:

    print('No cases for that person found')
    results["primary"]['Result_Not_Found'] = 'true'

else:
    rows = driver.find_elements(By.XPATH, "/html/body/table[4]/tbody/tr")

    for i in range(3, len(rows) + 1):

        driver.find_element(By.XPATH, f"/html/body/table[4]/tbody/tr[{i}]/td[1]/a").click()

        driver.implicitly_wait(2)
        # Getting Middle Name and Suffix from case page defendant part
        if len(driver.find_element(By.ID, "PIr11").text.split(' ')) == 3 and not results["primary"]['Middle_Name']:
            results["primary"]['Middle_Name'] = driver.find_element(By.ID, "PIr11").text.split(' ')[-1]
        elif len(driver.find_element(By.ID, "PIr11").text.split(' ')) > 3:
            results["primary"]['Suffix'] = driver.find_element(By.ID, "PIr11").text.split(' ')[-1]

        tb_number = 4
        if driver.find_element(By.CLASS_NAME, "ssCaseDetailSectionTitle").text == "Related Case Information":
            tb_number += 1

        results["primary"]['Gender'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[2]/td[2]").text.split(' ')[0]
        results["primary"]['Race'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[2]/td[2]").text.split(' ')[1].split('\n')[0]

        # all_page_tables = driver.find_elements(By.XPATH, "/html/body/table")

        results["info"][f"case_{i - 2}"] = {}


        results["info"][f"case_{i - 2}"]['City'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[3]/td").text.replace(" ", "").split(',')[0]
        results["info"][f"case_{i - 2}"]['State'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[3]/td").text.replace(" ", "").split(',')[1][:2]
        results["info"][f"case_{i - 2}"]['Zip'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[3]/td").text.replace(" ", "").split(',')[1][2:]

        cfd = driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr/td/table/tbody/tr[2]/td/b").text
        results["info"][f"case_{i - 2}"]['CaseFileDate'] = cfd[-4:] + cfd[0:2] + cfd[3:5]
        results["info"][f"case_{i - 2}"]['CaseNumber'] = driver.find_element(By.XPATH, "/html/body/div[2]/span").text
        results["info"][f"case_{i - 2}"]['Category'] = "CRIMINAL"
        results["info"][f"case_{i - 2}"]['CourtJurisdiction'] = 'FORT BEND'
        results["info"][f"case_{i - 2}"]['CourtName'] = driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr/td/table/tbody/tr[3]/td/b").text

        # charge(s)

        charge_table = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody")
        disposition_table = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 3}]/tbody")
        ct_trs = charge_table.find_elements(By.TAG_NAME, "tr")
        dt_trs = disposition_table.find_elements(By.TAG_NAME, "tr")
        counter = 0
        # Fixme: try this for "Lee, Derrick Tinnell" who has 2 charges; also fix inconsistencies in XPATH
        for j in range(1, len(ct_trs), 2):
            counter += 1
            results["info"][f"case_{i - 2}"][f"charge_{counter}"] = {}
            tds = ct_trs[j].find_elements(By.TAG_NAME, "td")
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["ChargeFileDate"] = tds[5].text[-4:] + tds[5].text[0:2] + tds[5].text[3:5]
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Comment"] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1 +j}]/tbody/tr[2]/td/table/tbody/tr[5]/td/table/tbody/tr/td[2]").text
            ad = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1 +j}]/tbody/tr[2]/td/table/tbody/tr[4]/td/table/tbody/tr/td[1]").text
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["ArrestDate"] = ad[-4:] + ad[0:2] + ad[3:5]
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["CountyOrJurisdiction"] = "FORT BEND"
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Sentence"] = ""

            for k in range(len(dt_trs)):

                if "Judgment" in dt_trs[k].text:
                    d = dt_trs[k].find_element(By.XPATH, "./td[3]/div/div/div/div[1]")
                    dd = dt_trs[k].find_element(By.TAG_NAME, "th")
                    results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Disposition"] = d.text
                    results["info"][f"case_{i - 2}"][f"charge_{counter}"]["DispositionDate"] = dd.text[-4:] + dd.text[0:2] + dd.text[3:5]

                if "Committed" in dt_trs[k].text:
                    nobr = dt_trs[k].find_element(By.XPATH, "./td[3]/div/div/div/div/table/tbody/tr[2]/td[2]/nobr")
                    sentence = nobr.find_elements(By.TAG_NAME, "span")
                    final_sentence = " ".join([" " + sentence[x].text for x in range(len(sentence))])
                    final_sentence = final_sentence.replace("  ", "")
                    final_sentence = final_sentence.replace(",", "")
                    results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Sentence"] = final_sentence

            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["OffenseCode"] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1+j}]/td[4]").text + " - " + \
                                                                                   driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1+j}]/td[2]").text
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["OffenseDescription"] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1+j}]/td[2]").text
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Severity"] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1+j}]/td[5]").text
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Statute"] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1+j}]/td[4]").text

        time.sleep(3)
        driver.back()

time.sleep(2)
#values = [{"key": k, "information": v} for k, v in results.items()]
#print(json.dumps(values, indent=4))

with open(f"{Internal_ID}.json", "w") as outfile:
    json.dump(results, outfile, indent=4)

driver.quit()
