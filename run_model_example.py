# Imports
import pandas as pd
import numpy as np
import pickle
import sys
import kabuki
import seaborn as sns
import pymc
import IPython
import subprocess
import csv
import pymc.progressbar as pbar
import matplotlib
import matplotlib.pyplot as plt
import hddm
import ipyparallel as ipp
matplotlib.use('Agg')

from kabuki.analyze import gelman_rubin
from scipy import stats
from patsy import dmatrix
from pandas import Series
from hddm.simulators.hddm_dataset_generators import simulator_h_c
from statsmodels.distributions.empirical_distribution import ECDF

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
pd.options.display.max_columns = None


# **** MODEL SPECIFICATION ****
datafilepath = 'example.csv' # Data that the model is fit to
model_name = 'exampleModel'  # Used in file names
model = 'angle'              # Used in call to HDDM

# Set the following variables for your model of interest 
nmcmc = 0
burn_in = 0
Group_only = False
n_samples = 0,
p_outlier = 0.05,
model_def = [
        'v ~ 1 + C(condition)',
        'a ~ 1 + C(condition)'
]

# If this is changed, be sure to change the number of 
# cores requested in the bash script that calls this file
num_chains = 3
# ******************************

## This function will run a single chain of the model using the 
## specifications above fit to the data loaded from datafilepath,
## and save that chain.
def run_model_chain(i):
    import hddm
    data = hddm.load_csv(datafilepath)
    m = hddm.HDDMnnRegressor(
        data,
        model_def,
        p_outlier=p_outlier,
        group_only_regressors = Group_only,
        include = hddm.model_config.model_config[model]['hddm_include'],
        model=model,
        informative=False
    )
    m.find_starting_values()
    m.sample(
        nmcmc,
        burn=burn_in,
        dbname=model_name + '_Chain_' + str(i) + '_traces.db', db='pickle'
    )
    m.save(model_name + '_Chain_' + str(i))
    print('\nSaved ' + model_name + '_Chain_' + str(i) + '...')


## Data that must be sent to each parallel process
model_info = dict(
    datafilepath=datafilepath,
    model_name=model_name,
    nmcmc=nmcmc,
    burn_in=burn_in,
    model=model,
    Group_only=Group_only,
    n_samples=n_samples,
    p_outlier=p_outlier,
    model_def=model_def
)

## Make sure that the number of chains is equal to the number of 
## CPU's that you have specified in your Bash script, otherwise
## you may have slowdowns
print("\nStarting ipyparallel engines...")

with ipp.Cluster(n=num_chains).start_and_connect_sync() as client:
        engines = client[:]
        engines.push(model_info)        
        async_results = engines.map_async(run_model_chain, range(num_chains))
        engines.wait([async_results]) # Wait until your chains are done
        print("\n\nSTART of Parallel Engine Outputs:\n")
        async_results.display_outputs(groupby='engine')
        print("\nEND of Parallel Engine Outputs\n\n")

        # Uncomment the following if you want to see the 
        # speedup from parallelization
        #wall_time = async_results.wall_time
        #serial_time = async_results.serial_time
        #speedup = serial_time / wall_time
        #n_engines = len(set(async_results.engine_id))
        #efficiency = speedup / n_engines
        #print(f"Wall time  : {wall_time:6.1f}s")
        #print(f"Serial time: {serial_time:6.1f}s")
        #print(f"Speedup    : {speedup:6.1f}x / {n_engines}")
        #print(f"Efficiency : {efficiency:7.1%}")

print("Parallel computation done.\n")

## Load the models that were saved
models = []
for chain in range(0, num_chains):
    model = hddm.load(model_name + '_Chain_' + str(chain))
    models.append(model)

## Get and save Gelman-Rubin Statistics
gelman = gelman_rubin(models)
models_comb = kabuki.utils.concat_models(models)
dfGR=pd.DataFrame.from_dict(gelman, orient='index', columns=['Gelman_Rubin_Statistics'])
dfGR.to_csv(model_name + '_Gelman_Rubin.csv')  

## Save Posterior Plots
models_comb.plot_posteriors(save=True, path=model_name)

## Save traces and model statistics
model_traces = models_comb.get_traces()
model_traces.to_csv(model_name + '_traces.csv')
models_comb.print_stats(fname=model_name + '_stats.csv')

## Create and save PPC data and PPC-comparison data
ppc_data = hddm.utils.post_pred_gen(models_comb, append_data=True, samples=500)
ppc_data_sub = ppc_data
ppc_data = ppc_data.reset_index(drop=True)
ppc_data.to_csv('ppc_' + model_name + '.csv')
data = hddm.load_csv(datafilepath)
ppc_compare = hddm.utils.post_pred_stats(data, ppc_data_sub)
ppc_compare.to_csv('ppc_results_' + model_name + '.csv')
