# -*- coding: utf-8 -*-
"""
Created on June 2017

@author: Nicolas
"""
#(provVar, provMod, provFlag, titleVar, titleFlag, titleTyp, charStats, charFlag, artFlag, artStats) = parse(lines)
import os
import io
import pandas as pd

#%%  

saveDir = "../save_archiver/saves/"
targetDir = "../save_parser/results/"

#%%

savePrefix = "save_test_"

#%%

extractedCharStats = list({"b_d", "d_d", "prs", "piety", "wealth", "emp",
                           "host", "emi", "eyi", "rel", "cul", "bn", "fat", "mot"})
charStatLib = {"b_d" : "Birth date", "d_d" : "Death date", "prs" :"Prestige",
               "piety": "Piety", "wealth" : "Wealth", "emp" : "Employer",
               "host" : "Host", "emi" : "Estimated month income",
               "eyi" : "Estimated year income", "rel" : "Religion",
               "cul" : "Culture", "bn" : "Birth Name", "fat" : "Father",
               "mot": "Mother"}
               
extractedArtStats = list({"type", "owner", "org_owner", "obtained", "equipped",
                          "active"})
artColumnOrder = ["type", "owner", "org_owner", "obtained", "equipped", "active"]

#%%
provinceKey = "provinces="
variableKey = "variables="
titleKey = "title="
characterKey = "character="
artifactKey = "artifacts="

modifierToken = "modifier"
flagToken = "flags"

provinceScope = "province"
titleScope = "title"
charScope = "character"
artScope = "artifact"

#%%
def unspaced(string):
    return string.replace(' ', '').replace('\t', '').replace('\n', '').replace('\"', '')

#%%

def goodScopeModifier(deep, scopeType):
    if scopeType == provinceScope:
        return (deep == 4)
    if scopeType == titleScope:
        return (deep == 5)
    if scopeType == charScope:
        return (deep == 4)
    # No modifier in other scopes, so it is false
    return False;
            

#%%

def parseScope(it, init, n, scopeType):
    """
    Parse the scopes of a CK2 save game
    
    :param it: iterator of the lines when we are at the province key
    :param init: current line number
    :param n: number of lines in the file
    :param scopeType: name of the scope type
    :return: list of scope variables, modified it and init
    :rtype: (variable dictionnary, modifier dictionnary, iterator, int,
             title type dictionnary, character stats, flag dictionnary,
             artifact stats)
    """
    var = list()
    mod = list()
    flag = list()
    titTyp = list()
    charSt = list()
    artSt = list()
    i = init
    isProvince = (scopeType == provinceScope)
    isCharacter = (scopeType == charScope)
    isArt = (scopeType == artScope)

    deep = 2 # deep 0 = root, 1 = provinces
    isVariable = False # Is currently parsing a variable bloc
    isTitle = False # Is currently parsing a title bloc
    isFlag = False # Is currently parsing a flag bloc
    oneChar = None # Stats of one character
    oneArt = None # Stats of one artifact
    while (deep > 1) & (i < n):
        i += 1
        line = unspaced(next(it))
        if '{' in line:
            deep += 1
        if '}' in line:
            deep -= 1
            isVariable = False
            isTitle = False
            isFlag = False
        tokens = line.split('=')
        if len(tokens) == 2:
            if deep == 2 :
                scope = tokens[0]
                if isCharacter :
                    # Save previous character
                    if oneChar != None:
                        charSt.append(oneChar)
                    # Prepare to store the next one
                    oneChar = dict.fromkeys(list({scopeType}))
                    oneChar[scopeType] = scope
                if isArt :
                    # Save previous artifact
                    if oneArt != None:
                        artSt.append(oneArt)
                    # Prepare to store the next one
                    oneArt = dict.fromkeys(list({scopeType}))
                    oneArt[scopeType] = scope
            
            # Variable parsing
            if isVariable:
                var.append({scopeType:scope, "variable":tokens[0],
                            "value":tokens[1]})
            if (deep == 3) & (variableKey in line):
                isVariable = True
              
            # Modifiers parsing
            if (tokens[0] == modifierToken) & (tokens[1] != '') & goodScopeModifier(deep, scopeType) :
                mod.append({scopeType:scope, "modifier":tokens[1]})
                
            # Flag parsing
            if isFlag:
                flag.append({scopeType:scope, "flag":tokens[0], "date":tokens[1]})
            if (tokens[0] == flagToken) & (tokens[1] == ''):
                isFlag = True
            
            # Title parsing
            if isProvince & (deep == 3) & (tokens[0].startswith("b_")) :
                title = tokens[0]
                isTitle = True             
            if isTitle & (tokens[0] == "type"):
                titTyp.append({provinceScope:scope, titleScope:title,
                               "type": tokens[1]})
                               
            # Character parsing
            if isCharacter & (tokens[0] in extractedCharStats):
                oneChar[charStatLib[tokens[0]]] = tokens[1]
                
            # Artifact parsing
            if isArt & (tokens[0] in extractedArtStats):
                oneArt[tokens[0]] = tokens[1]
    return (var, mod, it, i, titTyp, charSt, flag, artSt)

#%%

