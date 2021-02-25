import h5py

f = h5py.File('mask_rcnn_damage_0160.h5', 'r')
print(f.attrs.get('keras_version'))

# python .\custom.py splash  --weights .\mask_rcnn_damage_0160.h5 --image .\1.jpg