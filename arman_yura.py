from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import warnings
import json
import os
from datetime import datetime
from jinja2 import Template
warnings.filterwarnings("ignore", category=DeprecationWarning)

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get("http://tylerpaw.co.fort-bend.tx.us/PublicAccess/default.aspx")

# click on Criminal Case Records
driver.find_element(By.LINK_TEXT, "Criminal Case Records").click()


class Scraper:
    def __init__(self, internal_id, name, surname, middle_name, date_of_birth):
        self.internal_id = internal_id
        self.name = name
        self.surname = surname
        self.middle_name = middle_name
        self.date_of_birth = date_of_birth

    def submit_form(self):

        self.driver = webdriver.Chrome(PATH)
        self.driver.get(DESTINATION_URL)

        # click on Criminal Case Records
        self.driver.find_element(By.LINK_TEXT, "Criminal Case Records").click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "LastName")))
        ln = self.driver.find_element(By.ID, "LastName")
        ln.clear()
        ln.send_keys(self.surname)

        fn = self.driver.find_element(By.ID, "FirstName")
        fn.clear()
        fn.send_keys(self.name)

        mid = self.driver.find_element(By.ID, "MiddleName")
        mid.clear()
        mid.send_keys(self.middle_name)

        dob = self.driver.find_element(By.ID, "DateOfBirth")
        dob.clear()
        dob.send_keys(self.date_of_birth)

        self.driver.find_element(By.ID, "SearchSubmit").click()

    def get_primary_dict(self):

        # Constructing the dictionary
        results = {"primary": {}, "aliases": {}, 'info': {}}
        results["primary"]['First_Name'] = first
        results["primary"]['Last_Name'] = last
        results["primary"]['Middle_Name'] = middle
        results["primary"]['Date_of_Birth'] = birth[-4:] + birth[0:2] + birth[3:5]
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

        results["info"][f"case_{i - 2}"] = {}

        results["info"][f"case_{i - 2}"]['First_Name'] = first
        results["info"][f"case_{i - 2}"]['Last_Name'] = last
        results["info"][f"case_{i - 2}"]['Middle_Name'] = middle
        results["info"][f"case_{i - 2}"]['Suffix'] = ""

        # Getting Middle Name and Suffix from case page defendant part
        if len(driver.find_element(By.ID, "PIr11").text.split(' ')) == 3 and not results["info"][f"case_{i - 2}"]['Middle_Name']:
            results["info"][f"case_{i - 2}"]['Middle_Name'] = driver.find_element(By.ID, "PIr11").text.split(' ')[-1]
        elif len(driver.find_element(By.ID, "PIr11").text.split(' ')) > 3:
            if driver.find_element(By.ID, "PIr11").text.split(' ')[-1] != middle:
                results["info"][f"case_{i - 2}"]['Suffix'] = driver.find_element(By.ID, "PIr11").text.split(' ')[-1]

        tb_number = 4
        if driver.find_element(By.CLASS_NAME, "ssCaseDetailSectionTitle").text == "Related Case Information":
            tb_number += 1
        sub_tb_number = tb_number

        results["info"][f"case_{i - 2}"]['Gender'] = ""
        results["info"][f"case_{i - 2}"]['Race'] = ""
        results["info"][f"case_{i - 2}"]['City'] = ""
        results["info"][f"case_{i - 2}"]['State'] = ""
        results["info"][f"case_{i - 2}"]['Zip'] = ""

        try:
            results["info"][f"case_{i - 2}"]['Gender'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[2]/td[2]").text.split(' ')[0]
            results["info"][f"case_{i - 2}"]['Race'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[2]/td[2]").text.split(' ')[1].split('\n')[0]
        except:
            continue

        try:
            results["info"][f"case_{i - 2}"]['City'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[3]/td").text.replace(" ", "").split(',')[0]
            results["info"][f"case_{i - 2}"]['State'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[3]/td").text.replace(" ", "").split(',')[1][:2]
            results["info"][f"case_{i - 2}"]['Zip'] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number}]/tbody/tr[3]/td").text.replace(" ", "").split(',')[1][2:]
        except:
            continue

        results["info"][f"case_{i - 2}"]['Category'] = "CRIMINAL"
        results["info"][f"case_{i - 2}"]['CourtJurisdiction'] = 'FORT BEND'
        results["info"][f"case_{i - 2}"]['CaseFileDate'] = ""
        results["info"][f"case_{i - 2}"]['CaseNumber'] = ""
        results["info"][f"case_{i - 2}"]['CourtName'] = ""

        try:
            cfd = driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr/td/table/tbody/tr[2]/td/b").text
            results["info"][f"case_{i - 2}"]['CaseFileDate'] = cfd[-4:] + cfd[0:2] + cfd[3:5]
            results["info"][f"case_{i - 2}"]['CaseNumber'] = driver.find_element(By.XPATH, "/html/body/div[2]/span").text
            results["info"][f"case_{i - 2}"]['CourtName'] = driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr/td/table/tbody/tr[3]/td/b").text
        except:
            continue


        # charge(s)
        all_page_tables = driver.find_elements(By.XPATH, "/html/body/table")
        table_sequence = 0
        for rank in range(len(all_page_tables)):
            try:
                if all_page_tables[rank].find_element(By.XPATH, "./caption/div").text == "Charge Information":
                    table_sequence -= rank
            except:
                continue
            try:
                if all_page_tables[rank].find_element(By.XPATH, "./caption/div").text == "Events & Orders of the Court":
                    table_sequence += rank
            except:
                continue

        charge_table = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody")
        ct_trs = charge_table.find_elements(By.TAG_NAME, "tr")

        counter = 0
        for j in range(1, len(ct_trs), 2):
            counter += 1
            results["info"][f"case_{i - 2}"][f"charge_{counter}"] = {}
            tds = ct_trs[j].find_elements(By.TAG_NAME, "td")
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["ChargeFileDate"] = ""
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["OffenseCode"] = ""
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["OffenseDescription"] = ""
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Severity"] = ""
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Statute"] = ""
            try:
                results["info"][f"case_{i - 2}"][f"charge_{counter}"]["ChargeFileDate"] = tds[5].text[-4:] + tds[5].text[0:2] + tds[5].text[3:5]
                results["info"][f"case_{i - 2}"][f"charge_{counter}"]["OffenseCode"] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1 + j}]/td[4]").text + " - " + \
                                                                                       driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1 + j}]/td[2]").text
                results["info"][f"case_{i - 2}"][f"charge_{counter}"]["OffenseDescription"] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1 + j}]/td[2]").text
                results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Severity"] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1 + j}]/td[5]").text
                results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Statute"] = driver.find_element(By.XPATH, f"/html/body/table[{tb_number + 1}]/tbody/tr[{1 + j}]/td[4]").text
            except:
                continue

            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["CountyOrJurisdiction"] = "FORT BEND"
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Sentence"] = ""
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Disposition"] = ""
            results["info"][f"case_{i - 2}"][f"charge_{counter}"]["DispositionDate"] = ""

            if table_sequence == 1:
                if j == 1:
                    sub_tb_number = tb_number - 1
                results["info"][f"case_{i - 2}"][f"charge_{counter}"]["ArrestDate"] = results["info"][f"case_{i - 2}"][f"charge_{counter}"]["ChargeFileDate"]
                results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Comment"] = ""
            else:
                ad = driver.find_element(By.XPATH, f"/html/body/table[{sub_tb_number + 1 + j}]/tbody/tr[2]/td/table/tbody/tr[4]/td/table/tbody/tr/td[1]").text
                results["info"][f"case_{i - 2}"][f"charge_{counter}"]["ArrestDate"] = ad[-4:] + ad[0:2] + ad[3:5]
                results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Comment"] = driver.find_element(By.XPATH, f"/html/body/table[{sub_tb_number + 1 + j}]/tbody/tr[2]/td/table/tbody/tr[5]/td/table/tbody/tr/td[2]").text

            disposition_table = driver.find_element(By.XPATH, f"/html/body/table[{sub_tb_number + 3}]/tbody")
            dt_trs = disposition_table.find_elements(By.TAG_NAME, "tr")

            for k in range(len(dt_trs)):
                try:
                    if "Judgment" in dt_trs[k].text:
                        d = dt_trs[k].find_element(By.XPATH, "./td[3]/div/div/div/div[1]")
                        dd = dt_trs[k].find_element(By.TAG_NAME, "th")
                        results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Disposition"] = d.text
                        results["info"][f"case_{i - 2}"][f"charge_{counter}"]["DispositionDate"] = dd.text[-4:] + dd.text[0:2] + dd.text[3:5]
                except:
                    continue

                try:
                    if "Committed" in dt_trs[k].text:
                        nobr = dt_trs[k].find_element(By.XPATH, "./td[3]/div/div/div/div/table/tbody/tr[2]/td[2]/nobr")
                        sentence = nobr.find_elements(By.TAG_NAME, "span")
                        final_sentence = " ".join([" " + sentence[x].text for x in range(len(sentence))])
                        final_sentence = final_sentence.replace("  ", "")
                        final_sentence = final_sentence.replace(",", "")
                        results["info"][f"case_{i - 2}"][f"charge_{counter}"]["Sentence"] = final_sentence
                except:
                    continue

        driver.back()

