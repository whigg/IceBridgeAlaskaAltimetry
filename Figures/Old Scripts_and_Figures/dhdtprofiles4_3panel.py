# -*- coding: utf-8 -*-
import xlrd
import re
import unicodedata
import numpy as N
import datetime as dtm
import os
import glob
import simplekml as kml
import subprocess
import matplotlib.pyplot as plt
from osgeo import gdal
from types import *
import sys
import time
from mpl_toolkits.basemap import Basemap
from matplotlib.collections import PatchCollection
from osgeo.gdalnumeric import *
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab
import scipy.misc
import matplotlib
import matplotlib.colors as colors
import matplotlib.cm as cmx
import scipy.stats as stats
import scipy.stats.mstats as mstats
from numpy.ma import MaskedArray, masked, nomask
import numpy.ma as ma
import pickle
import datetime as dtm

import ConfigParser

cfg = ConfigParser.ConfigParser()
cfg.read(os.path.dirname(__file__)+'/setup.cfg')
sys.path.append(re.sub('[/][^/]+$','',os.path.dirname(__file__)))

from Altimetry.Interface import *
    

def make_interval_length_plot(axes,interval_list,colorlist,label=None):

    plt.rc("font", **{"sans-serif": ["Arial"],"size": 10})
    box = axes.boxplot(interval_list,vert=False,patch_artist=True,widths=0.7)
    print colorlist
    #axes.plot([6,10],[2.2,2.2],'-',lw=3,color=colorlist[0])
    axes.annotate(label,[0.5,0.7],xycoords='axes fraction', ha='center')
    
    for i,uzip in enumerate(zip(box['boxes'],box['medians'])):
        bx,median = uzip
        print 'bx',bx
        print 'med',median
        bx.set_facecolor(colorlist[i])
        bx.set_edgecolor(colorlist[i])
        median.set_color(color='k')
        median.set_lw(3)

    for i,uzip in enumerate(zip(box['caps'],box['whiskers'])):
        cap,whisk = uzip
        cap.set_lw(0)
        whisk.set_color(color=N.repeat(colorlist,2,axis=0)[i])
        whisk.set_ls('-')
        whisk.set_lw(3)
        
    axes.set_xticks([5,10,15,20])
    axes.set_xlabel("Interval Length (yr)")
    axes.axes.get_yaxis().set_visible(False)
    axes.get_xaxis().tick_bottom()
    axes.set_ylim([0,3])
    
    
    
plot_hist=False

user_where=["FLOOR((ergi.glactype::real-9000)/100)=0 AND gltype.surge='f'","FLOOR((ergi.glactype::real-9000)/100)=1 AND glnames.name!='Columbia'","FLOOR((ergi.glactype::real-9000)/100)=2 AND glnames.name!='Bering' AND glnames.name!='YakutatEast' AND glnames.name!='YakutatWest' AND gltype.surge='f'","gltype.surge='f'"]
#user_where=["FLOOR((ergi.glactype::real-9000)/100)=0 AND gltype.surge='f'","FLOOR((ergi.glactype::real-9000)/100)=1 AND glnames.name!='Columbia'","FLOOR((ergi.glactype::real-9000)/100)=2 AND glnames.name!='Bering' AND glnames.name!='YakutatWest' AND glnames.name!='YakutatEast' AND gltype.surge='f'"]
outroot = ["Tidewater","Lake","Land","All"]
color = ['k','g','r','r']
color = N.array([[0,0,0],[163,100,57],[45,80,150],[75,150,38]])/255.
min_intervals=N.array([0,3,5,10,3,5])
intervalsmax=N.array([3,5,10,30,30,30])
labels = ['<=3yr intervals','3-5 yrs','5-10yrs','>=10yrs','>=3yrs','>=5yrs','Before 2003','After 2002']
shpfiles = ['intervals_less3yr','intervals_3_5yrs','intervals5_10yrs','intervals_more10yrs','intervals_more3yrs','intervals_more5yrs','Before2003','After2002']
div1 = '2000-01-01'
i=0

