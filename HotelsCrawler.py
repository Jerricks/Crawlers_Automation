import time, requests , os , datetime
from bs4 import BeautifulSoup
import pandas as pd
import app


def hotels(filter):
    htm = requests.get(filter[0]["url1"])
    soup = BeautifulSoup(htm.text.encode('utf-8'), "lxml")
    hotelName = filter[0]["propertyName"]
    hotelPlace = filter[0]["Place"]
    mainDiv = soup.find("div", class_="brand-review-wrapper")
    div = mainDiv.find_all("div", class_="review-card")
    data = []
    for d in div:
        date = d.find("span", class_="date").getText()
        pattern = '%b %d, %Y'
        date = int(time.mktime(time.strptime(date, pattern)))
        if date != "":
            if filter[0]["lastCrawl"] != "" and date <= int(filter[0]["lastCrawl"]):
                if data:
                    dtaFrm = pd.DataFrame(data)
                    print(dtaFrm)
                    if not dtaFrm.empty:
                        app.PROPERTY_COLLECTION.update({"_id": filter[0]["_id"]},
                                                                 {"$set": {"lastCrawl": round(time.time())}})
                    filename = (
                        str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(
                            filter[0]["source"]) + "_" + str(
                            time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
                    with open(os.path.join(os.getcwd() , 'data' , str(datetime.datetime.today().date()) , 'hotel' , filename), 'a') as f:
                        dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
                    status = 's - %d' % len(data)
                    print("1-Crawled")
                    return status
                else:
                    status = 's - %s' % 'updated'
                    print("2-Already Updated !!")
                    return status
        rating = d["data-review-rating"]
        rname = d.find_next("div", class_="review-card-meta-reviewer").getText()
        rimg = filter[0]["Logo"]
        comment = d.find("blockquote", class_="expandable-content").getText()
        if comment == "":
            comment = "No Comment"
        data.append(
            {"Name": hotelName, "Place": hotelPlace, "Date": date, "Rname": rname,
             "Rimg": rimg, "Comment": comment, "ReviewID": "",
             "Rating": rating, "Channel": filter[0]["source"], "icon": "/static/images/hotels.png",
             "Replied": "R2", "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"], "City": filter[0]["City"],
             "State": filter[0]["State"], "Country": filter[0]["Country"]})
    dtaFrm = pd.DataFrame(data)
    if not dtaFrm.empty:
        app.PROPERTY_COLLECTION.update({"_id": filter[0]["_id"]}, {"$set": {"lastCrawl": round(time.time())}})
    filename = (
        str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(filter[0]["source"]) + "_" + str(
            time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
    with open(os.path.join(os.getcwd() , 'data' , str(datetime.datetime.today().date()) , 'hotel' , filename), 'a') as f:
        dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
    status = 's - %d' % len(data)
    print("3-Crawled")
    return status
