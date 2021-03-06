import psycopg2
import xlrd
import re
import unicodedata
import numpy as N
from time import mktime
from datetime import datetime
from time import mktime
import time
import os
import glob
import simplekml as kml
import subprocess
import datetime as dtm
from types import *
import sys
import ppygis
import StringIO
import shapefile
from osgeo import osr
from pylab import *
import matplotlib as plt

import ConfigParser
from glob import glob

cfg = ConfigParser.ConfigParser()
cfg.read(os.path.dirname(__file__)+'/setup.cfg')
sys.path.append(re.sub('[/][^/]+$','',os.path.dirname(__file__)))

from Altimetry.Interface import *

def plot_brace(ax,left,right,y,height,up=True,color='k',annotate=None,fontsize=12):
    if up:hgt = height/2.
    else: hgt = -height/2.
    
    mid = (left+right)/2.
    
    brace,tip = ax.plot([left,left,right,right],[y-hgt,y,y,y-hgt],'-%s' % color,[mid,mid],[y,y+hgt],'-%s' % color)
    if type(annotate)!=NoneType:
        if up:vert='bottom'
        else:vert='top'
        txt = ax.annotate(annotate,[mid,y+hgt*1.2],horizontalalignment='center',verticalalignment=vert,fontsize=fontsize)
        return brace,tip,txt
    else:
        return brace,tip
 
   
#PLOTTING FULL PARTITIONING
lamb = GetLambData(longest_interval=True,userwhere="ergi.gltype='1' and ergi.name != 'Taku Glacier'", as_object=True, orderby='glimsid',results=True)

width = 0.4
#ax4 = fig.add_axes([axwidth*2+0.15,0.1,axwidth,0.8])



#########################################################################
#FLUXES WITH ALL GLACIERS
#WHICH OF THE LAMB SURVEYED TIDEWATERS DO WE HAVE FLUX ESTIMATES?
w = N.where(N.isnan(lamb.eb_bm_flx.astype(float))==False)[0]
print len(w)
#of those get the total flux and flux error
flx=-N.sum(lamb.eb_bm_flx.astype(float)[w])
flxerr=N.sum((lamb.eb_bm_err.astype(float)[w])**2)**0.5

#NOW NEED THE ALTIMETRY NET MASS BUDGET FOR EACH OF THESE GLACIERS
##################
t = GetSqlData2("SELECT glimsid, SUM(mean*area)/1e9*0.85 as net, (((((SUM(error*area)/SUM(mean*area))^2+(0.06/0.85)^2)^0.5)*SUM(mean*area)/1e9*0.85)^2 + (0)^2)^0.5::real as neterror from resultsauto WHERE glimsid IN ('%s') GROUP BY glimsid;" %  "','".join(lamb.glimsid))
vol=N.sum(t['net'][w])
volerr=N.sum(t['neterror'][w])

#################
#NOW CLIMATIC BALANCE OR SMB
smb = N.sum(vol - flx)
smberr = (volerr**2+flxerr**2)**0.5

print N.c_[smb]

#########################
#NOW BEGINNING PLOTTING
fig = plt.figure(figsize=[8,3])
colors = [[1,0.8,0.8],[1,0,0],[0.8,0.8,1],[0,0,1],[0.8,1,0.8],[0,1,0]]
axwidth=0.23

ax = fig.add_axes([0.43,0.1,axwidth*2.35,0.8],frameon=False)

barlocs = [0,1,4,5,2,3]

b1,b2,b3 = ax.bar([3.2,4.2,5.2],[smb,flx,vol],yerr=[smberr,flxerr,volerr],width=width,color=[0.8,0.8,0.8],ecolor='k') # 


#########################################################################
#FLUXES WITH ALL GLACIERS EXCLUDING COLUMBIA
#WHICH OF THE LAMB SURVEYED TIDEWATERS DO WE HAVE FLUX ESTIMATES?
w = N.where(N.logical_and(N.isnan(lamb.eb_bm_flx.astype(float))==False,N.array([x!='Columbia Glacier' for x in lamb.name])))[0]

#of those get the total flux and flux error
flx=-N.sum(lamb.eb_bm_flx.astype(float)[w])
flxerr=N.sum((lamb.eb_bm_err.astype(float)[w])**2)**0.5

#flx=-N.mean((lamb.eb_bm_flx.astype(float)/lamb.area*1000.)[w])                     #THIS CALCULATES NUMBERS FOR PAPER OR THE SAME NUMBERS BUT IN M/W EQ RATHER THAN GT
#flxerr=N.sum(((lamb.eb_bm_err.astype(float)/lamb.area*1000.)[w])**2)**0.5/len(w)         #REROR this isn't right!!THIS CALCULATES NUMBERS FOR PAPER OR THE SAME NUMBERS BUT IN M/W EQ RATHER THAN GT