time.sleep(2)

driver.quit()

with open(f"{last}_{first}.json", "w") as outfile:
    json.dump(results, outfile, indent=4)

dob_formatted = results["primary"]["Date_of_Birth"]

XMLgeneral = {}
XMLgeneral["ScrapedDate"] = datetime.now().strftime('%Y%m%d')
XMLgeneral["SearchCriteria"] = {}
XMLgeneral["SearchCriteria"]["DateOfBirth"] = dob_formatted[4:6] + "/" + dob_formatted[-2:] + "/" + dob_formatted[:4]
XMLgeneral["SearchCriteria"]["SourceSite"] = results["primary"]['Source_Site']
XMLgeneral["SearchCriteria"]["DataSource"] = results["primary"]['DATA_SOURCE']
XMLgeneral["SearchCriteria"]["From"] = "FORT BEND"
XMLgeneral["SearchCriteria"]["ScrapedDate"] = XMLgeneral["ScrapedDate"]
XMLgeneral["SearchCriteria"]["Name1"] = results["primary"]['Last_Name'].upper() + " " + results["primary"]['First_Name'].upper()

def countCharges(input, lookup):
    count = 0
    for key, value in input.items():
        if key.startswith(lookup):
            count += 1
    return count

XMLcases = []
for i in range(len(results["info"])):
    XMLcases.append({})
    XMLcases[i]["City"] = results["info"][f"case_{i+1}"]['City']
    XMLcases[i]["State"] = results["info"][f"case_{i+1}"]['State']
    XMLcases[i]["ZipCode"] = results["info"][f"case_{i+1}"]['Zip']
    XMLcases[i]["CaseFileDate"] = results["info"][f"case_{i+1}"]['CaseFileDate']
    XMLcases[i]["CaseNumber"] = results["info"][f"case_{i+1}"]['CaseNumber']
    XMLcases[i]["CourtName"] = results["info"][f"case_{i+1}"]['CourtName']
    XMLcases[i]["Offenses"] = []

    for j in range(1, countCharges(results["info"][f"case_{i+1}"], "charge")+1):
        charge = {}
        charge["ChargeFileDate"] = results["info"][f"case_{i+1}"][f"charge_{j}"]["ChargeFileDate"]
        charge["Comment"] = results["info"][f"case_{i+1}"][f"charge_{j}"]["Comment"]
        charge["Sentence"] = results["info"][f"case_{i + 1}"][f"charge_{j}"]["Sentence"]
        charge["ArrestDate"] = results["info"][f"case_{i+1}"][f"charge_{j}"]["ArrestDate"]
        charge["Disposition"] = results["info"][f"case_{i+1}"][f"charge_{j}"]["Disposition"]
        charge["DispositionDate"] = results["info"][f"case_{i+1}"][f"charge_{j}"]["DispositionDate"]
        charge["OffenseCode"] = results["info"][f"case_{i+1}"][f"charge_{j}"]["OffenseCode"]
        charge["OffenseDescription"] = results["info"][f"case_{i+1}"][f"charge_{j}"]["OffenseDescription"]
        charge["Severity"] = results["info"][f"case_{i+1}"][f"charge_{j}"]["Severity"]
        charge["Statute"] = results["info"][f"case_{i+1}"][f"charge_{j}"]["Statute"]
        XMLcases[i]["Offenses"].append(charge)

    XMLcases[i]["DateOfBirth"] = dob_formatted
    XMLcases[i]["DateOfBirthDay"] = dob_formatted[-2:]
    XMLcases[i]["DateOfBirthMonth"] = dob_formatted[4:6]
    XMLcases[i]["DateOfBirthYear"] = dob_formatted[:4]
    XMLcases[i]["first"] = results["info"][f"case_{i+1}"]['First_Name']
    XMLcases[i]["last"] = results["info"][f"case_{i+1}"]['Last_Name']
    XMLcases[i]["middle"] = results["info"][f"case_{i+1}"]['Middle_Name']
    XMLcases[i]["suffix"] = results["info"][f"case_{i+1}"]['Suffix']
    XMLcases[i]["Gender"] = results["info"][f"case_{i+1}"]['Gender']
    XMLcases[i]["Race"] = results["info"][f"case_{i+1}"]['Race']

current_folder_path, current_folder_name = os.path.split(os.path.abspath(__file__))
xmlTemplate = current_folder_path + '\\arman_yura.xml'
xml = open(xmlTemplate).read()
template = Template(xml)
rep = template.render(general=XMLgeneral, subjects=XMLcases)
open(f"{last}_{first}.xml", "w").write(rep)
