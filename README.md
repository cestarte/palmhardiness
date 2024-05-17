# PalmTalk Hardiness Sqlite Importer

> Massive thanks to kinzyjr who painstakingly collected palm 
> hardiness data spread across the PalmTalk forum and other 
> sources.
> https://www.palmtalk.org/forum/profile/5832-kinzyjr/ 

The hardiness data was made accessible to a wide audience by
being distributed as an Excel document. This tool imports 
that data from Excel into a Sqlite database. From there it
can be queried using familiar syntax and used in an app.

## Requirements
  * Cold hardiness master data from kinzyjr on PalmTalk.org
    * The version used to develop this app 202211271020
  * Python3

## Steps

In the below examples, the commands `python` and `pip` may be named `python3` 
or `pip3` on your system.

### Virtual Environment

Create the environment.

`python -m venv venv`

Initialize the environment. 

**macOS**

`source venv/bin/activate`

**win**

`venv\Scripts\Activate.ps1`

### Install the prerequisites

`pip install -r requirements.txt`

### Create the database

`python prepare_database.py --drop`

The `--drop` argument will delete and overwrite the database tables, 
if already existing. 

### Perform the imports

`python populate_database.py --excel 202312100000_ColdHardinessMasterData.xlsx`

The `--excel` argumnent is where you specify the path to the 
cold hardiness data set.
