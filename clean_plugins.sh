# hide unused plugins
for i in bokeh_display wavelet Bruker_NMR_FT  Fitter  Integrate  Linear_prediction  PALMA  apmin  gaussenh test zoom3D
do
	mv .local/lib/python3.7/site-packages/spike/plugins/$i.py  .local/lib/python3.7/site-packages/spike/plugins/_$i.py
done
