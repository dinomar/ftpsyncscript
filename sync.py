from pathlib import Path
from ftplib import FTP
import random
import json

ftp = FTP()

def main():
    # load config
    config = loadJsonFromFile("sync.conf")
    
    # connect
    ftp.connect(config["host"], config["port"])
    ftp.login(config["credentials"]["username"], config["credentials"]["password"])
    
    # Iterate Sync Folders
    iterateSyncDirectories(config["folders"])

    ftp.quit()
    print("Sync complete! Exiting...")
    
def iterateSyncDirectories(folders):
    for syncFolder in folders:
        # Navigate to upload destination path
        for folder in splitDestPath(syncFolder["dest"]):
            navigateToFolder(folder)
        
        # Navigate to first dest folder
        navigateToFolder(syncFolder["source"].split('/')[-1])
        
        # Upload folder
        iterateDirectory(syncFolder["source"])

def iterateDirectory(directory):
    path = Path(directory)

    for p in path.iterdir():
        if p.is_file():
            # Upload
            checkFile(p)
        elif p.is_dir() and not str(p).startswith("."):
            # Change dir
            navigateToFolder(str(p).split('/')[-1])
            iterateDirectory(p)
            ftp.cwd("..")

def checkFile(p):
    # Get directory list
    dirList = []
    ftp.retrlines('LIST', dirList.append)
    
    for f in dirList:
        parts = f.split()
        fName = parts[8]
        fSize = parts[4]
        
        # Check file exists
        if fName == p.parts[-1] and int(fSize) == p.stat().st_size:
            # Skip uploading file
            #print("Skipping")
            return
        elif fName == p.parts[-1]:
            # File conflict. Rename local file.
            print("Conflict")
            newp = renameFileWithRandomStr(p)
            
            # Upload file
            upload(newp)
            return
    
    # Upload file
    upload(p)
        
def renameFileWithRandomStr(p):
    fParts = p.parts[-1].split('.')
    newFilename = fParts[0] + "-" + randomString(10)
    for i in range(1, len(fParts)): # -1
        newFilename += "." + fParts[i]
    return p.rename(newFilename)
    
    
def randomString(length):
    string = ""
    for i in range(length):
        string += str(random.randint(0, 9));
    return string

def upload(p):
    # Upload to server
    print("Uploading %s" % str(p))
    with open(str(p), 'rb') as f:
        ftp.storbinary("STOR %s" % str(p).split('/')[-1], f)
        

def navigateToFolder(folder):
    print("Navigating to %s" % folder)
    if not folder in ftp.nlst():
        ftp.mkd(folder)
    ftp.cwd(folder)

def splitDestPath(path):
    parts = path.split('/')
    while '' in parts:
        parts.remove('')
    return parts

def loadJsonFromFile(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def loadFromFile(filename):
    with open(filename, 'r') as f:
        return f.read()

if __name__ == "__main__":
    main()
 
