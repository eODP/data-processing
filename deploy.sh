#!/bin/bash

rsync -av --progress --exclude={"__pycache__",".pytest_cache",".DS_Store","tests"} --rsh='ssh -p7000' ./notebooks/cleaned_data $1:/data/eodp/data_processing

