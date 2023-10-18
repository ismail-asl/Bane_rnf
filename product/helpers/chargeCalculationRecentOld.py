from product.models import ChargeHead, Charges, ChargeHeadRules
from product.serializers import ChargeHeadSerializer
import math

# sub helping functions


def get_charge_head_rule_object(charge_head, dependent_value):
    charge_head_rule_objects = ChargeHeadRules.objects.filter(head=charge_head).all()
    if len(charge_head_rule_objects)>0:
        charge_head_rule_object = None
        for rule in charge_head_rule_objects:
            if rule.min <= dependent_value and rule.max >= dependent_value:
                charge_head_rule_object = rule
                break
        return charge_head_rule_object
    else:
        return None

# Independent functions for each calculation scenario

def calculate_per_unit_no_rules(charge_head, parameter_value, flight_type): # using for 1
    if charge_head.value:
        charge_object = Charges.objects.filter(based_on='head', base=charge_head.id).first()
        if charge_object:
            charge_unit = math.ceil(float(parameter_value) / float(charge_head.value))
            charge_value_per_unit = float(charge_object.local) if flight_type == 'local' else float(charge_object.international)
            charge = charge_unit * charge_value_per_unit
            return charge
        else:
            return None
    return None

def calculate_per_unit_with_rules(charge_head, request_data): # using for 2+3
    parameter_value = request_data['parameter_value']
    flight_mtow = request_data['flight_mtow']
    flight_type = request_data['flight_type']
    final_charge = 0
    independent_charge = 0

    if charge_head.value:
        charge_head_rule_object = get_charge_head_rule_object(charge_head, flight_mtow)
        if charge_head_rule_object:
            charge_object = Charges.objects.filter(based_on='rules', base=charge_head_rule_object.id).first()
            if charge_object:
                charge_unit = math.ceil(float(parameter_value) / float(charge_head.value))
                charge_value_per_unit = float(charge_object.local) if flight_type == 'local' else float(charge_object.international)

                if charge_head.max_value != None and charge_head.max_value != "NULL":
                    if float(charge_head.max_value) <= charge_unit:
                        request_data['parameter_value'] = charge_unit - float(charge_head.max_value)
                        independent_charge = float(charge_head.max_value) * charge_value_per_unit
                    else:
                        independent_charge = charge_unit * charge_value_per_unit
                        request_data['parameter_value'] = 0
                else:
                    independent_charge = charge_unit * charge_value_per_unit


    final_charge = independent_charge

    return final_charge

def calculate_fixed(charge_head, request_data): # using for rules 4
    flight_mtow = request_data['flight_mtow']
    parameter_value = request_data['parameter_value']
    charge_head_rule_object = get_charge_head_rule_object(charge_head, flight_mtow)
    if charge_head_rule_object:
        charge_object = Charges.objects.filter(based_on='rules', base=charge_head_rule_object.id).first()
        if charge_object:
            if charge_head.unit_labels != "NULL" and charge_head.unit_labels is not None:
                if charge_head.unit_labels == "Hour":
                    charge_unit = math.ceil(float(parameter_value) / float(charge_head.value))
                elif charge_head.unit_labels == "KG":
                    charge_unit = math.ceil(float(flight_mtow) / float(charge_head.value))
            else:
                charge_unit = 1

            charge_value_per_unit = float(charge_object.local) if request_data['flight_type'] == 'local' else float(charge_object.international)
            return charge_unit * charge_value_per_unit
    return 0

def calculate_in_percentage_no_rules(charge_head, request_data): # using for rules 5+6
    if charge_head.static_percentage:
        parent_charge = calculating_charge(charge_head.parent, request_data)

        if charge_head.value!="NULL"  and charge_head.value!=None:
            charge = (float((parent_charge * float(charge_head.static_percentage))/100)) * (math.ceil(float(request_data['parameter_value']) / float(charge_head.value)))
        else:
            charge = (float((parent_charge * float(charge_head.static_percentage))/100))

        if charge_head.min_static_cost!="NULL" and charge_head.min_static_cost!= None and charge < float(charge_head.min_static_cost):
            charge = float(charge_head.min_static_cost)
        return charge
    return 0


