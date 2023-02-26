from django.template import loader

from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
import json

# modules for ML app
from geopy.geocoders import Nominatim
import numpy as np
import pickle

import warnings
warnings.filterwarnings("ignore")

# Open the file in binary mode
lr_model = pickle.load(open('./model/LR_NYC_trainedM.sav','rb+'))



def predict_fare(year, hour, distance, passenger_count):
    fare = lr_model.predict([[year, hour, distance, passenger_count]])
    return fare


def distance(lat1, lon1, lat2, lon2):    
    p = 0.017453292519943295 # Pi/180
    a = 0.5 - np.cos((lat2 - lat1) * p)/2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    return 0.6213712 * 12742 * np.arcsin(np.sqrt(a)) # 2*R*asin...


def index(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            response = json.load(request)
            # passenger_name = response.get('passenger_name')
            passenger_count = response.get('passenger_count')
            pickup_inp = response.get('pickup_inp')
            dropoff_inp = response.get('dropoff_inp')

            yr_inp = response.get('yr')
            hr_inp = response.get('hrs')


            # find long and lat
            locator = Nominatim(user_agent='locator')

            pickup_location = locator.geocode(pickup_inp)
            dropoff_location = locator.geocode(dropoff_inp)

            pickup_lat = pickup_location.latitude
            pickup_long = pickup_location.longitude


            dropoff_lat = dropoff_location.latitude
            dropoff_long = dropoff_location.longitude


            loc_dis = distance(pickup_lat, pickup_long, dropoff_lat, dropoff_long)

            fare = predict_fare(yr_inp, hr_inp, loc_dis, passenger_count)[0][0]
            print(loc_dis, fare)

            # fare_amount(x) ~ [year, hour, distance, passenger_count]

            return JsonResponse({'status': "ok", 'fare':fare})        
        return JsonResponse({'status': 'Invalid request'}, status=400)
        

    return render(request, "index.html")