def parse(lines):
    """
    Parse the lines of a CK2 savegame file
    
    :return: (provVar, provMod, provFlag, titleVar, titleFlag, titTyp,
              charStats, charFlag, artFlag, artStats)
    """
    characterFound = False
    provinceFound = False
    titleFound = False
    artifactFound = False
    n = len(lines)
    i = 0
    it = iter(lines)
    while (not artifactFound) & (i < n):
        i += 1
        line = next(it)
        
        if (characterKey in line) & (not characterFound):
           characterFound = True 
           while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
           (charVar, charMod, it, i, empty, charStats, charFlag, empty) = parseScope(it, i, n, charScope)
        
        if characterFound & (provinceKey in line) & (not provinceFound):
            provinceFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (provVar, provMod, it, i, titTyp, empty, provFlag, empty) = parseScope(it, i, n, provinceScope)
            
        if provinceFound & (titleKey in line) & (not titleFound):
            titleFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (titleVar, titleMod, it, i, empty, empty, titleFlag, empty) = parseScope(it, i, n, titleScope)
        
        if titleFound & (artifactKey in line) & (not artifactFound):
            artifactFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (empty, empty, it, i, empty, empty, artFlag, artStats) = parseScope(it, i, n, artScope)
            
    return (provVar, provMod, provFlag, titleVar, titleFlag, titTyp, charStats,
            charFlag, artFlag, artStats)

#%%

def getYearFromFileName(fileName):
    parts = fileName.split('.')
    if len(parts) > 1:
        name = parts[0]
        parts = name.split('_')
        return parts[len(parts) - 1]
    return None
    
#%%
def createOrConcatDataFrame(dictionnary, df, year):
    """
    Create a dataframe or concatenate with df from a dictionnary
    
    :param dictionnary:
    :param df: if len(df) == 0 then create the dataframe,
                otherwise concatenate the dictionnary to df
    :param year: Added year information to the dictionnary
    :return: dataframe
    """
    dfYear = pd.DataFrame(dictionnary)
    dfYear["year"] = year
    if len(df) == 0:
        df = dfYear
    else:
        df = pd.concat([df, dfYear], axis=0)
    return df

#%%

filesToParse = []
for fileName in os.listdir(saveDir):
    if fileName.startswith(savePrefix):
        filesToParse.append(fileName)
print("{} files to parse".format(len(filesToParse)))

#%%

dfProvVar = pd.DataFrame()
dfProvMod = pd.DataFrame()
dfProvFlag = pd.DataFrame()
dfTitleVar = pd.DataFrame()
dfTitleFlag = pd.DataFrame()
dfCharStats = pd.DataFrame()
dfCharFlag = pd.DataFrame()
dfArtStats = pd.DataFrame()
dfArtFlag = pd.DataFrame()
for fileName in filesToParse:
    # Get the year
    year = getYearFromFileName(fileName)
    if year == None :
        continue
    
    # Get the lines
    readFile = io.open(saveDir + fileName, 'rt', 1, 'latin_1')
    lines = readFile.readlines()
    readFile.close()
    
    # Parse
    (provVar, provMod, provFlag, titleVar, titleFlag, titleTyp,
     charStats, charFlag, artFlag, artStats) = parse(lines)
    
    # Data consolidation
    dfProvVar = createOrConcatDataFrame(provVar, dfProvVar, year)
    dfProvMod = createOrConcatDataFrame(provMod, dfProvMod, year)
    dfProvFlag = createOrConcatDataFrame(provFlag, dfProvFlag, year)
    dfTitleVar = createOrConcatDataFrame(titleVar, dfTitleVar, year)
    dfTitleFlag = createOrConcatDataFrame(titleFlag, dfTitleFlag, year)
    dfCharStats = createOrConcatDataFrame(charStats, dfCharStats, year)
    dfCharFlag = createOrConcatDataFrame(charFlag, dfCharFlag, year)
    dfArtStats = createOrConcatDataFrame(artStats, dfArtStats, year)
    dfArtFlag = createOrConcatDataFrame(artFlag, dfArtFlag, year)
    
    
    # We only need the last values because it does not change
    # In fact some tribal titles can become castle, city or temple
    # We can do better by indicating the changing year
    dfTitleTyp = pd.DataFrame(titleTyp)
  
    print("Year {} treated!".format(year))
    
#%%
    
# Column ordering
dfProvMod = dfProvMod[[provinceScope, "modifier", "year"]]
dfProvFlag = dfProvFlag[[provinceScope, "flag", "date", "year"]]
dfTitleFlag = dfTitleFlag[[titleScope, "flag", "date", "year"]]
dfCharFlag = dfCharFlag[[charScope, "flag", "date", "year"]]
dfArtFlag = dfArtFlag[[artScope, "flag", "date", "year"]]
artColumnOrder.insert(0, artScope)
dfArtStats = dfArtStats[artColumnOrder]
        
#%%

# TODO : update the files instead of create them
dfProvVar.to_csv(targetDir + savePrefix + "ProvinceVariables.csv", index=False)
dfProvMod.to_csv(targetDir + savePrefix + "ProvinceModifiers.csv", index=False)
dfProvFlag.to_csv(targetDir + savePrefix + "ProvinceFlags.csv", index=False)
dfTitleVar.to_csv(targetDir + savePrefix + "TitleVariables.csv", index=False)
dfTitleFlag.to_csv(targetDir + savePrefix + "TitleFlags.csv", index=False)
dfTitleTyp.to_csv(targetDir + savePrefix + "TitleTypes.csv", index=False)
dfCharStats.to_csv(targetDir + savePrefix + "CharacterStats.csv", index=False,
                   encoding='utf-8')
dfCharFlag.to_csv(targetDir + savePrefix + "CharacterFlags.csv", index=False)
dfArtStats.to_csv(targetDir + savePrefix + "ArtifactStats.csv", index=False)
dfArtFlag.to_csv(targetDir + savePrefix + "ArtifactFlags.csv", index=False)

