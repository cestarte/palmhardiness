# Palm Hardiness

Data posted to forums is often lost in the depths of the internet. At the very least it means hunting through thousands of pages and remembering the interesting bits. The goal here is to collect and present that info in a more readily-available manner, with links back to the source for further reading. 

The hardiness data was made accessible to a wide audience by being distributed as an Excel document. The first step is to convert it to a Sqlite database and the second is to display it as a web app. 

https://www.palmtalk.org/forum/topic/61358-0000-cold-hardiness-observation-master-data/

> Massive thanks to kinzyjr who collected palm 
> hardiness data spread across the PalmTalk forum and other 
> sources.
> https://www.palmtalk.org/forum/profile/5832-kinzyjr/ 


## Requirements
  * Cold hardiness master data Excel file. (Developed against 202312100000.)
  * Python 3 (Developed against 3.11.)

# Setup

In the below examples, the commands `python` and `pip` may be named `python3` 
or `pip3` on your system.

## Virtual Environment

Create an environment to prevent cluttering up your default install. This is only necessary once. (But it is safe to delete the venv directory and re-run the command.)

`python -m venv venv`

Now initialize the environment. Do this every time before running the app. 

### macOS and linux

`source ./venv/bin/activate`

### Windows

From a powershell terminal:

`venv\Scripts\Activate.ps1`

## Install the prerequisites

Packages required by the python app are listed in the text file.

`pip install -r requirements.txt`

## Create the sqlite database

Build the sqlite3 database tables and relationships.

`python prepare_database.py --drop`

The `--drop` argument will delete and overwrite the database tables, 
if already existing. 

## Perform the import

Populate the database from the excel file.

`python populate_database.py --excel 202312100000_ColdHardinessMasterData.xlsx`

The `--excel` argument specifies the path to the cold hardiness data set.

## Launch the web app

This launches a development Flask server, probably running at http://localhost:5000 (check your terminal.) 

`python application.py`

# Misc

Styling is the default bulma 1.0

  * https://bulma.io/documentation/

Icons are Font Awesome 6 (free)

  * https://fontawesome.com/download
