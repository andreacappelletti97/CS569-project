sudo apt-get install curl

cd /tmp

curl –O https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh

bash Anaconda3-2020.02-Linux-x86_64.sh

export PATH=~/anaconda3/bin:$PATH

conda create --name py2 python=2.7

source ~/anaconda3/etc/profile.d/conda.sh

conda activate py2

conda install numpy

conda install basemap

pip install pyshp

pip install geopy

conda install scipy

