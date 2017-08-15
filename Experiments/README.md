## TRo 2017 Experiments

* [Preliminary](#preliminary)
* [Docker Usage](#docker)
* [Installation](#installation)
* [Experiments](#experiments)
* [Troubleshooting](#troubleshooting)

### Preliminary <a name="preliminary"></a>
This folder contains the source code to reproduce the experimental results presented in the paper.

* It contains sub folders with each folder containing an experiment.
* The modeling is done in Python language using the [GPy library](https://github.com/SheffieldML/GPy).
* The experiments can be run interactively using [IPython notebooks](https://ipython.org/) for each experiment.
* The evaluation dataset is available separately at this [link](https://github.com/buntyke/TRo2017/releases/download/v1.0/Data.zip).

### Docker Instructions <a name="docker"></a>

* A docker image was created with all the required software installed. This is the easiest way to use the source code.

#### Instructions for Windows:

* Install Docker by running the following command:
```
sudo apt-get install -y docker.io
```
* Clone the docker image for the workshop
```
sudo docker pull buntyke/tro2017
```
* Run the docker image for the workshop
```
sudo docker run -it -p 8888:8888 buntyke/tro2017
```
* The command outputs text that includes an URL like this:
```
Copy/paste this URL into your browser when you connect for the first time, to login with a token:
http://localhost:8888/?token=b8dbd6e58f68195b150bfcc69751bd97ddc20c097767d100
```
Copy the url and paste in the web browser to start the Ipython session.

#### Instructions for Ubuntu:

* Download docker-toolbox from this [link](https://www.docker.com/products/docker-toolbox).
* Install docker-toolbox and agree with all options. This will install Docker-Quickstart-Terminal.
* Open the Docker-Quickstart-Terminal application which opens a terminal.
* Download the docker image with this command:
```
docker pull buntyke/tro2017
```
* Run the docker image with this command:
```
docker run -it -p 8888:8888 buntyke/tro2017
```
The command outputs text that includes an URL like this:
```
Copy/paste this URL into your browser when you connect for the first time, to login with a token:
http://localhost:8888/?token=b8dbd6e58f68195b150bfcc69751bd97ddc20c097767d100
```
* Open a powershell and run the following command:
```
docker-machine.exe ip default
```
The command outputs an IP like this:
```
192.168.99.100
```
* Replace localhost with the IP and paste URL above in the web browser to start Ipython session:
```
http://192.168.99.100:8888/?token=b8dbd6e58f68195b150bfcc69751bd97ddc20c097767d100
```

### Installation Instructions <a name="installation"></a>

* Installation of Ipython to run notebooks (For Ubuntu):
  ```
  $ sudo pip install matplotlib --upgrade
  $ sudo pip install numpy --upgrade
  $ sudo pip install scipy --upgrade
  $ sudo pip install jupyter --upgrade
  $ sudo pip install ipython --upgrade
  $ sudo pip install filterpy --upgrade
  $ sudo pip install ipython[notebook] --upgrade
  ```
  For Windows, MAC OSX: Please install [Anaconda](https://www.continuum.io/downloads) as it contains all the required packages by default.
* Installation of GPy and its dependencies (For Ubuntu):
  ```
  $ sudo pip install GPy --upgrade
  ```
  For Windows, Mac OSX: Please follow the installation instructions from the [GPy page](https://github.com/SheffieldML/GPy).
* Clone/[Download](https://github.com/buntyke/TRo2017/archive/master.zip) the repository to your PC:
  ```
  $ git clone https://github.com/buntyke/TRo2017.git
  ```
* Download evaluation dataset into the Experiments folder:
  ```
  $ cd TRo2017/Experiments/
  $ wget "https://github.com/buntyke/TRo2017/releases/download/v1.0/Data.zip"
  $ unzip Data.zip
  ```
* Read an experiment overview and then run the desired experiment in Jupyter notebook:
  ```
  $ cd Exp1/
  $ gedit README.md
  $ jupyter notebook
  ```

### Experiments <a name="experiments"></a>

Please follow these steps in order to sequentially generate the results of the paper.

* [Preprocessing](preprocessing.ipynb): Run the preprocessing.ipynb notebook prior to the actual experiments to generate the pickle files of the dataset.

* [BGPLVM Experiment](Exp1/README.md): Comparison of BGPLVM with Principal Component Analysis (PCA). Used to generate Figures 8,9 and Table I in paper.

* [MRD Model Visualization](Exp4/README.md): Visualization of an example MRD model with test inference. Used to generate Figure 10.

* [Model Training](models.ipynb): Run the models.ipynb notebook prior to the cross validation experiments. The execution of this notebook is highly time consuming (about 3 days). Please contact the co-authors, if you would like to obtain the pre-trained models.

* [MRD Model Comparison](Exp2/README.md): Comparison of MRD with other linear regression models. Used to generate Figure 11.

* [Inference Strategies](Exp3/README.md): Comparison of various inference strategies for MRD. Used to generate Figures 12,13.

* [Feature Representations](Exp5/README.md): Comparison of different feature representations for both observation spaces. Used to generate Figures 15,16.

* [Postures Comparison](Exp6/README.md): Evaluation of generalizability of MRD to various postures of mannequin. Used to generate Figure 17.

* [T-shirts Comparison](Exp7/README.md): Evaluation of generalizability of MRD to various T-shirts. Used to generate Figure 18.

* [Framework Video](Exp8/README.md): Feature representations and latent space visualization. Used to generate later half of Framework.mp4 video.

* [Latent Features Video](Exp9/READM.md): Visualization of latent features learned by BGPLVM. Used to generate LatentFeatures.mp4 video.

### Troubleshooting <a name="troubleshooting"></a>

* Installing `jupyter` in Ubuntu could cause a dependency issue with `urllib3`. This can be resolved by running the following command:
  ```
  $ pip install appdirs --upgrade
  ```
  Please check this [issue](https://github.com/buntyke/TRo2017/issues/1) for further reference.
* The Ipython notebooks should run out of the box. However, the GPy API could change for future versions and cause some errors. This code was tested for the following versions of GPy: 0.8.x,1.0.x,1.5.x. Please switch to '1.5.x' if the error persists.
* The training time could take between 3-4 hrs per model. If the users would like to access the models trained by us, please contact the authors. [Nishanth Koganti](buntyke.github.io), [Tomohiro Shibata](brain.kyutech.ac.jp/~tom).