startfromscratch=True



if startfromscratch:    

    surveyeddata = GetLambData(verbose=False,longest_interval=True,interval_max=30,interval_min=5,by_column=True,as_object=True,results=False)  # 
    #surveyeddata.fix_terminus()
    #surveyeddata.remove_upper_extrap()
    surveyeddata.normalize_elevation()
    surveyeddata.calc_dz_stats()
    #surveyeddata.extend_upper_extrap()

    land = GetLambData(verbose=False,longest_interval=True,interval_max=30,interval_min=5,by_column=True,as_object=True, userwhere="FLOOR((ergi.glactype::real-9000)/100)=0 AND gltype.surge='f'",results=False) 
    land.convert085()
    land.fix_terminus()
    land.remove_upper_extrap(remove_bottom=False)
    land.normalize_elevation()
    land.calc_dz_stats(too_few=4)
    land.extend_upper_extrap()
    

    tide = GetLambData(verbose=False,longest_interval=True,interval_max=30,interval_min=5,by_column=True,as_object=True, userwhere="FLOOR((ergi.glactype::real-9000)/100)=1 AND glnames.name!='Columbia'",results=False) 
    tide.convert085()
    tide.fix_terminus()
    tide.remove_upper_extrap(remove_bottom=False)
    tide.normalize_elevation()
    tide.calc_dz_stats(too_few=4)
    tide.extend_upper_extrap()

    lake = GetLambData(verbose=False,longest_interval=True,interval_max=30,interval_min=5,by_column=True,as_object=True, userwhere="FLOOR((ergi.glactype::real-9000)/100)=2 AND glnames.name!='Bering' AND glnames.name!='YakutatEast' AND glnames.name!='YakutatWest' AND gltype.surge='f'",results=False) 
    lake.convert085()
    lake.fix_terminus()
    lake.remove_upper_extrap(remove_bottom=False)
    lake.normalize_elevation()
    lake.calc_dz_stats(too_few=4)
    lake.extend_upper_extrap()

    columbia = GetLambData(verbose=False,longest_interval=True,interval_min=5,by_column=True,as_object=True, userwhere="glnames.name='Columbia'") 
    columbia.convert085()
    columbia.fix_terminus()
    columbia.remove_upper_extrap(remove_bottom=False)
    columbia.normalize_elevation()
    
    hubbard = GetLambData(verbose=False,longest_interval=True,interval_min=5,by_column=True,as_object=True, userwhere="glnames.name='Hubbard'") 
    hubbard.convert085()
    hubbard.fix_terminus()
    hubbard.remove_upper_extrap(remove_bottom=False)
    hubbard.normalize_elevation()
    
    wolverine = GetLambData(verbose=False,longest_interval=True,interval_min=5,by_column=True,as_object=True, userwhere="glnames.name='Wolverine'") 
    wolverine.convert085()
    wolverine.fix_terminus()
    wolverine.remove_upper_extrap(remove_bottom=False)
    wolverine.normalize_elevation()
    
    gulkana = GetLambData(verbose=False,longest_interval=True,interval_min=5,by_column=True,as_object=True, userwhere="glnames.name='Gulkana'") 
    gulkana.convert085()
    gulkana.fix_terminus()
    gulkana.remove_upper_extrap(remove_bottom=False)
    gulkana.normalize_elevation()
    
    pickle.dump([surveyeddata,land,tide,lake,columbia,hubbard,wolverine,gulkana], open( "/Users/igswahwsmcevan/Desktop/temp4.p", "wb" ))
else:
    surveyeddata,land,tide,lake,columbia,hubbard,wolverine,gulkana = pickle.load(open( "/Users/igswahwsmcevan/Desktop/temp4.p", "rb" ))

#GLACIERS THAT ARE THICKENING AT THE TERMINUS AND THINNING UP HIGH
switch = N.logical_and(N.array([N.mean(dz[:20]) for dz in tide.normdz])>0,N.array([N.mean(dz[40:80]) for dz in tide.normdz])<0)

