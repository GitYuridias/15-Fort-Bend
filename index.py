try:
    import os, os.path, sys, time, datetime, csv, configparser, logging
except ImportError as exc:
    print(exc)
    raise
from lib import Engine
from lib import Runner

logger = None


def initialize():
    global logger
    """
    The main entry point of the application
    """
    current_folder_path, current_folder_name = os.path.split(os.path.abspath(__file__))
    logFld = current_folder_path+'\\logs'
    if not os.path.exists(logFld): os.makedirs(logFld)
    logger = logging.getLogger("scanner")
    logger.setLevel(logging.DEBUG)
    lgFile = "{0}\\{1}.log".format(logFld,datetime.datetime.now().strftime("%Y_%m_%d"))
    fh = logging.FileHandler(lgFile)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info("========================================================================")
    logger.info("Script called")


class Provider(object):

    def __init__(self, args, logger):
        
        self.engine = Engine(self)

        if self.engine.checkChrome():
            if '-?' in args:
                logger.info('"Help" menu called')
                self.help()
            elif '-cnf' in args:
                logger.info('"Configuration Update" menu called')
                self.engine.update()
            else:
                if len(args) < 4:
                    print('Error - the following arguments are required: File Name, Date of Birth (YYYYMMDD), Last Name, First Name, Alias Last, Alias First (optional)')
                else:
                    __runner__ = Runner(self.engine,args)
                    __runner__.run_script()
        else:
            pass

    @staticmethod
    def help():
        print('',
              '======= HELP =======',
              '',
              '',
              ' >> Run the Program First Time >>',
              '',
              'you will pass throw the configuration process',
              'by defining the Chrome Browser Version',
              '',
              '',
              ' >> Accepted Argument to Run the Program >>',
              '',
              ' ::  " -?" - Calling the "Help" Section',
              '',
              ' ::  " -cnf" - Change the Program Configuration:',
              '',
              '                       - Chrome Browser Driver Version',
              '                       - Report Folder Path and Name',
              '                       - Human Like Delay',
              '',
              '====================',
              '',
              sep='\r\n')

    def run(self):
        
        pass


if __name__ == '__main__':
    initialize()
    #a = ' '.join(sys.argv[1:]).split()
    a = sys.argv[1:]
    logger.info("with argument [ "+ ''.join(a)+" ]")
    __provider__ = Provider(a, logger)
