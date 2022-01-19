import os, os.path, sys, time, datetime, configparser, logging, requests, io
from .sandbox import webdriver
from zipfile import ZipFile


class Engine(object):

    def __init__(self, helper):
        current_folder_path, current_folder_name = os.path.split(os.path.abspath(__file__))
        self.path = current_folder_path + '\\'
        self.config = configparser.ConfigParser()
        self.ini = self.path+'manifest.cfg'
        self.logger = logging.getLogger("scanner.engine")
        self.drvRoot = self.path+'sandbox\\driver\\'
        self._provider_ = list(sys.argv)

        print(' Checking the system')

        if not os.path.isfile(self.ini):
            self.info('There is missing the system configuration')
            self.blankConfig()
            
        self.info('"System Health Check" passed')

    def debug(self, mess):
        pass

    def warning(self, mess):
        self.logger.warning(mess)
    
    def info(self, mess):
        self.logger.info(mess)

    def error(self, mess):
        self.logger.error(mess)

    def blankConfig(self):
        self.info('Calling the "Initial Configuration"')
        cnf = {}
        cnf['silent'] = True
        
        print('','>> Initial Configuration >>','',sep='\r\n')
        
        cnf['chrome version'] = self.cnf_chrome_driver()
        cnf['report directory'] = self.cnf_report_directory()
        cnf['human delay'] = self.cnf_delay()
        self.config['DEFAULT'] = cnf
        
        try:
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)
            self.info('Configuration saved')
        except Exception:
            self.logger.error("Fatal error in Configuration saving", exc_info=True)

    def update(self):
        self.info('Calling the "Configuration Update"')
        flds = ['chrome version', 'report directory', 'human delay', 'exit']
        print('',
              '>> Update Configuration >>',
              '',
              'Choose the Field to update',
              'Available Fileds (lower case):',
              'chrome version, report directory, human delay',
              '',
              'To Exit from this menu type "exit"',
              sep='\r\n')
        
        chrV = input("Which Configuration? : ")
        curr = self.cnf_get()

        if chrV in flds:
            if chrV != 'exit':
                print('','Current Value is [ {0} ]'.format(curr.get(chrV.replace(' ','_'))),'',sep='\r\n')
                if chrV == 'chrome version':
                    
                    nv = self.cnf_chrome_driver()
                    self.config.set('DEFAULT', 'chrome version', nv)

                if chrV == 'report directory':
                    
                    nv = self.cnf_report_directory()
                    self.config.set('DEFAULT', 'report directory', nv)

                if chrV == 'human delay':
                    
                    nv = self.cnf_delay()
                    self.config.set('DEFAULT', 'human delay', nv)

                try:
                    with open(self.ini, 'w') as configfile:
                        self.config.write(configfile)
                    self.info('Configuration updated')
                except Exception:
                    self.logger.error("Fatal error in Configuration saving", exc_info=True)

                if chrV == 'chrome version':
                    isOk = self.checkChrome()
                    if isOk:
                        self.update()
                    else:
                        pass
                else:
                    self.update()
                
            else:
                self.info('Exit the "Configuration Update"')
                pass
        else:
            self.warning('"Configuration Update" requested [ '+chrV+' ] unknown field')
            print('',chrV+' is unknown field','',sep='\r\n')
            self.update()

    def cnf_get(self):
        self.config.read(self.ini)
        report_directory = self.config.get('DEFAULT', 'report directory')
        silent = self.config.getboolean('DEFAULT', 'silent')
        chrome_version = self.config.getint('DEFAULT', 'chrome version')
        delay = self.config.getint('DEFAULT', 'human delay')
        return {'report_directory':report_directory,'silent':silent,'chrome_version':chrome_version,'delay':delay}


    def cnf_chrome_driver(self):
        print('',
              '   1. Chrome Browser Version:',
              '      1.1 Open the Chrome Browser;',
              '      1.2 Go to "Help" > "About Google Chrome";',
              '      1.3 From the Version we need only First Value;',
              '          For Example 78 from "Version 78.0.3904.108 (Official Build) (64-bit)"',
              '      1.4 Enter the Number in requested field.',
              '',
              sep='\r\n')
        
        chrV = input("Chrome Version: ")
        print()
        chk = input("Use the "+chrV+" version? [y/n]: ")
        if chk.lower() == 'y':
            print()
            print('Using the '+chrV+' Version')
            self.info('"Chrome Version" setted to : '+chrV)
            return chrV
        else:
            self.cnf_chrome_driver()

    def cnf_report_directory(self):
        print('',
              "   2. Generated Report's Folder Path and Name (Case Sensitive):",
              '      For Example "C:\My Folder\Generated Reports"',
              '',
              sep='\r\n')
        
        chrV = input("Folder Path and Name: ")
        print()
        chk = input('Use this "'+chrV+'" ? [y/n]: ')
        if chk.lower() == 'y':
            print()
            print('Using "'+chrV+'"')
            self.info('"Folder Path and Name" setted to : "'+chrV+'"')
            return chrV
        else:
            self.cnf_report_directory()

    def cnf_delay(self):
        print('',
              "   3. Artificial Delay in Script Execution (seconds):",
              '      To avoid the possible blocking from the domain.',
              '      The bigger value will slower the script execution',
              '      the lower value increase the possibility to recognize the scraper',
              '',
              sep='\r\n')
        
        chrV = input("Human Like Delay: ")
        print()
        chk = input('Use the "'+chrV+'" seconds for delay ? [y/n]: ')
        if chk.lower() == 'y':
            print()
            print('Using "'+chrV+'"')
            self.info('The Delay setted to : '+chrV)
            return chrV
        else:
            self.cnf_delay()

    def checkChrome(self):
        curr = self.cnf_get()
        file = self.path+'sandbox\\driver\\v{0}\\chromedriver.exe'.format(curr.get('chrome_version'))
        #print(file)
        if not os.path.isfile(file):
            print('',
              "   !!!!!!!!!! CHROME DRIVER VERSION ERROR !!!!!!!!!!!",
              '',
              '   You are trying to use the Chrome Driver " {0} " Version '.format(curr.get('chrome_version')),
              '   which is absent in the program drivers directory.',
              '',
              '   To use this version you have to open the',
              '   WebDriver for Chrome site by this link "https://chromedriver.chromium.org/downloads"',
              "   download the preffered version's windows driver,",
              '   next unzip the driver with "chromedriver.exe" name to the following directory:',    
              '',
              '   "path_to_program_folder\lib\sandbox\driver\\v{0}\"'.format(curr.get('chrome_version')),    
              '',
              '   OR change the driver version from Menu',
              '   ::  " -cnf" - Change the Program Configuration:',
              '',
              '                 - Chrome Browser Driver Version',
              '',
              sep='\r\n')
            mess = 'CHROME DRIVER VERSION {0} not found in drivers'.format(curr.get('chrome_version'))
            self.error(mess)
            self.cnf_chrome_driver()
            return False
        else:
            return True

    @staticmethod
    def makeDir(path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
    


