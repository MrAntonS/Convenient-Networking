import pickle
import os

def getDictFromPickleFile(filePath):
    if not CheckFileExist(filePath): 
        DumpDictToPickleFile(dict(), filePath)
        return dict()
    with open(filePath, 'rb') as file:
        result_dict = pickle.load(file)
    return result_dict

def DumpDictToPickleFile(var, filePath):
    with open(filePath, 'wb') as file:
        try: pickle.dump(var, file)
        except: return False
    return True

def CheckFileExist(filePath):
    return os.path.exists()