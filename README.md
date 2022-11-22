## Purpose

This script will send a job Oscar to run 3 chains of your model using 
parallel processing, which should lead to a speedup proportional to the 
number of chains you are running. Namely, if running 3 chains sequentially 
takes 3 hours, running this script instead will take 1 hour.

Additionally, this script does the following:
* Save the gelman rubin statistics associated with the combined chains
* Plot and save the parameter posteriors associated with the combined chains
* Get and save traces associated with the combined chains
* Create and save PPC data (via a call to HDDM `post_pred_gen`)
* Create and save PPC data compared with original data (via a call to 
HDDM `post_pred_stats`)


## Requirements

* **Base Conda Environment for HDDMnnRegressor:** As written, the bash script 
activates a conda environment on the Oscar cluster that receives your job. This 
environment needs to be set up to run HDDM and call HDDMnnRegressor, which would
include installations of pymc, patsy, jupyter, cython, kabuki, hddm, etc.

* **`ipyparallel` Added to the Base Conda Environment:** To run separate model
chains in parallel, the `ipyparallel` package is used. To install it on the
conda environment your Oscar jobs will run in, do the following after ssh'ing
into your Oscar account, inserting your own base conda env's name:
```
$ source activate <YOUR BASE CONDA ENVIRONMENT NAME>
$ pip install ipyparallel
```

## Quickstart

**1.** Have the filepath of the data you want to fit, and a conda environment set up as 
desribed in the ['Requirements' section](#Requirements).

**2.** In a folder on your Oscar account, download the two files `run_model_example.sh` 
and `run_model_example.py`.

**3.** In `run_model_example.sh`, edit the `mail-user` and `account` to point to your 
email address and your lab's Oscar condo. (The Frank lab's condo is 
`carney-frankmj-condo`.) Here is an example:
```
#SBATCH --mail-user=pranavan_chanthrakumar@brown.edu
#SBATCH --account=carney-frankmj-condo
```

**4.** In `run_model_example.sh`, edit the conda environment referenced to match the one 
you want to use. Here is an example where the conda environment to use is named 'pyHDDMN':
```
source activate pyHDDMN
```

**5.** In `run_model_example.py`, set your model details in the `MODEL SPECIFICATION` 
section. Be sure your datafile exists and has the columns you specify in your
model definition. Here is an example:
```
# **** MODEL SPECIFICATION ****
# Set the following variables for your model of interest 
datafilepath = './data_cleaned_112122.csv' # Data that the model is fit to
model_name ='Angle_v1'                     # Used in file names
model = 'angle'                            # Used in call to HDDM
nmcmc = 100
burn_in = 20
Group_only = False
n_samples = 10
p_outlier = 0.05
model_def = [
  'v ~ 1 + sub_reward + sub_averse', 
  'a ~ 1',
  'z ~ 1 + DBSStatus',
  't ~ 1',
  'theta ~ 1'
]

# If this is changed, be sure to change the number of 
# cores requested in the bash script that calls this file
num_chains = 3
# ****************************** 
```

