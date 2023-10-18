from product.models import ChargeHead, Charges, ChargeHeadRules
from product.serializers import ChargeHeadSerializer
import math

# Helper function to get a charge head rule object
def get_charge_head_rule_object(charge_head, dependent_value):
    charge_head_rule_objects = ChargeHeadRules.objects.filter(head=charge_head).all()
    if len(charge_head_rule_objects) > 0:
        for rule in charge_head_rule_objects:
            if rule.min <= dependent_value and rule.max >= dependent_value:
                return rule
    return None

# Function to calculate charge for "per_unit" type without rules
def calculate_per_unit_no_rules(charge_head, parameter_value, flight_type):
    if charge_head.value:
        charge_object = Charges.objects.filter(based_on='head', base=charge_head.id).first()
        if charge_object:
            charge_unit = math.ceil(float(parameter_value) / float(charge_head.value))
            charge_value_per_unit = float(charge_object.local) if flight_type == 'local' else float(charge_object.international)
            charge = charge_unit * charge_value_per_unit
            return charge
    return None

# Function to calculate charge for "per_unit" type with rules
def calculate_per_unit_with_rules(charge_head, request_data):
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
                if charge_head.unit_labels == "Hour":
                    charge_unit = math.ceil(float(parameter_value) / float(charge_head.value))
                if charge_head.unit_labels == "KG":
                    charge_unit = math.ceil(float(flight_mtow) / float(charge_head.value))

                charge_value_per_unit = float(charge_object.local) if flight_type == 'local' else float(charge_object.international)

                if charge_head.max_value is not None and charge_head.max_value != "NULL":
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

# Function to calculate charge for "fixed" type with rules
def calculate_fixed(charge_head, request_data):
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

# Function to calculate charge for "in_percentage" type without rules
def calculate_in_percentage_no_rules(charge_head, request_data):
    if charge_head.static_percentage:
        parent_charge = calculating_charge(charge_head.parent, request_data)
        # set logic for parking charge (if above 6 hours, then charge it) 
        if charge_head.value!="NULL" and charge_head.value!=None:
            if charge_head.head_code == "parking_charge":
                if float(request_data['parameter_value']) > 6:
                    charge = (float((parent_charge * float(charge_head.static_percentage)) / 100)) * (
                            math.ceil(float(request_data['parameter_value']) / float(charge_head.value))) # (percentage * unit)
                else:
                    charge = 0
            else:
                charge = (float((parent_charge * float(charge_head.static_percentage)) / 100)) * (
                        math.ceil(float(request_data['parameter_value']) / float(charge_head.value))) # (percentage * unit)
        else:
            charge = (float((parent_charge * float(charge_head.static_percentage)) / 100))

        if charge_head.min_static_cost!="NULL" and charge_head.min_static_cost is not None and charge < float(
                charge_head.min_static_cost):
            charge = float(charge_head.min_static_cost)
        return charge
    return 0

# Function to calculate charge for "in_percentage" type with rules
def calculate_in_percentage_with_rules(charge_head, request_data):
    flight_mtow = request_data['flight_mtow']
    parameter_value = request_data['parameter_value']
    charge_head_rule_object = get_charge_head_rule_object(charge_head, flight_mtow) if (
                charge_head.unit_labels == "NULL" or charge_head.unit_labels is None or charge_head.unit_labels != "Hour") else get_charge_head_rule_object(charge_head, parameter_value)
    
    if charge_head_rule_object:
        charge_object = Charges.objects.filter(based_on='rules', base=charge_head_rule_object.id).first()
        if charge_object:
            return charge_object
        else:
            return 0
    return 0

# Common function to decide which independent function to call
def calculating_charge(charge_head, request_data):
    if charge_head.head_value_type == 'per_unit' and charge_head.has_rules == 0 and charge_head.value:
        return calculate_per_unit_no_rules(charge_head, request_data['parameter_value'], request_data['flight_type'])

    if charge_head.head_value_type == 'per_unit' and charge_head.has_rules == 1 and charge_head.value !="NULL" and charge_head.value is not None:
        return calculate_per_unit_with_rules(charge_head, request_data)

    if charge_head.head_value_type == 'fixed' and charge_head.has_rules == 1:
        return calculate_fixed(charge_head, request_data)

    if charge_head.head_value_type == 'in_percentage' and charge_head.has_rules == 0 and charge_head.static_percentage:
        return calculate_in_percentage_no_rules(charge_head, request_data)

    if charge_head.head_value_type == 'in_percentage' and charge_head.has_rules == 1:
        return calculate_in_percentage_with_rules(charge_head, request_data)

    else:
        return None

# Function to calculate sub charges
def calculate_sub_charges(charge_head, request_data):
    sub_charges = {}
    total_charge = 0
    sub_charges_on_total = []

    # def addition_or_subtraction(sub_charge_head, res, total_charge):
    #     if sub_charge_head.perform == "discount":
    #         total_charge -= float(res)
    #     else:
    #         total_charge += float(res)

    if request_data['sub_charges']:
        for sub_key in request_data['sub_charges']:
            if request_data['sub_charges'][sub_key]:
                # sub_charge_head = charge_head.childChargeHeads.filter(head_code=sub_key).first()
                sub_charge_head = ChargeHead.objects.filter(head_code=sub_key).first()
                if sub_charge_head:
                    res = calculating_charge(sub_charge_head, request_data)
                    if isinstance(res, Charges):
                        sub_charges_on_total.append((sub_charge_head, res))
                    else:
                        sub_charges[sub_key] = res
                        if sub_charge_head.perform == "discount":
                            total_charge -= float(res)
                        else:
                            total_charge += float(res)

        if len(sub_charges_on_total)>0:
            for calc_on_total in sub_charges_on_total:
                sub_charge_head = calc_on_total[0]
                charge_obj = calc_on_total[1]
                if float(charge_obj.static_cost)>0:
                    res = float((total_charge * float((charge_obj.static_cost)) / 100))

                else:
                    percentg = float(charge_obj.local) if request_data['flight_type'] == 'local' else float(charge_obj.international)
                    res = float((total_charge * float((percentg)) / 100))

                sub_charges[sub_charge_head.head_code] = res
                if sub_charge_head.perform == "discount":
                    total_charge -= float(res)
                else:
                    total_charge += float(res)

    return sub_charges, total_charge

# Function to calculate the total charge
def calculate_total_charge(data):
    request_data = data.copy()
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

        sub_charges, total_charge = calculate_sub_charges(charge_head, request_data)
        response_data['sub_charges'] = sub_charges
        response_data['total_charge'] += total_charge

    return response_data
