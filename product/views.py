from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from .models import *
from .serializers import ChargeHeadSerializer
from .helpers.chargeCalculation import calculate_total_charge

class ProductView(APIView):

    renderer_classes = [JSONRenderer]

    def get(self,request):
        data = {
            "data": ""
        }
        return Response(data, status=status.HTTP_200_OK)



# Example usage for different scenarios

# Example 1: For "embarkation_fees"
request_data1 = {
    "head_code": "embarkation_fees",
    "flight_mtow": 5000,
    "parameter_value": 20,
    "flight_type": "international",
    "sub_charges": None
}

# response_data1 = calculate_total_charge(request_data1)
# print("Total Charge for", request_data1['head_code'], ":", response_data1['total_charge'])

# Example 2: For "landing"
request_data2 = {
    "head_code": "landing",
    "flight_mtow": 15000,
    "parameter_value": 30,
    "flight_type": "local",
    "sub_charges": {
        "off_time_landing_takeoff": True,
        "training_purpose_discount": True,
        "test_flight_discount": True,
        "parking_charge": True,
        "hanger_charge": True,
        "security_others_international": True,
        "security_others_local": True
    }
}

# response_data2 = calculate_total_charge(request_data2)
# print("Total Charge for", request_data2['head_code'], ":", response_data2['total_charge'])

# Example 3: For "boarding_bridge_charge"
request_data3 = {
    "head_code": "boarding_bridge_charge",
    "flight_mtow": 5000,
    "parameter_value": 70,
    "flight_type": "international",
    "sub_charges": {
        "boarding_bridge_above_2hour_charge": True,
        "discount_charge_frequent_boarding_bridge": True,
    }
}

# response_data3 = calculate_total_charge(request_data3)
# print("Total Charge for", request_data3['head_code'], ":", response_data3['total_charge'])

# Example 4: For "navigation_charge"
request_data4 = {
    "head_code": "navigation_charge",
    "flight_mtow": 5000,
    "parameter_value": 20,
    "flight_type": "international",
    "sub_charges": None
}

# response_data4 = calculate_total_charge(request_data4)
# print("Total Charge for", request_data4['head_code'], ":", response_data4['total_charge'])



class ChargeCalculation(APIView):
    renderer_classes = [JSONRenderer]

    def get(self,request):

        # heads = ChargeHead.objects.all()
        # headSerializer = ChargeHeadSerializer(heads, many=True)

        # request_data={
        #     "request_data1": request_data1,
        #     "request_data2": request_data2,
        #     "request_data3": request_data3,
        #     "request_data4": request_data4,
        # }
        

        data = [
            {
            "request_data1": request_data1,
            "response_data1": calculate_total_charge(request_data1)},
            {
            "request_data2": request_data2,
            "response_data2": calculate_total_charge(request_data2)},
            {
            "request_data3": request_data3,
            "response_data3": calculate_total_charge(request_data3)},
            {
            "request_data4": request_data4,
            "response_data4": calculate_total_charge(request_data4)}]

        return Response(data, status=status.HTTP_200_OK)








































# import csv
# import os
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework import status
# from .serializers import ChargeHeadSerializer
# from .models import *

    
# class ChargeHeadUpload(APIView):
#     def post(self, request, *args, **kwargs):

#         # Define the path to your CSV file in the project folder
#         csv_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'charge_head_rules.csv')

#         try:
#             # Read the CSV file and create or update ChargeHead objects
#             created_objects = []
#             with open(csv_file_path, 'r') as file:
#                 csv_reader = csv.DictReader(file)
#                 for row in csv_reader:
#                     print('row', row)
#                     # Extract the provided ID from the CSV
#                     provided_id = row.get('id')
#                     if provided_id:
#                         # Try to get an existing object or create a new one with the provided ID
#                         charge_head, created = ChargeHeadRules.objects.get_or_create(pk=provided_id)
#                         serializer = ChargeHeadSerializer(charge_head, data=row, partial=True)
#                     else:
#                         serializer = ChargeHeadSerializer(data=row)

#                     if serializer.is_valid():
#                         serializer.save()
#                         created_objects.append(serializer.data)
#                     else:
#                         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#             return Response({'message': 'CSV data successfully imported', 'created_objects': created_objects}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
