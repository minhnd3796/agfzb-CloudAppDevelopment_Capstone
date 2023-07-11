import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from ibm_watson import NaturalLanguageUnderstandingV1

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    # json_obj = json_payload["review"]
    print(kwargs)
    print("POST to {} ".format(url))
    try:
        response = requests.post(url, json=json_payload, params=kwargs)
    except:
        print("Something went wrong")
    print(response.json())
    return response


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["result"]
        # For each dealer object
        for dealer in dealers:
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_by_id_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["result"]
        # For each review object
        for review in reviews:
            review_obj = DealerReview(name=review["name"], dealership=review["dealership"], review=review["review"],
                                   purchase=review["purchase"], purchase_date=review["purchase_date"], car_make=review["car_make"],
                                   car_model=review["car_model"], car_year=review["car_year"], sentiment=analyze_review_sentiments(review["review"]))
            results.append(review_obj)
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    api_key = "uE0v7xQMCYP64Qz57aY61sWzRQMnXOXsm9vV-OZ_txKf"
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/cdd3259f-bd34-4b32-9d87-ec34b1b77ade"
    version = '2022-08-10'
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(authenticator=authenticator, version=version)
    natural_language_understanding.set_service_url(url)
    return natural_language_understanding.analyze(text=text, features= Features(sentiment= SentimentOptions())).get_result()["sentiment"]["document"]["label"]
