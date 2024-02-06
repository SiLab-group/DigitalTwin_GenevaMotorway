# Digital Twin - Geneva Motorway (DT-GM) in SUMO
This git repository is linked to the research papers entitled "_Building a Motorway Digital Twin in SUMO: Real-Time Simulation of Continuous Data Stream from Traffic Counters_", and "_A digital twin in transportation: Real-time synergy of traffic data streams and simulation for virtualizing motorway dynamics_"


This repository includes all the files required to run the simulations used to produce the results presented in the papers:

## (SCENARIO-I) Example of real-time simulation of actual traffic flow data (with minute resolution) obtained directly from Geneva motorway via ODPMS:
Notes: one needs to register at **Open data platform mobility Switzerland (ODPMS)** https://opentransportdata.swiss/en/ to get access to actual traffic data from traffic counters. Also, calculations in code are dependent on the step_length parameter, so it needs to be coupled with the parameter step length in .sumocfg to have everything working properly. Use the values for step length recommended at (https://sumo.dlr.de/userdoc/Car-Following-Models/EIDM.html). As well as, so far the EIDM model was not tested with option --step-method.ballistic.  
* SUMO Geneva motorway network model and scenario files,
* instructions to register on the ODPMS platform and get access to actual traffic data,
* instructions to setup SQL database on a local computer,
* python code for: 
(I) runtime access to Federal Roads Office (FEDRO) server via ODPMS (collecting actual data and storing it in real-time in a local SQL database),<br/> 
(II) runtime traffic demand generation and online simulation calibration using SUMO's calibrators and actual traffic data as inputs to the running simulation scenario (ODPMS <-> SQL <-> python <-> TraCI <-> SUMO),<br/>
(III) the output excel files with results (comparison between actual traffic flows from Geneva motorway and the runtime simulated traffic flows by Digital Twin).


## (SCENARIO-II) Example of dynamic flow generation in SUMO using external traffic flow data inputs with minute resolution:
Note: one **can change** the provided real **workday** traffic volume in **workday_traffic.xlsx** to see the effect of dynamic volume generation by SUMO's calibrator objects and foundation of DT-GM framework. Unrealistic traffic volume may cause instability in numerical computation in the flow model used by DFC mechanism
* SUMO Geneva motorway network model and scenario files,
* workday dataset (real traffic data with minute resolution),
* python code for:
(I) simulation of runtime demand generation (calibration) using external inputs traffic data,<br/>
(II) the output files of results (comparison of real traffic and the runtime simulated traffic).


