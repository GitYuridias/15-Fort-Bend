from sys import platform

DESTINATION_URL = "http://tylerpaw.co.fort-bend.tx.us/PublicAccess/default.aspx"

if platform == "linux" or platform == "linux2":
    CHROME_DRIVER_PATH = "/opt/chromedriver.exe"
elif platform == "darwin":
    CHROME_DRIVER_PATH = "/Applications/chromedriver.exe"
elif platform == "win32":
    CHROME_DRIVER_PATH = "C:\Program Files (x86)\chromedriver.exe"