**6.** After completing the above steps, if you run:
```
sbatch ./run_model_example.sh
```
in the folder that contains this bash file, you will submit one 
[batch job](https://docs.ccv.brown.edu/oscar/submitting-jobs/batch) to Oscar that will 
run 3 chains of your model in parallel. Posteriors, traces, chain files, and other related 
files will be stored in the same folder that contains the bash and python files you downloaded 
in step 1. An output file called 'out_example.txt' will be created that has the output of the 
script, and a separate slurm output file is also auto-created associated with the parent 
Oscar job.


## Notes

### Changing Script File Names or Output File Names

If you want to remove the `_example` suffix on the python file, or change it to
something else, be sure to edit the *bash* script to have the `PYTHON_FILE` variable
reflect the new name for the python file. You can also change the name of the
script's output file by editing the `BASH_OUTFILE` variable in the bash script.

### Running More (or Less) than 3 Chains

Be mindful of Oscar's potential limit on the number of cores requested and any limitation
on lab resources (see [this section](#Can-I-just-request-more-cores-to-speed-things-up?)).

With this in mind, if you want to run more or less than 3 chains in parallel, 2 changes 
will need to be made to ensure that the number of cores requested to Oscar matches up with 
the number of chains run per model 
([and to prevent unexpected runtime slowdown](#Can-I-just-request-more-cores-to-speed-things-up?)):
* In `run_model_example.sh`, edit the `#SBATCH -c 3` line to have the desired number
 of chains. For example, if you wanted to run 5 chains, edit the line to be `#SBATCH -c 5`
* In `run_model_example.py`, edit the `num_chains` variable in the `MODEL SPECIFICATION`
to the desired number of chains. Here is an example for 5 chains:
```
# **** MODEL SPECIFICATION ****

...

# If this is changed, be sure to change the number of 
# cores requested in the bash script that calls this file
num_chains = 5
# ******************************
```


## FAQ's

#### Why not just use jobarray or submit a job per chain to Oscar?

You *can* submit multiple jobs to Oscar or make use of 
[job arrays](https://docs.ccv.brown.edu/oscar/submitting-jobs/array) to run each 
chain (one job per chain). The benefit of having chains run in parallel 
*via a python script* is that the python script can *wait* for all the chains to finish, 
load them all, and then run further calculations on the combined chains (gelman-rubin stats, 
ppc plot generation if convergence occurs, etc.). With jobarray's & multiple jobs, you'd 
need another layer (another parent job or script, or a manual step by *you* after being 
notified that your chain-jobs are done) to wait for each job to finish before running 
these calculations on the combined chains.

In other words, this script is the first step towards a 'Set it and forget it' world 
where all you'd need to do is set some model specification and return to PPC's and 
data that can inform you how well your model fit.

#### Isn't there already info on how to parallelize on the HDDM docs?

There is! Scroll towards the bottom of 
[this section](https://hddm.readthedocs.io/en/latest/howto.html#r-hat-convergence-statistic) 
to read more.

`ipyparallel` relies on having your CPU setup (with the cores that each parallel engine 
instantiated by `ipyparallel` runs on) ready before making calls to it in your Python code.
When running code on a machine with more than one CPU (like your laptop), the code on 
[parallelization in the HDDM docs](https://hddm.readthedocs.io/en/latest/howto.html#r-hat-convergence-statistic) 
will likely lead to the expected performance speedup.

When submitting jobs to Oscar, though, one additional step is needed to yield the expected 
performance speedup. Namely, you need to request a number of cores from Oscar 
that matches the number of chains you have. Running `ipyparallel`-related code on Oscar 
*without* requesting the appropriate number of cores does **not** result in a performance 
speedup. This package takes care of this additional step, while also providing a template for
any further calculations you might want to do on the combined chains.

You can read more about `ipyparallel` [here](https://ipyparallel.readthedocs.io/en/latest/).

#### Can I just request more cores to speed things up?

This script was designed to make use of one core per chain; there may be unexpectedly 
slow runtime performance if the cores requested don't match up with the number of chains 
to run. Starting up each parallel engine also has some overhead, so requesting a larger number
of cores may lead to even slower runtimes.

If you wanted to run more than 3 chains, though, you could request more cores and 
have each chain run in parallel on each core (see 
[this section](#Running-More-or-Less-than-3-Chains). Oscar likely has a limit to the 
number of cores that can be requested. If an error message like 'Requested configuration 
is not available' appears, this might be the case. See a similar situation for 
[MPI jobs](https://docs.ccv.brown.edu/oscar/submitting-jobs/mpi-jobs#maximum-number-of-nodes-for-mpi-programs).

#### I want to see the output of the parallel engines as computations are happening.

Seeing live output from each parallel engine is currently not possible, but is being worked on.
[Contact us](#Contact) to let us know you want this as well.

#### Do I need to use the provided bash script?

No! If you have the python file and made the appropriate changes to it as detailed
in the [Quickstart](#Quickstart) section, then you can also submit a job to Oscar 
via the command line and specify the number of desired cores there, too. See 
[this link](https://docs.ccv.brown.edu/oscar/submitting-jobs/batch) for more info.

#### I want to run more than 3 chains, what should I do?

See [this section](#Running-More-or-Less-than-3-Chains).

#### I don't want to use the HDDMnnRegressor method, but something else.

You can edit the `run_model_example.py` code to do this. Look for the line
`m = hddm.HDDMnnRegressor( ... )` and change the call and parameters accordingly.

#### What are all these other flags in the bash script?

Read more about them [here](https://docs.ccv.brown.edu/oscar/submitting-jobs/batch).

#### When running the script, I don't see that chain files are being saved.

This likely means there's an error in the actual model fitting. Double check
that your data filepath and model definition is correct. If so, then try fitting
your model once without using this script. You could also [contact us](#Contact) 
if you are having issues with the script that aren't present when fitting the 
model without the script.

#### I have a another question/concern/thought/complaint!

See the [Contact section](#Contact).


## Contact

Contact us with any questions/concerns/thoughts/complaints via 
[this form](https://docs.google.com/forms/d/e/1FAIpQLScJPuLQS4sRWiLShrhTDgYo_ijISAFJTwv5oVO2vTklniZDkQ/viewform) 
or email pranavan_chanthrakumar@brown.edu.