#NOW NEED THE ALTIMETRY NET MASS BUDGET FOR EACH OF THESE GLACIERS
##################
#t = GetSqlData2("SELECT glimsid, SUM(mean*area)/1e9*0.85 as net, (((((SUM(error*area)/SUM(mean*area))^2+(0.06/0.85)^2)^0.5)*SUM(mean*area)/1e9*0.85)^2 + (0)^2)^0.5::real as neterror from resultsauto WHERE glimsid IN ('%s') GROUP BY glimsid;" %  "','".join(lamb.glimsid))
t = GetSqlData2("SELECT glimsid, SUM(mean*area)/SUM(area)*0.85::real as net, (((((SUM(error*area)/SUM(mean*area))^2+(0.06/0.85)^2)^0.5)*SUM(mean*area)/SUM(area)*0.85)^2+(0)^2)^0.5::real as neterror from resultsauto WHERE glimsid IN ('%s') GROUP BY glimsid;" %  "','".join(lamb.glimsid))   #THIS CALCULATES NUMBERS FOR PAPER OR THE SAME NUMBERS BUT IN M/W EQ RATHER THAN GT
vol=N.sum(t['net'][w])       
volerr=N.sum(t['neterror'][w])   

#vol=N.mean(t['net'][w])                            #THIS CALCULATES NUMBERS FOR PAPER OR THE SAME NUMBERS BUT IN M/W EQ RATHER THAN GT
#volerr=(N.sum(t['neterror'][w]**2))**0.5/len(w)    #ERROR this isn't right!!THIS CALCULATES NUMBERS FOR PAPER OR THE SAME NUMBERS BUT IN M/W EQ RATHER THAN GT
#################
#NOW CLIMATIC BALANCE OR SMB
smb = N.sum(vol - flx)
smberr = (volerr**2+flxerr**2)**0.5
w2 = N.where(lamb.name!='Columbia Glacier')

b1,b2,b3 = ax.bar(N.array([3.2,4.2,5.2])+width,[smb,flx,vol],yerr=[smberr,flxerr,volerr],width=width,color=[0.5,0.5,0.5],ecolor='k') # 

print smb,flx,vol
print smberr,flxerr,volerr
#########################################################################
#UNPARTITIONED MASS LOSS



#list of glimsids of glaciers that have partitioned mass balances
partitionedglims = lamb.glimsid[N.where(N.isnan(lamb.eb_bm_flx.astype(float))==False)[0]]
t = GetSqlData2("SELECT name, glimsid, SUM(mean*area)/1e9*0.85 as net, (((((SUM(error*area)/SUM(mean*area))^2+(0.06/0.85)^2)^0.5)*SUM(mean*area)/1e9*0.85)^2 + (0)^2)^0.5::real as neterror from resultsauto WHERE glimsid NOT IN ('%s') AND gltype = '1' GROUP BY glimsid,name;" %  "','".join(partitionedglims))
unpart_vol=N.sum(t['net'][w])
unpart_volerr=N.sum(t['neterror'][w])

b1 = ax.bar([6.5],[unpart_vol],yerr=[unpart_volerr],width=width,color=[0.5,0.5,0.5],ecolor='k') # 

ax.annotate('SMB',[3+width,-4],rotation=90,horizontalalignment='center',verticalalignment='top',fontsize=10)
ax.annotate('Calving',[4+width,-16],rotation=90,horizontalalignment='center',verticalalignment='top',fontsize=10)
ax.annotate('Net',[5+width,-11],rotation=90,horizontalalignment='center',verticalalignment='top',fontsize=10)
ax.annotate('Unpartitioned',[6.5+width/2,-4],rotation=90,horizontalalignment='center',verticalalignment='top',fontsize=10)
font = matplotlib.font_manager.FontProperties(family='Arial', weight='bold', size=15)
ax.annotate('B.',[0.5,-49],horizontalalignment='center',verticalalignment='center',fontproperties=font)
ax.annotate('C.',[3.4,-49],horizontalalignment='center',verticalalignment='center',fontproperties=font)

########################################################################
#MASS BALANCE BY GTS 
density=0.85
density_err=0.06
acrossgl_err=0.000


