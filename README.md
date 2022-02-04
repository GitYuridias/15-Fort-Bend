# 15-Fort-Bend

Scraping of Criminal Data on Physical Entity Level for Fort Bend County in Texas, USA.


USAGE 
-----

First step is to install 'selenium' package in Python: to do so, run the below line. This will also be automatically initialized when the main script is called.

`pip install selenium'

In Terminal, run the below line to get general help with arguments that the script intakes:

'python run_script.py --help'


Then, to execute the script for a combination of following arguments - [first name (required), last name (required), middle name (optional), date of birth (optional) and internal ID (optional)], run the below line with actual values instead of placeholders:

'python run_script.py -fn "first name" -ln "last name" -mn "middle name" -dob "date of birth" -id "internal ID"'


For no-hit entries that won't return a record associated with them, a "No cases found for that person" message will be returned and no JSON & XML reports will be produced.
For all other correct entries, a web driver will be launched, initiating the scraping procedure and ultimately creating both reports for the given individual in a separate folder.
