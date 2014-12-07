ncaa-coaching-analysis
======================
DATA FLOW: acquisition -> finalData -> analysis (and database) -> visualization
ACQUISITION:
	All scripts are self-starting. Optional parameters for restarting after failure.
Output files are all labeled (numbered in order if restarted after failure). 

FINAL DATA:
	All data is processed via Excel and Google Refine. No work flow for this portion of project. Formulas may be seen in .xlsx files.
Weighting file is decision of group members in how to score coaching success. See associated .txt file and report for notes on how scoring works.

ANALYSIS:
	use buildDataset.py to create coaching database and pickle resulting python variables of coaches and schools.
jsonGen transforms this data into usable json file for visualization. headCoaches.csv is the combined list of head coaching stops from cfbwarehouse and wikipedia. coaches.csv is list of all positions held by all coaches.
scoreCheck is temporary output of all coaching scores to ensure validity.

VISUALIZATION:
	use output json files and d3 to create interactive visualization in web browser.