#!/bin/sh

conda uninstall -y opencv
conda install -y -c menpo opencv=2.4.11
pip install -U /home/iizuka/foodcomputer-vm/common