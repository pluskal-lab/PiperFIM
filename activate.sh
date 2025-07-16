#!/bin/bash

#check if conda environment piperFIM already exists
if conda env list | grep -q 'piperfim'; then

    #if env exists, print message and activate environment
    echo "Conda environment 'piperfim' already exists. Activating existing environment..."
    conda activate piperfim

else
    #if env doesn't exist, create it and install packages in requirements.txt
    echo "Creating conda environment piperfim..."
    conda env create -f requirements.yaml
    conda activate piperfim
fi

#export cwd to PYTHONPATH
echo "Exporting current working directory to PYTHONPATH..."
export PYTHONPATH=$(pwd):$PYTHONPATH
echo "Piperfim ready!"