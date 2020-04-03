# hide unused plugins
for i in bokeh_display wavelet Bruker_NMR_FT  Fitter  Integrate  Linear_prediction  PALMA  apmin  gaussenh test zoom3D
do
	mv  .conda/envs/Spike/lib/python3.8/site-packages/spike/plugins/$i.py .conda/envs/Spike/lib/python3.8/site-packages/spike/plugins/_$i.py
done
