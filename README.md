ncaa-coaching-analysis
======================
Environment:
Python 3.4

Necessary libraries:
BeautifulSoup via http://www.crummy.com/software/BeautifulSoup/#Download
mechanicalsoup via https://github.com/hickford/MechanicalSoup
xlrd via https://pypi.python.org/pypi/xlrd


DATA FLOW: acquisition -> finalData -> analysis (and database) -> visualization
ACQUISITION:
	All scripts are self-starting. Optional parameters for restarting after failure.
Output files are all labeled (numbered in order if restarted after failure). 

FINAL DATA:
	All data is processed via Excel and Google Refine. No work flow exists for recreating this portion of project. Formulas may be seen in .xlsx files.
Weighting file is decision of group members in how to score coaching success. See associated .txt file and report for notes on how scoring works.
SchoolMapping is very important and easily expanded as more schools are added later if necessary

ANALYSIS:
	use buildDataset.py to create coaching database and pickle resulting python variables of coaches and schools.
jsonGen transforms this data into usable json file for visualization. headCoaches.csv is the combined list of head coaching stops from cfbwarehouse and wikipedia. coaches.csv is list of all positions held by all coaches.
scoreCheck is temporary output of all coaching scores to ensure validity.

VISUALIZATION:
	use output json files and d3 to create interactive visualization in web browser.
	This folder is primarily for debugging/testing code

See the finalized visualization at http://paulkern.github.io/ncaa-coaching-analysis/
	Fork from the gh-pages fork to modify visualization
