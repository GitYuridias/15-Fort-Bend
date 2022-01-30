# coding: utf8

import time, sys, os, os.path, datetime, re, csv, logging, glob, json, requests
from uuid import uuid1
from bs4 import BeautifulSoup
from jinja2 import Template
import errno
from operator import itemgetter
from .sandbox import webdriver
from .sandbox.webdriver.common.by import By
from .sandbox.webdriver.support.ui import WebDriverWait
from .sandbox.webdriver.support import expected_conditions as EC
from .sandbox.webdriver.common.keys import Keys
from .sandbox.webdriver.common.desired_capabilities import DesiredCapabilities
from .sandbox.common.exceptions import NoSuchElementException
from .sandbox.common.exceptions import SessionNotCreatedException
from .sandbox.webdriver.support.ui import Select


class Runner(object):

    def __init__(self, engine, args):
        self.logger = logging.getLogger("scanner.script")
        self.engine = engine
        self.url = 'http://tylerpaw.co.fort-bend.tx.us/PublicAccess/default.aspx'
        self.reportDir = 'Reports'
        self.CHROME_VERSION = 78
        self.chromeSilent = True
        self.delay = 1

        self.argiParse(args)
        self.update()
        
        self.info('Configuration loaded')
        
        current_folder_path, current_folder_name = os.path.split(os.path.abspath(__file__))
        self.chromedriver = current_folder_path+"\sandbox\driver\\v{}\chromedriver.exe".format(self.CHROME_VERSION)
        self.repPath = "{0}\\{1}".format(self.reportDir, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.xmlTemplate = current_folder_path+"\\sandbox\\inc\\template.xml"
        self.xmlRep = self.repPath+'\\{}.xml'
        self.intrDtc = current_folder_path+"\\sandbox\\inc\\" # 'C:\\Users\\yusha\\Desktop\\15 - Fort Bend\\lib\\sandbox\\inc\\'
        self.driver = None
        self.chrome_capabilities = None
        self.chrome_options = None
        self.state = None
        self.generalData = {}
        self.generalData['ScrapedDate'] = datetime.datetime.now().strftime("%Y%m%d")
        self.totalRecs = 0

        self.srch = {}
        self.caseList = {}
        self.clObtain = []
        self.bigDATA = []
        self.dataINF = []
        self.reGet = []
        self.lastFlag = ''
        self.details = []
        self.armFails = []
        self.noResults = False
        self.notRetred = True

        self.make_dir(self.reportDir)
        self.make_dir(self.repPath)

        self.prepareDriver()
        self.prepareReporter()
        self.prepareSearch(args)

    def argiParse(self,argv):
        args = [arg for arg in argv if arg.find('=') < 0]
        kwargs = {kw[0]:kw[1] for kw in [ar.split('=') for ar in argv if ar.find('=')>0]}
        for key, val in kwargs.items():
            setattr(self, key.lower(), val)

    def debug(self,mess):
        self.logger.debug(mess)

    def warning(self,mess):
        self.logger.warning(mess)
    
    def info(self,mess):
        self.logger.info(mess)

    def error(self,mess):
        self.logger.error(mess)

    def report(self,mess):
        self.reporter.info(mess)

    def reportErr(self,mess):
        self.reporter.info('\n [ ====== CRITICAL ====== ]\n\n'+ mess +'\n\nContact to Technical Personel\n\n ================================\n\n')

    def reportNetw(self,mess):
        self.reporter.info('[ NETWORK ISSUE ] - '+mess)

    def prepareReporter(self):
        self.reporter = logging.getLogger("reporter")
        self.reporter.setLevel(logging.INFO)
        fh = logging.FileHandler(self.repPath+"\\Report.txt")
        formatter = logging.Formatter('%(asctime)s ::: %(message)s',datefmt='%H:%M:%S')
        fh.setFormatter(formatter)
        self.reporter.addHandler(fh)

    def update(self):
        cnf = self.engine.cnf_get()
        self.CHROME_VERSION = int(cnf.get('chrome_version'))
        if str(cnf.get("silent")) == 'True':
            self.chromeSilent = True
        else:
            self.chromeSilent = False
        self.reportDir = str(cnf.get("report_directory"))
        self.delay = int(cnf.get("delay"))

    def prepareDriver(self):
        options = webdriver.ChromeOptions()
        if self.chromeSilent is True:
            options.add_argument("--headless")
            options.add_argument("--silent-launch")
            options.add_argument('--disable-gpu')
        options.add_argument("--log-level=3")    
        options.add_argument("--disable-web-security")
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--window-size=800,600')
        prefs = {"profile.default_content_settings.popups": 0,
                 "download.default_directory": r"{0}\\pdf\\".format(self.repPath), 
                 "directory_upgrade": True}
        options.add_experimental_option("prefs", prefs)
        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'browser':'ALL' }
        self.chrome_options = options
        self.chrome_capabilities = d
        self.info('Chrome Driver loaded')

    def prepareSearch(self, args):
        self.srch = {'last_first': [], 'date_of_birth': []}
        dobReq = ''
        ms = time.time_ns() // 1000000
        
        if args[0].lower().strip() == 't':
            f = ms
            self.generalData['RequestId'] = ''
        else:
            f = args[0].strip()
            self.generalData['RequestId'] = f
            
        self.xmlRep = self.xmlRep.format(f)

        v = str(args[1].strip())

        self.srch['date_of_birth'] = {'Y': v[-4:], 'M': v[0:2], 'D': v[3:5]}
         
        self.generalData['DateOfBirth'] = v
        self.generalData['SearchCriteria'] = {'DateOfBirth': v}
        args = args[2:]
        # print(f'Here are the args {args}')
        c = 0
        n = 1
        last_first = []
        for x in args:
            last_first.append(x.strip())
            # print(last_first)
            if c % 2 == 1:
                self.srch['last_first'].append(last_first)
                self.generalData['SearchCriteria']['Name{}'.format(n)] = ' '.join(last_first)

                last_first = []
                n += 1
            c += 1
            
            self.generalData['SearchCriteria']['SourceSite'] = self.url
            self.generalData['SearchCriteria']['DataSource'] = 'TX_FORT_BEND'
            self.generalData['SearchCriteria']['From'] = 'FORT BEND'
            td = datetime.date.today()
            self.generalData['SearchCriteria']['ScrapedDate'] = td.strftime("%Y%m%d")

    def request(self,u, s=False):
        session = requests.Session()
        session.headers.update({ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36' })
        try:
            if s:
                return session.get(u, stream=True, timeout=10)
            else:
                return session.get(u, timeout=10)
            
        except requests.exceptions.ReadTimeout:
            self.error('Target Read Timeout occured')
            self.reportNetw('Target Read Timeout occured')
            self.armFails.append('Target Read Timeout occured for {}'.format(u))
            print('Oops. Read timeout occured')
            return None

        except requests.exceptions.ConnectTimeout:
            self.error('Connection Timeout occured')
            self.reportNetw('Connection Timeout occured')
            self.armFails.append('Connection Timeout occured for {}'.format(u))
            print('Oops. Connection timeout occured!')
            return None

        except requests.exceptions.ConnectionError:
            self.error('Connection Error occured')
            self.reportNetw('Connection Error occured')
            self.armFails.append('Connection Error occured for {}'.format(u))
            print('Seems like dns lookup failed..')
            return None

    def xBuilder(self):
        xml = open(self.xmlTemplate).read()
        template = Template(xml)
        print(self.generalData)
        print(self.bigDATA)
        rep = template.render(general=self.generalData, subjects=self.bigDATA)
        open(self.xmlRep, "w").write(rep)


    def searchForm(self,last_name='',first_name=''):
        try:
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit' and @value='Search' and @name='SearchSubmit']")))
            
            print(' Search Form is Ready')
            dob = '{}/{}/{}'.format(self.srch['date_of_birth']['M'], self.srch['date_of_birth']['D'], self.srch['date_of_birth']['Y'])
            print(' Search Attempt for :', last_name + ', ' + first_name,  dob, sep=' ')

            sb = self.driver.find_element_by_xpath("//input[@type='radio' and @name='SearchBy' and @labelvalue='Defendant']")
            if sb.get_attribute("checked") != "true": sb.click()

            sb = self.driver.find_element_by_xpath("//input[@type='radio' and @name='PartySearchMode' and @value='Name']")
            if sb.get_attribute("checked") != "true": sb.click()

            sb = self.driver.find_element_by_xpath("//input[@type='radio' and @name='CaseStatusType' and @value='0']")
            if sb.get_attribute("checked") != "true": sb.click()

            sb = self.driver.find_element_by_xpath("//input[@type='checkbox' and @name='UseSoundex']")
            if sb.get_attribute("checked") != "true": sb.click()

            self.driver.find_element_by_xpath("//input[@type='text' and @name='LastName']").send_keys(last_name)
            self.driver.find_element_by_xpath("//input[@type='text' and @name='FirstName']").send_keys(first_name)
            self.driver.find_element_by_xpath("//input[@type='text' and @name='DateOfBirth']").send_keys(dob)

            time.sleep(self.delay)

            self.driver.find_element_by_xpath("//input[@type='submit' and @name='SearchSubmit' and @value='Search']").click()

            try:
                WebDriverWait(self.driver, 60).until(EC.text_to_be_present_in_element((By.XPATH, "//b"),'Record Count:'))
                return True
            except Exception as e:
                self.armFails.append('Unsuccessful Search Submiting')
                return False
                pass
        except NoSuchElementException:
            print('\n Cannot Reach the Search Form')
            self.armFails.append('Cannot Reach the Search Form')
            pass


    def collectCases(self,sn):
        self.noResults = False
        self.clObtain = []
        try:
            btbl = self.driver.find_elements_by_xpath("//body/table")
            rc = btbl[2].find_element_by_xpath("//tr[1]/td[2]/b").text
            if int(rc.strip()) == 0:
                self.noResults = True
            else:
                trs = btbl[3].find_elements_by_xpath('./tbody/tr')
                n=0
                rec = {}
                for tr in trs:
                    if tr.get_attribute('height') is None:
                        if n>0:
                            td = tr.find_elements_by_tag_name('td')
                            a = td[0].find_element_by_tag_name('a')
                            cn = a.text.strip()
                            if cn not in self.caseList:
                                self.caseList[cn] = {'primary':'','aliases':[],'info':{}}
                                rec['Case Number'] = cn
                                rec['href'] = a.get_attribute('href').strip()
                                rec['Citation Number'] = td[1].text.strip()
                                rec['Defendant Info'] = td[2].find_element_by_tag_name('div').text.strip()
                                self.caseList[cn]['primary'] = self.nameDivider(rec['Defendant Info'])
##                                t = self.defNPA(rec['Defendant Info'])
##                                self.caseList[cn]['primary'] = t['primary']
##                                if 'aliases' in t:
##                                    self.caseList[cn]['aliases'].append(t['aliases'])
                                div = td[3].find_elements_by_tag_name('div')
                                rec['Filed'] = div[0].text.strip()
                                rec['Location'] = div[1].text.strip()
                                div = td[4].find_elements_by_tag_name('div')
                                rec['Type'] = div[0].text.strip()
                                rec['Status'] = div[1].text.strip()
                                rec['Charge(s)'] = [el.text.strip() for el in td[5].find_elements_by_tag_name('td')]
                                self.caseList[cn]['info'].update(rec)
                                self.clObtain.append([cn,rec['href']])
                            else:
                                self.caseList[cn]['aliases'].append(self.nameDivider(sn))
                        n = n+1
            
            return True
        except Exception as e:
            self.armFails.append('The Search Does Not Returns necessary page structure')
            return False
            pass

    def defNPA(self,val):
        patrn = [" AKA ", " Aka ", " aka ", "Also Known As", "also known as", "Also known as", "Also Known as", "Now Known As", "Now known as", "Now Known as", "now known as"]
        ret = {}
        splt = ''
        for p in patrn:
            if p in val:
                splt = p
                break
        
        if splt != '':
            t = val.split(splt)
            ret['primary'] = self.nameDivider(t[0].strip())
            ret['primary']["middle"] = "" if ret['primary']["middle"].lower() == 'aka' else ret['primary']["middle"]
            if len(t)>1 and t[1].strip() != '':
                if ',' in t[1].strip():
                    ret['aliases'] = self.nameDivider(t[1].strip())
                else:
                    a = t[1].strip().split(' ')
                    ret['aliases'] = {'last':'','first':'','middle':'','suffix':''}
                    ret['aliases']['last'] = ret['primary']['last']
                    if len(a) > 1:
                        ret['aliases']['first'] = a[0]
                        ret['aliases']['middle'] = ' '.join(a[1:])
                    else:
                        ret['aliases']['first'] = a[0]
                    
        else:
            ret['primary'] = self.nameDivider(val)

        return ret


    def partyInformation(self,table):
        res = {}
        try:
            #res = self.nameDivider(table.find_element_by_id("PIr11").text.strip())
            res['Defendant'] = table.find_element_by_id("PIr11").text.strip()
        except Exception:
            res['Defendant'] = ''
            pass
        try:
            res['type'] = table.find_element_by_id("PIr01").text.strip()
        except Exception: pass
        bodinf = table.find_element_by_xpath("./tbody/tr[2]/td[2]").text.strip().split('\n')
        gs = bodinf[0].split(' ')
        try:
            res['Gender'] = gs[0].strip()
        except Exception: pass
        try:
            res['Race'] = gs[1].strip()
        except Exception: pass
        try:
            res['phisics'] = bodinf[1].strip()
        except Exception: pass
        try:
            res['Attorneys'] = table.find_element_by_xpath("./tbody/tr[2]/td[3]/s").text.strip()
        except Exception: pass
        try:
            adr = table.find_element_by_xpath("./tbody/tr[3]/td").text.strip().split('\n')
            res.update(self.adrDivider(adr[0].strip()))
        except Exception: pass
        return res

    def chargeInformation(self,table):
        res = []
        rec = {}
        trs = table.find_elements_by_xpath("./tbody/tr")
        trs = trs[1:-1]
        for tr in trs:
            td = tr.find_elements_by_tag_name('td')
            if len(td)>2:
                rec['Charge'] = td[1].text.strip()
                rec['Statute'] = td[3].text.strip()
                rec['Level'] = td[4].text.strip()
                rec['Date'] = datetime.datetime.strptime(td[5].text.strip(), '%m/%d/%Y').strftime('%Y%m%d')
                res.append(dict(rec))
        return res

    def bondsInformation(self,table):
        res = []
        trs = table.find_elements_by_xpath("./tbody/tr")
        trs = trs[1:]
        for tr in trs:
            tblwrap = tr.find_element_by_tag_name('table')
            wrp_trs = tblwrap.find_elements_by_xpath("./tbody/tr")
            wrp_trs = wrp_trs[:-1]
            t=1
            rec = {}
            for wrp_tr in wrp_trs:
                if t!=3:
                    sbtr = wrp_tr.find_element_by_xpath("./td/table/tbody/tr")
                    stds = sbtr.find_elements_by_tag_name('td')
                    if t==5:
                        rec[stds[0].text.replace(':','').strip()] = stds[1].text.strip()
                    elif t==1:
                        sttl = stds[0].text.strip()
                        stds = stds[1:]
                        rec[sttl] = " ".join([elt.text.strip() for elt in stds])
                    else:
                        rec[stds[1].text.strip()] = datetime.datetime.strptime(stds[0].text.strip(), '%m/%d/%Y').strftime('%Y%m%d')
                else:
                    std = wrp_tr.find_element_by_xpath("./td").text.strip().split(':')
                    rec[std[0].strip()] = std[1].strip()
                    
                    
                t = t+1
            
            res.append(dict(rec))
        return res

    def eventsInformation(self,table):
        res = {}
        disp = table.find_elements_by_id('CDisp')

        if len(disp)>0:
            trs = table.find_elements_by_xpath("./tbody/tr")
            cell = table.find_element_by_xpath("(./tbody//th[@id='COtherEventsAndHearings'])[last()]/parent::tr")
            ind = self.driver.execute_script('return arguments[0].rowIndex;', cell)-1
            trs = trs[1:ind]

            for tr in trs:
                dt = datetime.datetime.strptime(tr.find_element_by_xpath('./th').text.strip(), '%m/%d/%Y').strftime('%Y%m%d')
                td = tr.find_elements_by_xpath('./td')[-1]
                ttl = td.find_element_by_xpath('./div/b').text.strip()
                dr = []
                dr.append(dt)
                tbchk = td.find_elements_by_tag_name('table')
                data = [elt.strip() for elt in td.find_element_by_xpath('./div/div/div').text.strip().split('\n')]
                rec = []
                for d in data:
                    new = d.split('.')[0].strip().isdigit()
                    
                    if new and len(rec) > 0:
                        dr.append(rec)
                        rec = []
                        rec.append(d.strip())
                    else:
                        rec.append(d.strip())
                        
                dr.append(rec)
                res[ttl] = dr
                     
        return res

    def getDetails(self,cn=''):
        try:
            WebDriverWait(self.driver, 60).until(EC.text_to_be_present_in_element((By.XPATH, "//div[@class='ssCaseDetailROA']"),'Register of Actions'))

            btbl = self.driver.find_elements_by_xpath("//body/table")
            detail = {'party':{},'charge':[],'events':{},'bonds':[]}
            for table in btbl:
                caption = table.find_elements_by_xpath("./caption/div")
                if len(caption)>0:
                    ttl = caption[0].text.lower().strip()

                    if ttl == 'party information':
                        detail['party'] = self.partyInformation(table)
                        if detail['party']['Defendant'] != '':
                            t = self.defNPA(detail['party']['Defendant'])
                            self.caseList[cn]['primary'] = t['primary']
                            if 'aliases' in t: self.caseList[cn]['aliases'].append(t['aliases'])                        
                    elif ttl == 'charge information':
                        detail['charge'] = self.chargeInformation(table)
                    elif ttl == 'events & orders of the court':
                        detail['events'] = self.eventsInformation(table)
                elif len(table.find_elements_by_xpath("./tbody/tr[1]/td/b/div[contains(text(), 'Bonds')]")) > 0:
                    detail['bonds'] = self.bondsInformation(table)
            
            self.caseList[cn]['info'].update(detail)
            
            return
        except Exception as e:
            self.armFails.append('Cannot get {} case details'.format(cn))
            return
            pass

    def convertRec(self):
        self.bigDATA = []
        
        for k,v in self.caseList.items():
            
            primary = v["primary"]
            alias = v["aliases"]
            i = v["info"]
            ca = {}

            
            try: ca['City'] = self.replaceChars(i["party"]["city"])
            except Exception: pass
            try: ca['State'] = self.replaceChars(i["party"]["state"])
            except Exception: pass
            try: ca['ZipCode'] = i["party"]["zip"]
            except Exception: pass

            try: 
                ca['CaseFileDate'] = self.dateFlipper(i["Filed"])
            except Exception: pass
            
            try: ca['CaseNumber'] = self.replaceChars(i["Case Number"])
            except Exception: pass
            try: ca['CourtName'] = self.replaceChars(i["Location"])
            except Exception: pass

            try: ca['Gender'] = self.replaceChars(i["party"]["Gender"])
            except Exception: pass
            try: ca['Race'] = self.replaceChars(i["party"]["Race"])
            except Exception: pass


            ca['Names'] = []
            try:
                name = primary
                name['type'] = 'Primary'
                ca['Names'].append(dict(name))
            except Exception: pass
            try:
                for n in alias:
                    name = n
                    name['type'] = 'Alias'
                    ca['Names'].append(dict(name))
            except Exception: pass

            ca['DateOfBirth'] = '{}{}{}'.format(self.srch['date_of_birth']['Y'], self.srch['date_of_birth']['M'] ,self.srch['date_of_birth']['D'])
            ca['DateOfBirthDay'] = self.srch['date_of_birth']['D']
            ca['DateOfBirthMonth'] = self.srch['date_of_birth']['M']
            ca['DateOfBirthYear'] = self.srch['date_of_birth']['Y']

            ca['Offenses'] = []
            try:
                for x in range(len(i["charge"])):
                    o = {}
                    o['Comments'] = []
                    charge = i["charge"][x]
                    o['ChargeFileDate'] = self.dateFlipper(charge["Date"])
                    o['Severity'] = self.replaceChars(charge["Level"])
                    o['OffenseDescription'] = self.replaceChars(charge["Charge"])
                    o['Statute'] = self.replaceChars(charge["Statute"])
                    o['OffenseCode'] = '{} - {}'.format(o['Statute'], o['OffenseDescription'])
                    try:
                        if len(i["bonds"]) > 0:
                            try:
                                bond = i["bonds"][x]
                            except Exception:
                                bond = i["bonds"][0]
                            if bond["Comments"].strip() != '':
                                o['Comments'].append(self.replaceChars(bond["Comments"]))
                            o['ArrestDate'] = bond["Arrest Date"] if "Arrest Date" in  bond else ''
                    except Exception: pass
                    
                    if len(i["events"]) > 0:
                        try:
                            if "Judgment" in i["events"]:
                                o['DispositionDate'] = self.dateFlipper(i["events"]["Judgment"][0])
                                j = i["events"]["Judgment"][x+1]
                                o['Disposition'] = self.replaceChars(j[1])
                        except Exception: pass

                        
                        committed = []
                        try:
                            committed = next( b for a,b in i["events"].items() if a.startswith('Committed Directly'))
                            if len(committed) > 0:
                                xyz = self.stripSentence(committed[x+1][2])
                                o['Comments'].append(xyz)
                                o['Comments'].append(self.replaceChars(committed[x+1][2]))
                                if len(committed[x+1])>3: o['Comments'].append(committed[x+1][3])
                        except Exception: pass

                        
                                   
                    ca['Offenses'].append(dict(o))
            except Exception: pass

            self.bigDATA.append(dict(ca))

    def new_run(self):
        if self.pass_check(self.url) is True:
            try:
                self.driver = webdriver.Chrome(executable_path=self.chromedriver, options=self.chrome_options, desired_capabilities=self.chrome_capabilities)
                return True
            except SessionNotCreatedException as exception:
                self.chromeDrvUpdMess(str(exception))
                self.logger.error("Fatal error in Starting The Chrome", exc_info=True)
                self.armFails.append('Fatal error in Starting The Chrome')
        else:
            return False

    def pass_check(self,url):
        response = self.request(url)
        if response:
            if(response.status_code == 200):
                self.info('Target Response OK')
                return True
            else:
                self.error('Target HTTPError Response Code: {0}'.format(response.status_code))
                self.reportNetw('Target HTTPError Response Code: {0}'.format(response.status_code))
                print('Oops. HTTPError Response Code ',response.status_code)
                self.armFails.append('Target HTTPError Response Code: {0} for {1}'.format(response.status_code,url))
                return False
        else:
            return False
        return True

    def run_script(self):
        
        if self.new_run() is True:

            self.driver.get(self.url)

            try:
                WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "Criminal Case Records")))
                time.sleep(3)
                print('\n Requesting Search Form')
                self.driver.find_element_by_link_text('Criminal Case Records').click()
                try:
                    WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit' and @value='Search' and @name='SearchSubmit']")))
                    for lf in self.srch['last_first']:
                        if self.searchForm(lf[0], lf[1]):
                            print()
                            if self.collectCases(', '.join(lf)):
                                print(' {} Unique Case(s) Considered'.format(len(self.clObtain)))
                                if len(self.clObtain) > 0:
                                    
                                    main_window = self.driver.current_window_handle
                                    self.driver.execute_script("window.open();")
                                    self.driver.switch_to_window(self.driver.window_handles[1])
                                    for i in self.clObtain:
                                        self.driver.get(i[1])
                                        self.getDetails(i[0])
                                        time.sleep(1)
                                        
                                    self.driver.close()
                                    self.driver.switch_to_window(main_window)

                            else:
                                print(' Something went wrong with Search Results Parsing')
                                self.armFails.append('Something went wrong with Search Results Parsing')
                        else:
                            print(' Something went wrong with Searching')
                            self.armFails.append('Something went wrong with Searching')

                        self.driver.find_element_by_link_text('New Criminal Search').click()
                        
                except NoSuchElementException:
                    print('\n Cannot Reach the Search Form')
                    self.armFails.append('Cannot Reach the Search Form')
                    pass

            except NoSuchElementException:
                print('Cannot Find Requested')
                self.armFails.append('Unable to find the requested in the root of structure')
            finally:
                self.driver.quit()
                self.info('self.driver.quit()')
                print('\n\nOK')



            with open(self.xmlRep.replace('.xml','.json'), 'w') as fp: json.dump(self.caseList, fp, indent=4)

            self.report('Generatig Report')
            if len(self.caseList) > 0: self.convertRec()
            self.xBuilder()

            if len(self.armFails) > 0:
                armReporter = logging.getLogger("reporter")
                armReporter.setLevel(logging.INFO)
                fh = logging.FileHandler(self.xmlRep.replace('.xml','.log'))
                formatter = logging.Formatter('%(message)s')
                fh.setFormatter(formatter)
                armReporter.addHandler(fh)
                for m in self.armFails:
                    armReporter.info(m)

            self.info('Exit from Script')
            self.info('...................................................................')
            print('exit')
            


    def chromeDrvUpdMess(self,mess):
        t = mess.split('\n')
        t = t[0].split(':')
        text = t[2].replace(' Chrome','To use the current v{0} Driver your Windows Google Chrome Browser')
        text = text.format(self.CHROME_VERSION)+'\nOr follow to the "Help" Instruction to update Chrome Driver Version according to the Browser version'
        print(text)
        self.report(text)

    @staticmethod
    def cli_progress(i, end_val, bar_length=20):
        percent = float(i) / end_val
        hashes = '#' * int(round(percent * bar_length))
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\r Progress: [{0}] {1}% - {2} of {3}".format(hashes + spaces, int(round(percent * 100)), i, end_val))
        sys.stdout.flush()
        
    @staticmethod
    def make_dir(path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

    def nameDivider(self,name):
        nameD = {'last':'','first':'','middle':'','suffix':''}
        if name.strip() !='':
            u = [',',':',';','"']
            r = name.strip().split(',')
            t = self.nameCleaner(r[1].strip())
            
            ln = r[0].strip()
            fn = t['cnm'][0].strip()
            mn = '' if len(t['cnm']) == 1 else ' '.join(t['cnm'][1:])
            sx = t['sfx'] if 'sfx' in t else ''
            
            nameD['last'] = self.replaceChars(''.join(i for i in ln if not i in u))
            nameD['first'] = self.replaceChars(''.join(i for i in fn if not i in u))
            nameD['middle'] = self.replaceChars(''.join(i for i in mn if not i in u))
            nameD['suffix'] = self.replaceChars(''.join(i for i in sx if not i in u))
           
        return nameD
    
    @staticmethod
    def nameCleaner(n):
        r = {}
        n = n.strip()
        u = [',',':',';','"']
        s = ['jr','sr','jr.','sr.','i','ii','iii','iv','v']
        t = ''.join(i for i in n if not i in u).replace('  ',' ').split(' ')
        n = [x.strip() for x in t if x.strip()]
        if n[-1].lower() in s:
            r['sfx'] = n[-1].replace('.','')
            r['cnm'] = n[:-1]
        else:
            r['cnm'] = n
        return r

    @staticmethod
    def replaceChars(d):
        r = {'&' : '&amp;', '>' : '&gt;', '<' : '&lt;', '"' : '&quot;', "'" : '&apos;', "’" : '&apos;'}
        return str(d).translate(str.maketrans(r))

    @staticmethod
    def adrDivider(r):
        n = {'zip':'','state':'','city':''}
        if r.strip() != '' and ',' in r:
            r = r.strip().split(',')
            r = list(filter(None, r))
            t = r[1].strip().split(' ')
            n['zip'] = t[1]
            n['state'] = t[0]
            n['city'] = r[0].strip()
        return n

    @staticmethod
    def dateFlipper(d):
        try:
            return datetime.datetime.strptime(d, '%m/%d/%Y').strftime('%Y%m%d')
        except Exception as e:
            return d
            pass

    def stripSentence(self,string):
        result = ''
        r = string.lower().find('days')
        if r > -1:
            result = string[0:r+4].strip().replace(',','')
            return self.replaceChars(result)
        
        r = string.lower().find('months')
        if r > -1:
            result = string[0:r+6].strip().replace(',','')
            return self.replaceChars(result)
        
        r = string.lower().find('years')
        if r > -1:
            result = string[0:r+5].strip().replace(',','')
            return self.replaceChars(result)
        
        return result
