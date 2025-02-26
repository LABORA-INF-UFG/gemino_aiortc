### Error without set config_path
```
python cli.py offer --play-from sundar_pichai.mp4 --signaling-path /tmp/test.sock --signaling unix-socket --verbose
/home/elton/anaconda3/envs/gemino/lib/python3.9/site-packages/timm/models/layers/__init__.py:48: FutureWarning: Importing from timm.models.layers is deprecated, please import via timm.layers
  warnings.warn(f"Importing from {__name__} is deprecated, please import via timm.layers", FutureWarning)
'NoneType' object is not subscriptable
'NoneType' object is not subscriptable
{'frame_shape': [1024, 1024, 3], 'use_lr_video': False, 'lr_size': 64, 'generator_type': 'occlusion_aware'}
Traceback (most recent call last):
  File "/home/elton/gemino_aiortc/examples/videostream-cli/cli.py", line 17, in <module>
    from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, generator_type
  File "/home/elton/anaconda3/envs/gemino/lib/python3.9/site-packages/aiortc-1.2.1-py3.9-linux-x86_64.egg/aiortc/contrib/media.py", line 45, in <module>
    model = FirstOrderModel(config_path, checkpoint)
  File "/home/elton/gemino_aiortc/gemino_model/first_order_model/fom_wrapper.py", line 34, in __init__
    with open(config_path) as f:
FileNotFoundError: [Errno 2] No such file or directory: 'None'
```


### Error while setting config_path to aionrtc folder
Original `media.py` file:
```
config_path = os.environ.get('CONFIG_PATH', 'None')
checkpoint = os.environ.get('CHECKPOINT_PATH', 'None')
```

Modified `media.py` file:
```
config_path = os.environ.get('~/Gemino/aiortc')
checkpoint = os.environ.get('CHECKPOINT_PATH', 'None')
```

Error output:
```
python cli.py offer --play-from sundar_pichai.mp4 --signaling-path /tmp/test.sock --signaling unix-socket --verbose 
/home/isabela/anaconda3/envs/fom/lib/python3.9/site-packages/timm/models/layers/_init_.py:48: FutureWarning: Importing from timm.models.layers is deprecated, please import via timm.layers
  warnings.warn(f"Importing from {_name_} is deprecated, please import via timm.layers", FutureWarning)
'NoneType' object is not subscriptable
'NoneType' object is not subscriptable
{'frame_shape': [1024, 1024, 3], 'use_lr_video': False, 'lr_size': 64, 'generator_type': 'occlusion_aware'}
Traceback (most recent call last):
  File "/home/isabela/Gemino/aiortc/examples/videostream-cli/cli.py", line 17, in <module>
    from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, generator_type
  File "/home/isabela/anaconda3/envs/fom/lib/python3.9/site-packages/aiortc-1.2.1-py3.9-linux-x86_64.egg/aiortc/contrib/media.py", line 45, in <module>
    model = FirstOrderModel(config_path, checkpoint)
  File "/home/isabela/Gemino/aiortc/gemino_model/first_order_model/fom_wrapper.py", line 34, in _init_
    with open(config_path) as f:
TypeError: expected str, bytes or os.PathLike object, not NoneType
```

