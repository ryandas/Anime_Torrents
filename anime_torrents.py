import requests, random, argparse,csv, os, sys, re, time
from natsort import natsorted
from bs4 import BeautifulSoup

base_address="https://animetosho.org/"
watched = -1
headerfile = os.path.abspath("./Chrome.txt")

def random_ua(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)

def source(url):
    headers = {"User-Agent":random_ua(headerfile)}
    r=requests.get(url,headers=headers,timeout=5)
    if r.status_code == 200:
        return r.text
    if r.status_code == 503:
        print(r.status_code)
        return source(url)
    else:
        print(r.status_code) 

def sort_csv(filename,rev):
    csvfile=open(filename,'r')
    reader = csv.reader(csvfile)
    sortedlist = natsorted(reader)
    with open(filename, 'w') as f:
        fileWriter = csv.writer(f, delimiter=',')
        for row in sortedlist:
            fileWriter.writerow(row)
    csvfile.close()

def torrent_links(page):
    #print("\t"+page) # debug
    soup=BeautifulSoup(source(page), "html.parser")
    anchors = soup.findAll("a")
    title = soup.findAll("h2",{"id":"title"})
    try:
        episode_number = soup.findAll("td")[2].a.next_sibling.next_sibling.text.split()[1]
    except:
        episode_number = "-"
    #print(episode_number) # debug
    for anchor in anchors:
        if(anchor.text=="Torrent Download"):
            try:
                if(int(watched) >= int(episode_number)):
                    return
                else:
                    print("\tGetting "+page)
                    main_write.writerow({"episode_number":episode_number,"title":title[0].text,"torrent":anchor["href"]})
                    d_write.writerow({"episode_number":episode_number,"title":title[0].text,"torrent":anchor["href"]})
            except:
                special_write.writerow({"episode_number":episode_number,"title":title[0].text,"torrent":anchor["href"]})
                return
            

def link_finder(page,pattern):
    print(page)
    soup = BeautifulSoup(source(page), "html.parser")
    links = soup.findAll("div",{"class":"link"})
    res = re.compile("\[1080p\]")
    anomaly1 = re.compile("~")
    anomaly2 = re.compile("\[Unofficial Batch\]")
    for link in links:
        if(re.search(pattern, link.text)):
            if(re.search(res,link.text)):
                if(re.search(anomaly1, link.text)):
                    #print(link.a["href"],file=lfile) # debug
                    continue
                elif(re.search(anomaly2,link.text)):
                    continue
                else:
                    torrent_links(link.a["href"])

def pages_finder(anime_details,page_number,pattern):
    url="{address}?page={i}".format(address=anime_details["address"],i=page_number)
    #print(url) # debug
    soup = BeautifulSoup(source(url), "html.parser")
    date = soup.find("div",{"class":"home_list_datesep"})
    if date.text != "-":

        link_finder(url,pattern)
        pages_finder(anime_details,page_number+1,pattern)
    else:
        return

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--provider",dest="provider",help="<Name of Channel>")
    parser.add_argument("-s","--search",dest="search",help="<Name of Anime>")
    args = parser.parse_args()
    if(args.provider):
        pattern = re.compile("\["+args.provider+"\]")
    else:
        pattern = re.compile("\[Erai-raws\]")

    search_query=re.sub(" ","+",args.search)
    url = "{address}search?q={query}".format(address=base_address,query=search_query)
    print(url)

    soup = BeautifulSoup(source(url), "html.parser")

    series_set = set(soup.findAll("span",{"class":"serieslink"}))
    series_dict = dict()
    for num,series in enumerate(series_set):
        print(str(num) + " " + series.text + " : " + series.a["href"])
        series_dict.setdefault(num,series)

    i = int(input("Which anime : "))

    anime_details={
        "address": series_dict.get(i).a["href"],
        "title": series_dict.get(i).text,
    }

    try:
        os.mkdir(anime_details["title"])
    except OSError:
        print(anime_details["title"] + " directory aleady exists")
        os.chdir(anime_details["title"])
        csvfile = open("main.csv",'r')
        reader = csv.reader(csvfile)
        try:
            watched = next(reader)[0]
        except:
            watched = -1
        csvfile.close()
        os.chdir("../")

    os.chdir(anime_details["title"])

    fieldnames = ["episode_number","title","torrent"]

    download = open("to_download.csv",'w')
    main_csv = open("main.csv",'a')
    special = open("special.csv",'a')

    main_write = csv.DictWriter(main_csv,fieldnames=fieldnames)
    d_write = csv.DictWriter(download,fieldnames=fieldnames)
    special_write = csv.DictWriter(special,fieldnames=fieldnames)

    pages_finder(anime_details,1,pattern)

    main_csv.close()
    download.close()
    special.close()

    sort_csv("main.csv",True)
    #sort_csv("to_download.csv",False
