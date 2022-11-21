# Purpose

This script will, when given model specifications and oscar user metadata, send
a job Oscar to do the following:
* Run 3 chains of your model using parallel processing, and save each chain
* Save the gelman rubin statistics associated with the combined chains
* Plot and save the parameter posteriors associated with the combined chains
* Get and save traces associated with the combined chains
* Create and save PPC data (via a call to HDDM `post_pred_gen`), and PPC data
 compared with original data (via a call to HDDM `post_pred_stats`)


# Quickstart

0. Have the filepath of the data you want to fit, and a conda environment set up as 
desribed in the 'Requirements'.

1. In a folder on your Oscar account, download the two files `run_model_example.sh` 
and `run_model_example.py`.

2. In `run_model_example.sh`, edit the `mail-user` and `account` to point to your 
email address and your lab's Oscar condo. (The Frank lab's condo is 
`carney-frankmj-condo`.) Here is an example:
```
#SBATCH --mail-user=pranavan_chanthrakumar@brown.edu
#SBATCH --account=carney-frankmj-condo
```

3. In `run_model_example.sh`, edit the conda environment referenced to match the one 
you want to use. Here is an example where the conda environment to use is named 'pyHDDMN':
```
source activate pyHDDMN
```

4. In `run_model_example.py`, set your model details in the 'MODEL SPECIFICATIONS' 
section. Be sure your datafile exists and has the columns you specify in your
model definition. Here is an example:
```
# **** MODEL SPECIFICATION ****
# Set the following variables for your model of interest 
datafilepath = 'data_cleaned_112122.csv'	# Data that the model is fit to
model_name ='Angle_v1'						# Used in file names
model = 'angle'              				# Used in call to HDDM
nmcmc = 5000
burn_in = 3000
Group_only = False
n_samples = 1000,
p_outlier = 0.05,
model_def = [
		'v ~ 1 + sub_reward*DBSStatus + sub_averse*DBSStatus', 
        'a ~ 1 + sub_conflict*DBSStatus',
        'z ~ 1 + DBSStatus',
        't ~ 1 + DBSStatus',
        'theta ~ 1 + DBSStatus'
]

# If this is changed, be sure to change the number of 
# cores requested in the bash script that calls this file
num_chains = 3
# ****************************** 
```

4. After completing the above steps, if you run:
```
./run_model_example.sh
```
in the folder that contains this bash file, you will submit one batch job to Oscar that will 
run 3 chains of your model in parallel. Posteriors, traces, chain files, and other related 
files will be stored in the same folder that contains the bash and python files you downloaded 
in step 1. An output file called 'out_example.txt' will be created that has the output of the 
script, and a separate slurm output file is also auto-created associated with the parent 
Oscar job.

# Requirements

* Base Conda Environment for HDDMnnRegressor: As written, the bash script 
activates a conda environment on the Oscar cluster that receives your job. This 
environment needs to be set up to run HDDM and call HDDMnnRegressor, which would
include installations of pymc, patsy, jupyter, cython, kabuki, hddm, etc.

* `ipyparallel` Added to the Base Conda Environment: To run separate model
chains in parallel, the `ipyparallel` package is used. To install it on the
conda environment your Oscar jobs will run in, do the following after ssh'ing
into your Oscar account, inserting your base conda env's name:
```
$ source activate <YOUR BASE CONDA ENVIRONMENT NAME>
$ pip install ipyparallel
```