Please use the following citation when referencing our work. Merci!
>@article{KUSIC2023101858,
> author = {Krešimir Kušić and René Schumann and Edouard Ivanjko},
> title = {A digital twin in transportation: Real-time synergy of traffic data streams and simulation for virtualizing motorway dynamics},
> journal = {Advanced Engineering Informatics},
> volume = {55},
> year  = {2023},
> doi = {https://doi.org/10.1016/j.aei.2022.101858}
>}

>@inproceedings{Kusic2022_DT_GM_ELMAR,
>  author={Kušić, Krešimir and Schumann, René and Ivanjko, Edouard},
>  booktitle={Proc. of 64th International Symposium ELMAR},
>  title={{Building a Motorway Digital Twin in SUMO: Real-Time Simulation of Continuous Data Stream from Traffic Counters}},
>  year={2022}
>}


# How To setup entire framework (SUMO-Python-SQL-ODPMS)
Note: current DT-GM framework uses SQL between ODPMS (traffic counters) and SUMO to permanently store actual traffic data received from traffic counters since we use data in the latter analysis
     

## Python setup:
(I) Install Python (we tested DT-GM in version 3.9.13)<br/>
(II) Open cmd and navigate to the directory where you want to create Python virtual environment (can be a path to our folder you downloaded) and run commands (copy) in cmd to create Python virtual environment using terminal command (Note: if you have multiple pythons installed specify a version):<br/>

create virtual environment
```
python -m venv venvDTGM
```
activate virtual environment
```
venvDTGM\Scripts\activate
```
update pip
```
python -m pip install --upgrade pip
```
install necessary libraries from **requirements.txt** file
```
pip install -r requirements.txt 
```
## SUMO setup:
Instal SUMO (we tested DT_GM in version Latest Development Version May 30 2022 23:15:46 UTC), **however, we highly recommend using the latest release of SUMO**

## SQL setup (only for SCENARIO-I):
(I) Install Microsoft SQL (we tested DT-GM in version: SQL Server 2019 Express and SQL Server Management Studio (SSMS) 18.11.1)<br/>
(II) run query below in SQL:<br/>
Execute:
```
Create Database SWISS_traffic_data
```
Then this
```
Use [SWISS_traffic_data]
Go
```
Then create table by executing this block  
```
Create Table tblDetectors
(
ID int NOT NULL IDENTITY(1,1),
DetectorID nvarchar(50) NULL,
TimeStampUTC DATETIME NULL,
CarFlow int NULL,
CarSpeed float NULL,
TruckFlow int NULL,
TruckSpeed float NULL,
UnknownClassFlow int NULL,
UnknownClassSpeed float NULL,
)
```

# Run Scenarios

##  Only for (SCENARIO-I) start real-time data collecting from traffic counters and storing it in SQL
Note: register at ODPMS https://opentransportdata.swiss/en/
and insert the token you were provided by ODPMS in the python script **ODPMS_traffic_counters_request_live.py** (see comments in the script).<br/> 
Run the **ODPMS_traffic_counters_request_live.py** using terminal command:<br/>
activate virtual environemt
```
C:\Users\kkusic\Desktop\DT-GM>venvDTGM\Scripts\activate
```
navigate to folder SCENARIO-I
```
(venvDTGM) C:\Users\kkusic\Desktop\DT-GM>cd SCENARIO-I
```
run code for real-time traffic data collection
```
(venvDTGM) C:\Users\kkusic\Desktop\DT-GM\SCENARIO-I>python ODPMS_traffic_counters_request_live.py
```
##  For (SCENARIO-I): run live simulation  (**actual traffic from motorway traffic counters - ODPMS**) <-> SQL <-> Python <-> TraCI <-> SUMO
Run python script <DT_GM_live24h.py> using terminal command:<br/>
activate virtual environment
```
C:\Users\kkusic\Desktop\DT-GM>venvDTGM\Scripts\activate
```
navigate to folder SCENARIO-I
```
(venvDTGM) C:\Users\kkusic\Desktop\DT-GM>cd SCENARIO-I
```
run On-The-Fly synchronized Digital Twin Simulation of Geneva motorway (DT-GM) (SCENARIO-II)
```
(venvDTGM) C:\Users\kkusic\Desktop\DT-GM\SCENARIO-I>python DT_GM_live24h.py
```

#  For (SCENARIO-II): run small example of dynamic flow generation by sampling external flow inputs (one workday traffic dataset from input_flow.xlsx) into the running simulation
activate virtual environment
```
C:\Users\kkusic\Desktop\DT-GM>venvDTGM\Scripts\activate
```
navigate to folder SCENARIO-II
```
(venvDTGM) C:\Users\kkusic\Desktop\DT-GM>cd SCENARIO-II
```
run dynamic flow simulation script:
```
(venvDTGM) C:\Users\kkusic\Desktop\DT-GM\SCENARIO-II>python DT_GM_workday_dynamic_flow.py
```

## Users
* Master-Thesis, author Paulo Ribeiro, GitHub nickname is "paulinho-16", Master in Informatics and Computing Engineering at FEUP (Faculty of Engineering of the University of Porto)

If you use DT-GM or its tools to create a new one, we would be glad to add you to the list.
You can send an email with your name and affiliation to kresimir.kusic@unizg.fpz.hr

As well, feel free to contact us if you experience any problems, so we can improve or add additional comments to make DT-GM easier to use.
