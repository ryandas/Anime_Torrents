import requests, random, csv, os, sys, re, operator,time
from bs4 import BeautifulSoup

base_address="https://animetosho.org/"
watched = -1

def random_ua(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)

def source(url):
    headers = {"User-Agent":random_ua("/home/ryan/repos/dotfiles/scripts/anime_torrents/Chrome.txt")}
    r=requests.get(url,headers=headers,timeout=2)
    if r.status_code == 200:
        return r.text
    if r.status_code == 503:
        print(r.status_code)
        source(url)
    else:
        print(r.status_code) 


def sort_csv(filename,rev):
    csvfile=open(filename,'r')
    reader = csv.reader(csvfile)
    sortedlist = sorted(reader, key=operator.itemgetter(1), reverse=rev)
    with open(filename, 'a') as f:
        fileWriter = csv.writer(f, delimiter=',')
        for row in sortedlist:
            fileWriter.writerow(row)
    csvfile.close()

def torrent_links(page):
    #print("\t"+page)
    soup=BeautifulSoup(source(page), "html.parser")
    anchors = soup.findAll("a")
    title = soup.findAll("h2",{"id":"title"})
    episode_number = soup.findAll("td")[2].a.next_sibling.next_sibling.text.split()[1]
    #print(episode_number)
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
            

def link_finder(page):
    print(page)
    soup = BeautifulSoup(source(page), "html.parser")
    links = soup.findAll("div",{"class":"link"})
    #pattern1 = re.compile("\[Erai-raws\]")
    pattern1 = re.compile("\[HorribleSubs\]")
    pattern2 = re.compile("\[1080p\]")
    pattern3 = re.compile("~")
    pattern4 = re.compile("\[Unofficial Batch\]")
    for link in links:
        if(re.search(pattern1, link.text)):
            if(re.search(pattern2,link.text)):
                if(re.search(pattern3, link.text)):
                    #print(link.a["href"],file=lfile)
                    continue
                elif(re.search(pattern4,link.text)):
                    continue
                else:
                    torrent_links(link.a["href"])

def pages_finder(anime_details,page_number):
    url="{address}?page={i}".format(address=anime_details["address"],i=page_number)
    #print(url)
    soup = BeautifulSoup(source(url), "html.parser")
    date = soup.find("div",{"class":"home_list_datesep"})
    if date.text != "-":

        link_finder(url)
        pages_finder(anime_details,page_number+1)
    else:
        return

#if __name__ == "__main__":
search_query='+'.join(sys.argv[1:])
url = "{address}/search?q={query}".format(address=base_address,query=search_query)
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

pages_finder(anime_details,1)

main_csv.close()
download.close()
special.close()

sort_csv("main.csv",True)
#sort_csv("to_download.csv",False
