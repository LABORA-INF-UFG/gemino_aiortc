# Gemino installation
The OS used in this guide was the Ubuntu 20.04.

OS dependencies
```bash
sudo apt update
sudo apt-get install -y libavdevice-dev libavfilter-dev libopus-dev libvpx-dev pkg-config libsrtp2-dev gcc
```

Install conda

Download and install Anaconda from:
[Anaconda Distribution](https://www.anaconda.com/products/distribution)

Once downloaded, navigate to the directory where the `.sh` file is located and run:
```bash
bash Anaconda3-2024.10-1-Linux-x86_64.sh
```


Clone the repo and the model submodule
```bash
git clone --recurse-submodules https://github.com/LABORA-INF-UFG/gemino_aiortc
```

Setup the conda environment
```bash
conda create -n gemino python=3.9.21
```

Install conda packages
```bash
conda activate gemino
conda install "setuptools <65"
```

Install python packages
```
python3 -m pip install av==8.1.0 opencv-python face_alignment pyee==8.2.2 protobuf==3.20.0 bitstring pyyaml scikit-image==0.18.3  tensorboardX==2.6.2.2 flow-vis piq==0.8.0 timm==1.0.15 torchprofile==0.0.4 pandas==2.2.3 lpips==0.1.4 numpy==1.26.4 scikit-learn==1.6.1
```

Compile `aiortc` code. Replace $USER with your username. Check if the path is correct for your anaconda env python3 binary file.
```
sudo /home/$USER/anaconda3/envs/gemino/bin/python3 setup.py install
```

Export PYTHONPATH environment var. Replace the $REPO_PATH with your gemino_aiortc location folder.
```
export PYTHONPATH=$REPO_PATH/gemino_model:$REPO_PATH/SwinIR:$REPO_PATH/lte
# example
export PYTHONPATH=/home/elton/gemino_aiortc/gemino_model:/home/elton/gemino_aiortc/SwinIR:/home/elton/gemino_aiortc/lte
```

Get the video of Sundar Pichai to use as sample.
```bash
pip install -U yt-dlp
cd aiortc
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" "https://www.youtube.com/watch?v=gEDChDOM1_U&vl=en" -o "examples/videostream-cli/sundar_pichai.mp4"
```

Run the sender in one terminal (this opens a unix socket connection and waits for receiver to connect)
```bash
cd examples/videostream-cli
python cli.py offer --play-from sundar_pichai.mp4 --signaling-path /tmp/test.sock --signaling unix-socket --verbose 2>sender_output
```

Run the receiver in other terminal (this connects to the receiver's unix socket)
```bash
cd examples/videostream-cli
python cli.py answer --record-to sundar_pichai_recorded.mp4 --signaling-path /tmp/test.sock --signaling unix-socket --verbose 2>receiver_output
```
---

**MODIFICATIONS:** The expected output right now is just three lines corresponding to receiving video, audio and keypoints since there is a bug in the main branch (and no video is recorded). 

If anything goes wrong, please look at the two output files for any obvious errors. If everything works as desired and the video is recorded to `sundar_pichai_recorded.mp4`, proceed below to setup the model and its dependencies.

# FOM and model dependencies
From the home directory of the repo `/path/to/aiortc`, use your path to the repo and run,
```bash
export PYTHONPATH=$PYTHONPATH:"/path/to/aiortc/nets_implementation"
```
You might want to place this in your bashrc (or whichever terminal you use), so that the Python path always includes the `nets_implementation` submodule.


Test that the model and dependencies work. If it complains that it can't find `first_order_model`, your python path may not be configured in this shell.

**MODIFICATIONS:** The `video_name` variable in `fom_api_test.py` and the `checkpoint_path` field in `config/api_sample.yaml` both have to be changed to use your path to the video and checkpoint respectively.
```bash
cd nets_implementation/first_order_model
python fom_api_test.py
```
If all worked correctly, you will see a `prediction.mp4` file in the directory that shows a botched prediction of my face.

# Integrating FOM and Aiortc
In the main aiortc repo, checkout the `api_integration` branch (until it has been merged with master)
```bash
git checkout api_integration
```

**MODIFICATIONS:** Go into `aiortc/src/aiortc/contrib/media.py` and alter the `config_path` variable at
the top to refer to the path on your machine to the `aiortc` repo. 

Then, make sure the aiortc installed in the `fom` conda environment has the latest changes
``` bash
conda activate fom
sudo python setup.py install
```

Now, repeat the steps to run the `videostream-cli` application but now with calls to the model to run
prediction rather than use the default video stream.
Run the sender in one terminal 
```bash
cd examples/videostream-cli
conda activate fom
python cli.py offer --play-from vibhaa_smiling_modified.mp4 --signaling-path /tmp/test.sock --signaling unix-socket --verbose 2>sender_output
```

Run the receiver in other terminal after waiting for a couple of seconds (because the sender model initiation takes a bit and it may not be immediately ready to accept connections)
```bash
cd examples/videostream-cli
conda activate fom
python cli.py answer --record-to vibhaa_prediction_recorded.mp4 --signaling-path /tmp/test.sock --signaling unix-socket --verbose 2>receiver_output
```

If anything goes wrong, please look at the two output files for any obvious errors. 
**NOTE** that we expect some bugs and output such as "It is stopping in PlayerStreamTrack, error happens before this". We're working on addressing this. 

Nevertheless, if everything works as desired and the video is recorded and playable at `vibhaa_prediction_recorded.mp4`, you're all set.  