d = GetSqlData2("SELECT gltype,surveyed,SUM(mean*area)/SUM(area)*0.85 as myr,SUM(mean*area)/1e9*0.85 as gt,(((((SUM(error*area)/SUM(mean*area))^2+(0.06/0.85)^2)^0.5)*SUM(mean*area)/SUM(area)*0.85)^2+(0)^2)^0.5::real as myrerr,(((((SUM(error*area)/SUM(mean*area))^2+(0.06/0.85)^2)^0.5)*SUM(mean*area)/1e9*0.85)^2 + (0)^2)^0.5::real as gterr,sum(area)/1e6::real as area from resultsauto group by gltype,surveyed order by gltype,surveyed;")

colors = [[1,0.8,0.8],[1,0,0],[0.8,0.8,1],[0,0,1],[0.8,1,0.8],[0,1,0]]

colors = N.array([[209,150,111],[163,100,57],[128,162,232],[45,80,150],[138,212,102],[75,150,38]])/255.

barlocs = [4,4+width,6,6+width,5,5+width]
barlocs = [0,0+width,1,1+width,2,2+width]


#PLOTTING Mass Balance(m w. eq.)

#ADDING ERROR FOR SMALL GLACIER BIAS from output from balance_by_area2.py
uneven_error = [list(d['gterr']),list(d['gterr'])]
uneven_error[0][0]+=2.605

#PLOTTING
pl1 = ax.bar(barlocs, d['gt'], color=colors, width=width,yerr=uneven_error,error_kw=dict(ecolor='k'))

#PLOT settings
ax.axes.get_xaxis().set_visible(False)
ax.get_yaxis().tick_left()
plot_brace(ax,3.2,6.1,-35,5,up=False,annotate='Tidewater\nPartitioning',fontsize=10)
#plot_brace(ax,4,6.8,5,5,up=True,annotate='Mass Balance',fontsize=10)
for tick in ax.yaxis.get_major_ticks():tick.label.set_fontsize(11) 
xmin, xmax = ax.get_xaxis().get_view_interval()
ymin, ymax = ax.get_yaxis().get_view_interval()
ax.add_artist(Line2D((xmin, xmin), (ymin, ymax), color='black', linewidth=1.5))
ax.add_artist(Line2D((xmin, xmax), (0, 0), color='black', linewidth=1.))
ax.set_ylabel("Gt a"+"$^{-1}$",fontsize=11)



########################################################################
#MASS BALANCE BY MWeq per year 

#d = GetSqlData2("SELECT gltype,surveyed,SUM(mean*area)/SUM(area)*0.85 as myr,SUM(mean*area)/1000000000.*0.85 as gt,((SUM(error*area)/SUM(area))^2+0.06^2)^0.5 as myrerr,((SUM(error*area)/1000000000.)^2+0.06^2)^0.5 as gterr,sum(area)/1000000.::real as area from resultsauto group by gltype,surveyed order by gltype,surveyed;")

#colors = [[1,0.8,0.8],[1,0,0],[0.8,0.8,1],[0,0,1],[0.8,1,0.8],[0,1,0]]
#barlocs = [4,4+width,6,6+width,5,5+width]


#PLOTTING Mass Balance(m w. eq.)
ax2 = fig.add_axes([0.09,0.1,axwidth,0.8],frameon=False)

#ADDING ERROR FOR SMALL GLACIER BIAS from output from balance_by_area2.py
uneven_error = [list(d['myrerr']),list(d['myrerr'])]
uneven_error[0][0]+=0.0639


pl1 = ax2.bar(barlocs, d['myr'], color=colors, width=width,yerr=uneven_error,error_kw=dict(ecolor='k'))



#PLOT settings
ax2.axes.get_xaxis().set_visible(False)
ax2.get_yaxis().tick_left()
##plot_brace(ax,0.1,3.5,-35,5,up=False,annotate='Tidewater\nPartitioning')
for tick in ax2.yaxis.get_major_ticks():tick.label.set_fontsize(11) 
xmin, xmax = ax2.get_xaxis().get_view_interval()
ymin, ymax = ax2.get_yaxis().get_view_interval()
ax2.add_artist(Line2D((xmin, xmin), (ymin, ymax), color='black', linewidth=1.5))
ax2.add_artist(Line2D((xmin, xmax), (0, 0), color='black', linewidth=1))
ax2.set_ylabel("Mass Balance (m w. eq. a"+"$^{-1}$"+")",fontsize=11)

ax2.annotate('A.',[0.4,-1.2],horizontalalignment='center',verticalalignment='center',fontproperties=font)

#ax2.set_xlim([0,6.3])




plt.show()
fig.savefig("/Users/igswahwsmcevan/Papers/AK_altimetry/Figures/partition4.jpg",dpi=300)