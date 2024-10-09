# Palm Hardiness

Palm enthusiasts the world over are sharing their observations online in forums! The information is out there but it's scattered across various forum threads and sites. A large effort has been made to collect and organize this data by [kinzyjr](https://www.palmtalk.org/forum/profile/5832-kinzyjr/ ). This goal of this app is to provide a web interface on top of that collected data set, making it more easily accessible, with links back to the source for further reading.

The hardiness data was made accessible to a wide audience by being distributed as an Excel document. For our purpose, the first step is to convert it to a Sqlite database and the second is to display it as a web app. 
https://www.palmtalk.org/forum/topic/61358-0000-cold-hardiness-observation-master-data/

> Massive thanks to [kinzyjr](https://www.palmtalk.org/forum/profile/5832-kinzyjr/ ) who collected palm 
> hardiness data spread across the PalmTalk forum and other 
> sources.
> https://www.palmtalk.org/forum/profile/5832-kinzyjr/ 


## Requirements
  * [Cold hardiness master data](https://www.palmtalk.org/forum/topic/61358-0000-cold-hardiness-observation-master-data/) Excel file. (Developed against 2024.)
  * [Python](https://www.python.org) 3 (Developed against 3.11.)
    * Ability to install python modules through `pip`

# Quick Start

Run the following commands. [Read the full setup](setup.md#setup) instructions if you want to understand what's happening.

`python -m venv venv`

macOS & Linux: `source ./venv/bin/activate`

Windows: `venv\Scripts\Activate.ps1`

```
pip install -r requirements.txt
python ./populate_database.py --excel ./202406092045_ColdHardinessMasterData.xlsx
python main.py
```
Open your browser to the web address from the terminal, probably http://localhost:5000

# Libraries

Styling is the default bulma 1.0

  * https://bulma.io/documentation/

Icons are provided by Font Awesome 6 (free)

  * https://fontawesome.com/download

Geocoding is provided by Nominatim

  * https://operations.osmfoundation.org/policies/nominatim/