yakeast = GetLambData(verbose=False,longest_interval=True,interval_min=5,by_column=True,as_object=True, userwhere="glnames.name='YakutatEast'") 
yakeast.fix_terminus()
yakeast.remove_upper_extrap(remove_bottom=False)
yakeast.normalize_elevation()

yakwest = GetLambData(verbose=False,longest_interval=True,interval_min=5,by_column=True,as_object=True, userwhere="glnames.name='YakutatWest'") 
yakwest.fix_terminus()
yakwest.remove_upper_extrap(remove_bottom=False)
yakwest.normalize_elevation()

samples_lim=None
err_lim=None
title=None
alphafill = 0.3

fig = plt.figure(figsize=[4,8])
ax = fig.add_subplot(3,1,1)
ax2 = fig.add_subplot(3,1,2)
ax3 = fig.add_subplot(3,1,3)
fig.subplots_adjust(bottom=0.05,top=0.99,right=0.96,hspace=0.12)
plt.rc("font", **{"sans-serif": ["Arial"],"size": 13})
#ax.set_title('Surface Elevation Change: %s Glaciers' % outroot[i])

#ax.set_xlabel('Normalized Elevation', fontsize=11)
ax.set_ylim([-6,1])
ax.set_xlim([0,1])
for tick in ax.xaxis.get_major_ticks():tick.label.set_fontsize(10) 
for tick in ax.yaxis.get_major_ticks():tick.label.set_fontsize(10) 

ax.plot(land.norme,land.dzs_mean,'-',color=N.array([163,100,57])/255.,linewidth=2.5,label='Land')
ax.plot(land.norme,land.dzs_mean-land.dzs_sem,'-',land.norme,land.dzs_mean+land.dzs_sem,'-',color=N.array([163,100,57])/255.,linewidth=1)
ax.fill_between(land.norme,land.dzs_mean+land.dzs_std,land.dzs_mean-land.dzs_std,alpha=alphafill,color= N.array([163,100,57])/255.,lw=0.01)

ax2.plot(lake.norme,lake.dzs_mean,'-',color='green',linewidth=2.5,label='Lake')
ax2.plot(lake.norme,lake.dzs_mean-lake.dzs_sem,'-',lake.norme,lake.dzs_mean+lake.dzs_sem,'-',color='green',linewidth=1)
ax2.fill_between(lake.norme,lake.dzs_mean+lake.dzs_std,lake.dzs_mean-lake.dzs_std,alpha=alphafill,color= 'green',lw=0.01)

ax2.set_ylim([-6,1])
ax2.set_xlim([0,1])

font = matplotlib.font_manager.FontProperties(family='Arial', weight='bold', size=15)
ax.annotate('A',[0.07,0.5],horizontalalignment='center',verticalalignment='center',fontproperties=font)
ax2.annotate('B',[0.07,0.5],horizontalalignment='center',verticalalignment='center',fontproperties=font)
ax2.set_ylabel("Elevation Change (m w. eq. yr"+"$\mathregular{^{-1})}$", fontsize=11,labelpad=3)

#ax.legend(fontsize=9,loc='lower right', bbox_to_anchor=(0.956, 0.47))
for dz in land.normdz:ax.plot(land.norme,dz,'-k',linewidth=0.4,alpha=0.2)
for dz in lake.normdz:ax2.plot(lake.norme,dz,'-k',linewidth=0.4,alpha=0.2)

#ax3 = fig.add_axes([0.15,0.07,0.8,0.43])
plt.rc("font", **{"sans-serif": ["Arial"],"size": 13})

#ax3.set_ylabel("Elevation Change (m yr"+"$\mathregular{^{-1})}$", fontsize=11,labelpad=-2)
ax3.set_xlabel('Normalized Elevation', fontsize=11)
ax3.set_ylim([-10,12])
ax3.set_xlim([0,1])
for tick in ax3.xaxis.get_major_ticks():tick.label.set_fontsize(10) 
for tick in ax3.yaxis.get_major_ticks():tick.label.set_fontsize(10) 

