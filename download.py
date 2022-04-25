import requests,csv,sys,os
os.chdir(sys.argv[1])
with open("to_download.csv") as file:
    os.chdir("/mnt/d/Downloads/Torrents")
    reader = csv.reader(file, delimiter=',')
    for row in reader:
        name = sys.argv[1].replace('/','-')+row[0]+".torrent"
        print("downloading "+name)
        open(name,"wb").write(requests.get(row[2]).content)
