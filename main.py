from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError
import requests
import urllib.request

def create_log_file(username, old_logs, new_logs):
    if old_logs != None:
        #combine two logs
        new_logs.update(old_logs)
    f= open("log_{}.txt".format(username),"w+")

    for id in new_logs:
        f.write(str(id)+"\n")
    f.close
    print("created log-file")

def get_log(dir):
    ids = set(map(int, open(dir).read().split()))
    print("found log file")
    return ids
    # try:
    #     ids = set(int(open(dir).read().split()))
    #     print("found log file")
    #     return ids
    # except:
    #     print("no log file found")
    #     return None


def get_bs4_object(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        return None
    try:
        bs = BeautifulSoup(html.read(), 'html.parser')
        return bs
    except AttributeError as e:
        return None


def save_picture(url, name):
    bs = get_bs4_object(url)
    if bs == None:
        return
    else:
        picture = bs.find('img', class_='_1izoQ')
        if picture == None:
            print("no picture found")
        else:
            try:
                urllib.request.urlretrieve(picture["src"], name + ".png")
            except:
                print("no picture found")


def get_pictures(username, link, depth = 24, min_ratio=1.3, max_ratio=2, logs=None, dir = "", just_latest = False):
    i = 0
    new_logs = set()
    finished = False

    while(i < depth and not finished):
        if i + 24 < depth:
            url = link.format(username, i, 24)
        else:
            url = link.format(username, i, depth%24)
        
        json = requests.get(url).json()

        #falls es keine Bilder mehr gibt
        if(not json["hasMore"]):
            break
        try:
            deviations = json["results"]
            counter = 0
            for deviation in deviations:
                counter += 1
                # ka warum, dumme json Struktur
                deviation = deviation["deviation"]

                # schaut ob biler schon existieren
                if(logs != None):
                    if deviation["deviationId"] in logs:
                        if just_latest:
                            finished = True
                            break
                        continue
                print("Number: "+str(i + counter)+", Prozent: "+str(100 * (i + counter)/depth)+"%", end="\r", flush=True)
                
                # schaut ob ratio (width/height) passt
                if(deviation["media"]["types"][0]["w"]/deviation["media"]["types"][0]["h"] >= min_ratio and deviation["media"]["types"][0]["w"]/deviation["media"]["types"][0]["h"] <= max_ratio):
                    save_picture(deviation["url"], dir + str(deviation["deviationId"]))
                    new_logs.add(deviation["deviationId"])
        except:
            continue

        i += 24
    create_log_file(username, logs, new_logs)

usernames = ["NanoMortis"]
dir = "C:/Users/Lundralion/Pictures/wallpapers/"
depth = 100
#ratio = width/height
min_ratio = 1.3
max_ratio = 2

url = "https://www.deviantart.com/_napi/da-user-profile/api/gallery/contents?username={}&offset={}&limit={}&all_folder=true&mode=newest"


for username in usernames:
    logs = get_log("log_{}.txt".format(username))
    get_pictures(username, url, depth, min_ratio, max_ratio, logs, dir)
    print("finished")