ax3.plot(tide.norme,tide.dzs_mean,'-',color='blue',linewidth=2,label='Tidewater')
ax3.plot(tide.norme,tide.dzs_mean-tide.dzs_sem,'-',tide.norme,tide.dzs_mean+tide.dzs_sem,'-',color='blue',linewidth=0.7)
ax3.fill_between(tide.norme,tide.dzs_mean+tide.dzs_std,tide.dzs_mean-tide.dzs_std,alpha=alphafill,color= 'blue',lw=0.01)
ax3.fill_between(ax.get_xlim(),N.repeat(N.array(ax.get_ylim()[0]),2),N.repeat(N.array(ax.get_ylim()[1]),2),alpha=0.1,color= 'black',lw=0.01,zorder=0)

for j,dz in enumerate(tide.normdz):
    if switch[j]: ax3.plot(tide.norme,dz,'-k',linewidth=0.3,alpha=0.3)   # can make these a separate color
    else: ax3.plot(tide.norme,dz,'-k',linewidth=0.3,alpha=0.3)
    
ax3.plot(columbia.norme,columbia.normdz[0],'--k',linewidth=1.,alpha=0.6)
ax3.plot(hubbard.norme,hubbard.normdz[0],'-.k',linewidth=1.,alpha=0.6)

ax.plot(gulkana.norme,gulkana.normdz[0],'--k',linewidth=1.,alpha=0.6)
ax.plot(wolverine.norme,wolverine.normdz[0],'-.k',linewidth=1.,alpha=0.6)

ax2.plot(yakeast.norme,yakeast.normdz[0],'--k',linewidth=1.,alpha=0.6)
#ax2.plot(yakwest.norme,yakwest.normdz[0],'-.k',linewidth=1.,alpha=0.6)

ax3.annotate('C',[0.07,10],horizontalalignment='center',verticalalignment='center',fontproperties=font)

#ax.legend(fontsize=9,loc='upper right', bbox_to_anchor=(0.945, 0.6))
#ax2.legend(fontsize=9,loc='upper right', bbox_to_anchor=(0.945, 0.6))
#ax3.legend(fontsize=9,loc='upper right', bbox_to_anchor=(0.57, 0.99))

ax4 = fig.add_axes([0.627,0.755,0.3,0.07])
make_interval_length_plot(ax4,[land.interval/365.],color[[1]],label="Land")

ax5 = fig.add_axes([0.627,0.434,0.3,0.070])
make_interval_length_plot(ax5,[lake.interval/365.],color[[3]],label='Lake')

ax6 = fig.add_axes([0.627,0.259,0.3,0.07])
make_interval_length_plot(ax6,[tide.interval/365.],['blue'],label="Tidewater")


#ax3 = ax3.twiny()
#ax3.set_xlim([0,15])
#plt.text(0.1,14,"Calving Flux (Gt a"+"$^{-1}$"+")", fontsize=11)
#ax3.set_xticks([1, 2, 3,4,5])
#for tick in ax3.xaxis.get_major_ticks():tick.label2.set_fontsize(10) 
#
#
##PLOTTING FLUXES AS CIRCLES
#termidz = [dz.compressed()[0] for dz in tide.normdz]
#
#for i,flx in enumerate(tide.eb_bm_flx.astype(float)):
#    circle1=plt.Circle([0,termidz[i]],flx,color='r',zorder=-1)
#    ell = mpatches.Ellipse(xy=[0,termidz[i]], width=flx*2, height=0.3, angle=0)
#    ax3.add_artist(ell)
#    ell.set_alpha(0.7)
#    ell.set_color('r')
plt.show()

fig.savefig("/Users/igswahwsmcevan/Papers/AK_altimetry/Figures/dhdtprofiles4_1.jpg",dpi=500)

