# 1. Overview for the China RE Pathways Project
This repository contains the renewable capacity expansion model for China's power sector for the study **"Reaching Carbon Neutrality in China: Temporal and Subnational Limitations of Renewable Energy Scale-Up"**. The model is written using [Python](https://www.python.org/).

You can use the model for conducting both single-year snapshot analysis and multi-year pathway study. In the multi-year scenario, if the outputs from the last period are missing, the model will use the existing default inputs as the intial conditions.

Contact Zhenhua (`zhenhua at ucsd dot edu`) if you run into any issues.



# 2. System requirements
## 2.1 Operating system
The code should work well on a "normal" desktop computer or laptop with either Windows or Mac OS operating system. To ensure eifficient I/O operations, we recommend that you have at least 1 GB of available hard disk space, a 4 GB or higher RAM, and an Intel Core i3 or equivalent AMD processor.

## 2.2 Software dependencies
The required Python packages including version numbers are listed below:
- Python=3.9
- pandas=1.5.3
- numpy=1.23.5
- gurobipy=10.0.2
- scipy=1.10.1
- geopandas=0.12.3
- geoplot=0.4.3
- mapclassify=2.5.0
- matplotlib=3.7.1
- shapely=2.0.1
- plotly=5.14.0

## 2.3 Gurobi license
Make sure that you have a valid Gurobi license for using the Gurobi optimization package. You should be able to obtain free academic licenses on their [website](https://www.gurobi.com/academia/academic-program-and-licenses/). By default, the Barrier method is used as the LP solution algorithm. 



# 3. Installation guide
The installation consists of two parts: (1) pull from the GitHub repository, and (2) download additional data inputs from the Zenodo directory.

## 3.1 Pull from the Github repository
https://github.com/Power-Lab/AdvAppliedEnergy_Pathways_2025 -- this repository includes hte main optimization model, small data inputs, results, visualization/analysis scripts, and the generated plots. Additionally, we also include the shell scripts for running the model on a cloud computing system.

The size of the GitHub repository is around 100 MB, so it should only take a few minutes to install with a "normal" internect connection.

## 3.2 Add additional data inputs from Zenodo
Large data files in the `data_pkl`, `data_shp`, and `data_mat` folders are not stored on Github due to the file size limit. Instead, these files are stored on the project Zenodo directory. Before running the code, you will have to copy the files in the shared folder to the corresponding locations, by taking the following two steps:

1. Download the `data_pkl`, `data_shp`, and `data_mat` folders in `AdvAppliedEnergy_Pathways_2025` from Zenodo (https://doi.org/10.5281/zenodo.14907700)
2. Move the `data_pkl`, `data_shp`, and `data_mat` folders to the `AdvAppliedEnergy_Pathways_2025` directory
3. Create a `data_res` folder in the `AdvAppliedEnergy_Pathways_2025` directory as a placeholder for outputs

The size of the additional data inputs is aorund 7 GB.

> [!CAUTION]
> Before you proceed, double check that `data_pkl`, `data_shp`, `data_mat`, and `data_res` folders exist in the `AdvAppliedEnergy_Pathways_2025` directory.



# 4. Demo
## 4.1 Run on a small dataset
Two scripts are provided for running single-year and multi-year optimization tasks:
- `testMultiYear`: generate and initialize the necessary files, and optimize for multiple years, where outputs from the last year will be used as inputs for the current year. If the outputs from last year are not available, default files will be used instead.  
- `testSingleYear`: generate and initialize the necessary files, and optimize for a single year.

In the paper, the modeled output is obtained using a full year of data (i.e., 8760 hours). For demo purposes, we can run the model on only 1 week of data (i.e., 168 hours) for each decade from 2030 to 2060. To do so, open the Terminal on your desktop computer and enter the following command lines:

```
$ cd <path_to_AdvAppliedEnergy_Pathways_2025>
$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py
```

## 4.2 Expected output from the test run
The test results will be saved to the `AdvAppliedEnergy_Pathways_2025/data_res/test_<date>_7days_all_years_pc_w2015_s2015` folder, including the capacity expansion decisions and operational results for each decade. For sanity check, you can examine the `stat_national.csv` file, which is a summary of all the modeled output.
- Onshore wind capacity: `Line 19`, should be 610, 1257, 1610, and 2369 GW for each decade.
- Utility solar capacity: `Line 21`, should be 234, 250, 389, and 723 GW for each decade.
- New transmission capacity: `Line 29`, should be 27, 93, 67, and 151 GW for each decade.


## 4.3 Expected run time
With 10 physical cores and 500 MB of memory, the test run should take around 30 minutes to complete.



# 5. Instruction for use
## 5.1 Run the model locally on your desktop computer
At the beginning of `testMultiYear` and `testSingleYear` (i.e., Step 0), you can set the simulation parameters that determine the scenarios. The updated parameters will be used to overwrite the default simulation template. Then, run the scripts in [PyCharm](https://www.jetbrains.com/pycharm/?var=1). Preliminary and processed outputs will be saved in the `outputs` and `outputs_processed` folder, respectively.

With 32 Intel Xeon processors and 256 GB of memory, each full-year simulation takes up to 20 hours to complete.

> [!NOTE]
> The current supported parameters are as below:
> - `optimization_days`: optimization days, which can be 5, 10, ..., 365
> - `start_year`: start year for the multi-year simulation, which can be 2030, 2040, 2050, or 2060
> - `year_count`: total number of years for simulation, which can be 1, 2, 3, or 4
> - `node`: running node, added as a name tag
> - `emission_target`: carbon emission target for the power sector, which can be "2C" or "15C"
> - `ccs_start_year`: CCS retrofit start year, which can be 2040, 2050, 2060, or 2070
> - `heating_electrification`: district heating mode, which can be "chp_ccs" or "heat_pump"
> - `renewable_cost_decline`: renewable cost decline trajectory, which can be "baseline" or "conservative"
> - `endogenize_firm_capacity`: indicate if the firm resource capacity is endogenized (1 if so, otherwise 0)
> - `demand_sensitivity`: demand sensitivity, which can be "none", "p5", or "m5". "p5" means plus 5%, and "m5" means minus 5%
> - `custom_tag`: customized name tag

## 5.2 Run the model on a cloud computing system
As the multi-year analysis takes up too much computational power away, it is preferred to run the model remotely at the cluster. To do so, some shell scripts are provided. In the shell script, you will have to specify the key scenario parameters (e.g., high or low renewable capex, high or low CCS retrofit cost, CCS availability year, etc.)

After you log into the cluster, you can submit the shell script and wait for it to finish. You will get an email notification when the job is finished. Lastly, you can use [FileZilla](FileZilla) to transfer the outputs back to your laptop for further analysis.

## 5.3 Reproduction instructions
To reproduce all the quantitative results in the manuscript, take the following steps (assume that the model runs remotely on a cloud computing system):
1. 2C scenario
	- 2C baseline: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b1_low 2C 2040 chp_ccs baseline 1 none 3500`
2. 1.5C scenario
	- 1.5C baseline: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b2_low 15C 2040 chp_ccs baseline 1 none 3500`
3. CCS scenario
	- 2C with no CCS: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b3 2C 2070 chp_ccs baseline 1 none 3500`
4. Heat pump scenario
	- 2C with heat pumps: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b4 2C 2040 heat_pump baseline 1 none 3500`
5. Sensitivity analysis
	- 2C with very high CCS capex: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b1_very_high 2C 2040 chp_ccs baseline 1 none 10000`
	- 2C with high CCS capex: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b1_high 2C 2040 chp_ccs baseline 1 none 6000`
	- 1.5C with very high CCS capex: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b2_very_high 15C 2040 chp_ccs baseline 1 none 10000`
	- 1.5C with high CCS capex: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b2_high 15C 2040 chp_ccs baseline 1 none 6000`
	- 2C with conservative renewable cost: `$ python AdvAppliedEnergy_Pathways_2025s/pycode/testMultiYear.py 365 2030 4 b1_c 2C 2040 chp_ccs conservative 1 none 3500`
	- 1.5C with conservative renewable cost: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b2_c 15C 2040 chp_ccs conservative 1 none 3500`
	- 2C with high demand: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b1_p 2C 2040 chp_ccs baseline 1 p5 3500`
	- 2C with low demand: `$ python AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py 365 2030 4 b1_m 2C 2040 chp_ccs baseline 1 m5 3500`



# 6. Software structure
This section lists the folder structure under the `AdvAppliedEnergy_Pathways_2025` directory:
> [!NOTE]
> - `pycode`: contains all the Python scripts
> 	- `callUtility.py`: data processing
> 	- `clearupData.py`: data cleaning
> 	- `initData.py`: initialization script that ensures the input data have the right format
> 	- `main.py`: the main optimization model
> 	- `multiYearAutomation.py`: simulation script that generates multi-year inputs
> 	- `obtainPrice.py`: obtain electricity prices based on modeled output
> 	- `plotResult.py`: data visualization
> 	- `testMultiYear.py`: test script for running multi-year analysis
> 	- `testSingleYear.py`: test script for running single-year analysis
> - `data_csv`: contains all the input files in CSV format
> 	- `capacity_assumptions`: lower/upper capacity bounds for all the non-renewable generators (i.e., BECCS, coal CHP CCS, coal, gas, hydro, nuclear, pumped-hydro storage) obtained from policy documents, power sector emission limits under the 2C and 1.5C targets, and raw unit-level coal and gas plant data from GEM
> 	- `cost_assumptions`: transmission line capex by voltage level, and thermal, renewable, and storage cost parameters
> 	- `demand_assumptions`: projected hourly electricity demand data at the provincial level in 2030/2060, and monthly average temperature data in northern China in winter months
> 	- `geography`: demographic/geographic data by province
> 	- `scen_params_template.json`: default simulation parameter template
> 	- `simulation_meta`: meta data including simulation hours and winter hours
> 	- `transmission_assumptions`: inter-provincial transmission capacity and voltage levels
> 	- `vre_installations`: existing cell-level and provincial-level wind/solar capacity data
> 	- `vre_potentials`: cell-level wind/solar maximum capacity data
> - `data_pkl`: all the input filesin PICKLE format, including wind and solar cell-level resource assessment results
> - `data_shp`: all the geospatial data used for plotting
> - `data_mat`: all the matlab matrix files
> - `data_res`: result folder, including copied inputs, single-year outputs, and multi-year summary
> - `figures_for_papers`: contains simplied model output, visualization scripts, and all the generated figures in the paper
> - `README.md`
