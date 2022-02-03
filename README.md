# 15-Fort-Bend

Scraping of Criminal Data on Individual/Physical Entity Level for Fort Bend County in Texas, USA.


USAGE 
-----
In Terminal, run the below line to get general help with arguments that the script intakes:

python arman_yura_run_script.py --help


Then, to execute the script for a combination of following arguments - [first name (required), last name (required), middle name (optional) and date of birth (optional)], run the below line with actual values instead of placeholders:

python arman_yura_run_script.py -fn "first name" -ln "last name" -mn "middle name" -dob "date of birth"


For no-hit entries that won't return a record associated with them, a "No cases found for that person" message will be returned and no JSON & XML reports will be produced.
For all other correct entries, a web driver will be launched, initiating the scraping procedure and ultimately creating both reports for the given individual in a separate folder.
