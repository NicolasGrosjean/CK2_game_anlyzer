# -*- coding: utf-8 -*-
"""
Created on July 2017

@author: Nicolas
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

#%%

dataDir = "../save_parser/results/"
imageDir = "../graphs/images/"

#%%

savePrefix = "save_test_"

#%%

# Image resolution
width = 16
height = 9

# Multiplication of previous ones by dpi to have pixel resolution
dpi = 100 

#%%

# Cathedral points for each steps
steps = [100, 600, 2600, 3100, 5600, 6800,
         8300, 9800, 10300, 10800, 11300, 12000]

#%%

# OPUS FRANCIGENUM

#TODO : Get the date of the global flag
ofYear = 1097

#TODO : Analyze the title flag repaired_cathedral

#%%

dfTitleVar = pd.read_csv(dataDir + savePrefix + "TitleVariables.csv")
dfChar = pd.read_csv(dataDir + savePrefix + "CharacterStats.csv")
dfArtFlag = pd.read_csv(dataDir + savePrefix + "ArtifactFlags.csv")
dfArtStats = pd.read_csv(dataDir + savePrefix + "ArtifactStats.csv")

#%%

cathedral = dfTitleVar[dfTitleVar["variable"] == "cathedral"]

#%%

print("Holdings which build Cathedral")
print(cathedral["title"].unique())

#%%

#TODO : Analyze the cathedral province modifiers

#TODO : Analyze the relic disparition

#%%

################## ANALYZE INCOMES OF RELIC OWNERS ############################
dfArt = pd.merge(dfArtFlag, dfArtStats, on="artifact")

#%%

############## ANALYZE THE CATHEDRAL BUILDING EVOLUTION #######################
cathedralByYear = pd.DataFrame()
for year in cathedral["year"].unique():
    cathedralByYear = pd.concat([cathedralByYear, cathedral.loc[cathedral["year"] == year, ["title","value"]].set_index("title").rename(columns={'value':year})], axis=1)
    

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Cathedral evolution (Opus Francigenum {0})".format(ofYear),
             fontsize=20)
cathedralByYear.transpose().plot(ax=ax, fontsize=20, lw=2)
for i in range(len(steps)):
    ax.axhline(steps[i], color="black", linestyle='--')
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "Cathedral.png", dpi=dpi)
