import app
import os, datetime

from threading import Timer, Lock

from model_reply import maindef

from crawl_worker.AgodaCrawler import agoda
from crawl_worker.BookingCrawler import bookingClient, booking
from crawl_worker.BurrpCrawler import burrp
from crawl_worker.DineoutCrawler import dineOut
from crawl_worker.EveningFlavorCrawler import eveningFlavor
from crawl_worker.FoodpandaCrawler import foodpanda
from crawl_worker.GoogleCrawler import googleReview
from crawl_worker.HolidayIqCrawler import holidayIQClient, holidayIQ
from crawl_worker.MakeMyTripCrawler import makemytrip
from crawl_worker.HotelsCrawler import hotels
from crawl_worker.GoibbiboCrawler import goibibo
from crawl_worker.ExpediaCrawler import expedia
from crawl_worker.TripAdvisorCrawler import tripadvisor
from crawl_worker.MouthshutCrawler import mouthshut
from crawl_worker.ZomatoCrawler import zomato

from classifier.HotelClassifier import hotelClassifier
from classifier.RestaurantClassifier import restaurantClassifier


def propertyData(custom=None):
    try:
        property_Data = list(app.PROPERTY_COLLECTION.find({"Status": "Active"}))
        propertyList = list(set([x["propertyName"] + "," + x["Place"] for x in property_Data]))
        property_Hotel = list(
            app.PROPERTY_COLLECTION.find({"Status": "Active", "For": "Hotel", "type": "Customer"}))
        property_Restaurant = list(
            app.PROPERTY_COLLECTION.find(
                {"Status": "Active", "For": "Restaurant", "type": "Customer"}))
        return {"property_Data": property_Data, "propertyList": propertyList,
                "property_Hotel": property_Hotel, "property_Restaurant": property_Restaurant}
    except Exception as e:
        print(e)
        return {"property_Data": [], "propertyList": [], "property_Hotel": [], "property_Restaurant": []}


def crawl():
    review_datas = propertyData()
    if not os.path.exists(os.path.join(app.DATA_DIR, str(datetime.datetime.today().date()))):
        os.makedirs(os.path.join(app.DATA_DIR, str(datetime.datetime.today().date()), 'hotel'))
        os.makedirs(os.path.join(app.DATA_DIR, str(datetime.datetime.today().date()), 'restaurant'))
    # review_datas['property_Hotel'] +
    review_datas = review_datas['property_Restaurant'] + review_datas['property_Hotel']
    for review_data in review_datas:
        if review_data is not None:
            status = None
            log_data = {}
            try:
                # prop = review_data["property"]
                # propName = prop.split(",")[0]
                # propLocation = prop.split(",")[1]
                # cData = list(app.PROPERTY_COLLECTION.find(
                # {"source": review_data["source"], "propertyName": propName, "Place": propLocation}))
                cData = [review_data]
                if review_data["source"] == "TripAdvisor":
                    status = tripadvisor(cData)
                    log_data["status"] = status
                elif review_data["source"] == "MakeMyTrip":
                    status = makemytrip(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Goibibo":
                    status = goibibo(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Booking":
                    if cData[0]["type"] == "Customer":
                        status = bookingClient(cData)
                    else:
                        status = booking(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Expedia":
                    status = expedia(cData)
                    log_data["status"] = status
                elif review_data["source"] == "GoogleReview":
                    status = googleReview(cData)
                    log_data["status"] = status
                elif review_data["source"] == "HolidayIQ":
                    if cData[0]["type"] == "Customer":
                        status = holidayIQClient(cData)
                    else:
                        status = holidayIQ(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Agoda":
                    status = agoda(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Zomato":
                    status = zomato(cData)
                    log_data["status"] = status
                elif review_data["source"] == "EveningFlavors":
                    status = eveningFlavor(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Dineout":
                    status = dineOut(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Mouthshut":
                    status = mouthshut(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Burrp":
                    status = burrp(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Foodpanda":
                    status = foodpanda(cData)
                    log_data["status"] = status
                elif review_data["source"] == "Hotels":
                    status = hotels(cData)
                    log_data["status"] = status
            except Exception as e:
                print(e)
                status = 'e - %s' % e
            if status is not None:
                print(status)


def classify(path, for_type):
    status = "It is not POST Request"
    dict = {}
    for_type = 'sasd'
    s = {'filePath': path}
    if for_type == "Hotel":
        status = hotelClassifier(filter)
    else:
        status = restaurantClassifier(s)
    dict["status"] = status
    return status


def crawl_classify():
    print('Crawl Classify started')
    crawl()
    # str(datetime.datetime.today().date())
    files = os.listdir(os.path.join(os.getcwd(), 'data', str(datetime.datetime.today().date()), 'restaurant'))
    for i in files:
        print(
            classify(os.path.join(os.getcwd(), 'data', str(datetime.datetime.today().date()), 'restaurant', i), 'asd'))

    files = os.listdir(os.path.join(os.getcwd(), 'data', str(datetime.datetime.today().date()), 'restaurant'))
    for i in files:
        print(
            classify(os.path.join(os.getcwd(), 'data', str(datetime.datetime.today().date()), 'restaurant', i),
                     'hotel'))


class Periodic(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self.stopped:
            self.stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self._lock.release()

    def _run(self):
        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


if __name__ == '__main__':

    a = Periodic(60 * 60 * 24 * 7, crawl_classify)
    b = Periodic(60 * 60 * 24, maindef)
