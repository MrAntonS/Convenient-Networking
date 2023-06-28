import pickle
import os

def getDictFromPickleFile(filePath):
    if not checkFileExist(filePath): 
        dumpDictToPickleFile(dict(), filePath)
        return dict()
    with open(filePath, 'rb') as file:
        result_dict = pickle.load(file)
    return result_dict

def appendToPickleFile(var, filePath):
    data = getDictFromPickleFile(filePath)
    try:
        for keys in var:
            data[keys] = var[keys]
            print(data[keys])
        assert dumpDictToPickleFile(data, filePath) == True
    except:
        return False
    return True

def dumpDictToPickleFile(var, filePath):
    with open(filePath, 'wb') as file:
        try: pickle.dump(var, file)
        except: return False
    return True

def getEntryInDict(initDict, *keys):
    result = initDict
    for key in keys:
        result = result[key]
    return result

def checkFileExist(filePath):
    return os.path.exists(filePath)