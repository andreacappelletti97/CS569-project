#!bash
#Installation script

#Clone the repo
#git clone https://github.com/andreacappelletti97/HPPS_project.git
#Install cur
sudo apt-get install curl

#Install anaconda
cd /tmp
curl –O https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh
bash Anaconda3-2020.02-Linux-x86_64.sh

#Export conda as a global variable
export PATH=~/anaconda3/bin:$PATH

#Create conda environment with python 2.7
conda create --name py2 python=2.7
#Source necessary files
source ~/anaconda3/etc/profile.d/conda.sh
#Activate conda environment
conda activate py2

#Install required packages
conda install numpy

conda install basemap

pip install pyshp

pip install geopy

conda install scipy