def calculate_in_percentage_with_rules(charge_head, request_data): # using for rules 7
    flight_mtow = request_data['flight_mtow']
    parameter_value = request_data['parameter_value']
    charge_head_rule_object = get_charge_head_rule_object(charge_head, flight_mtow) if (charge_head.unit_labels=="NULL" or charge_head.unit_labels==None or charge_head.unit_labels!="Hour") else get_charge_head_rule_object(charge_head, parameter_value)
    if charge_head_rule_object:
        charge_object = Charges.objects.filter(based_on='rules', base=charge_head_rule_object.id).first()
        if charge_object:
            print('charge_object',charge_object)
            return 0
        else:
            return 0
            #incomplete for not knowing actual rules
    return 0


# Common function to decide which independent function to call

def calculating_charge(charge_head, request_data):

    # serializedHead = ChargeHeadSerializer(charge_head, many=False)
    # print('serializedHead',serializedHead.data)

    if charge_head.head_value_type == 'per_unit' and charge_head.has_rules == 0 and charge_head.value:  #working for rules 1
        return calculate_per_unit_no_rules(charge_head, request_data['parameter_value'], request_data['flight_type'])

    if charge_head.head_value_type == 'per_unit' and charge_head.has_rules == 1 and charge_head.value!="NULL" and charge_head.value!=None:  #working for rules 2+3
        return calculate_per_unit_with_rules(charge_head, request_data)

    if charge_head.head_value_type == 'fixed' and charge_head.has_rules == 1 and charge_head.value:
        return calculate_fixed(charge_head, request_data)

    if charge_head.head_value_type == 'in_percentage' and charge_head.has_rules == 0 and charge_head.static_percentage:  #working for rules 5+6
        return calculate_in_percentage_no_rules(charge_head, request_data)

    if charge_head.head_value_type == 'in_percentage' and charge_head.has_rules == 1:
        return calculate_in_percentage_with_rules(charge_head, request_data)

    else:
        return None





def calculated_charge():

    # #for embarkation_fees

    # request_data = {
    #     "head_code": "embarkation_fees",
    #     "flight_mtow": 5000,
    #     "parameter_value": 20, # mainly in 
    #     "flight_type": "international", # local/international
    #     "sub_charges": None
    # }


    # #for landing

    # request_data = {
    #     "head_code": "landing",
    #     "flight_mtow": 5000,
    #     "parameter_value": 30,
    #     "flight_type": "local", # local/international

    #     "sub_charges": {
    #     "off_time_landing_takeoff": True,
    #     "training_purpose_discount": True,
    #     "test_flight_discount": True,
    #     "parking_charge": True, 
    #     "hanger_charge": True,
    #     "security_others_international": True,
    #     "security_others_local": True
    #     }
    # }

    #for boarding_bridge_charge

    request_data = {
        "head_code": "boarding_bridge_charge",
        "flight_mtow": 5000,
        "parameter_value": 70,
        "flight_type": "international", # local/international

        "sub_charges": {
            "boarding_bridge_above_2hour_charge": True,
            "discount_charge_frequent_boarding_bridge": True,
	    }
    }

    #for navigation_charge

    # request_data = {
    #     "head_code": "navigation_charge",
    #     "flight_mtow": 5000,
    #     "parameter_value": 20, # mainly in 
    #     "flight_type": "international", # local/international
    #     "sub_charges": None
    # }

    response_data = {
        "head_code": request_data['head_code'],
        "sub_charges": {},
        "total_charge": 0
    }

    charge_head = ChargeHead.objects.filter(head_code=request_data['head_code']).first()

    if charge_head:
        charge_heads_charge_value = calculating_charge(charge_head, request_data)
        response_data['head_code_charge'] = charge_heads_charge_value
        response_data['total_charge'] += charge_heads_charge_value


        # child charge heads value

        childChargeHeads = charge_head.childChargeHeads.all()

        if len(childChargeHeads)>0:
            child_head_code_list = []

            for child in childChargeHeads:
                response_data['sub_charges'][child.head_code] = 0
                child_head_code_list.append(response_data['sub_charges'][child.head_code])
            if request_data['sub_charges']:
                for sub_key in request_data['sub_charges']:
                    if request_data['sub_charges'][sub_key]:
                        sub_charge_head = charge_head.childChargeHeads.filter(head_code=sub_key).first()
                        if sub_charge_head:
                            res = calculating_charge(sub_charge_head, request_data)
                            response_data['sub_charges'][sub_key] = res

                            if sub_charge_head.perform=="discount":
                                response_data['total_charge'] -= res
                            else:
                                response_data['total_charge'] += float(res)

                        #calculate charge and put it in response data
        return response_data