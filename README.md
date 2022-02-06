# 15-Fort-Bend

Scraping of Criminal Data on Physical Entity Level for Fort Bend County in Texas, USA.


SETUP
-----

First of all, have Google Chrome web browser installed on your computer. 

The next step is to install Chromedriver and have it in the following location: "C:\Program Files (x86)" (this can also be manually modified in 'configs.py'). You will need to check the version of your Google Chrome by clicking on three dots at the top-right corner of the browser, then "Settings", and then 'About Chrome'. Thereafter, download the appropriate version of "chromedriver.exe" from here: "https://chromedriver.chromium.org/downloads" and extract in the above mentioned folder. 

Then, please install 'selenium' package in Python: to do so, run the below line. This will also be automatically initialized when the main script is called.

`pip install selenium'

Lastly, please make sure that your Internet is configured to open U.S.-based websites (e.g., via VPN) as there are accessibility restrictions in place.


USAGE 
-----

In Terminal, run the below line to get general help with arguments that the script intakes:

'python run_script.py --help'


Then, to execute the script for a combination of following arguments - [first name (required), last name (required), middle name (optional), date of birth (optional) and internal ID (optional)], run the below line with actual values instead of placeholders:

'python run_script.py -fn "first name" -ln "last name" -mn "middle name" -dob "date of birth" -id "internal ID"'


For no-hit entries that won't return a record associated with them, a "No cases found for that person" message will be returned and no JSON & XML reports will be produced.
For all other correct entries, a web driver will be launched, initiating the scraping procedure and ultimately creating both reports for the given individual in a separate folder.
