# colormaps
A collection of colormaps

For the NCL color maps do the following
```console
export NCARG_COLORMAPS=$HOME/kode/colormaps:$NCARG_ROOT/lib/ncarg/colormaps
python3 convert_json.py --inputname SINTEF1.json --outputname SINTEF1.rgb && cat *.rgb
```
