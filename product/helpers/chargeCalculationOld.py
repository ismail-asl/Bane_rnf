from product.models import ChargeHead, Charges, ChargeHeadRules
from product.serializers import ChargeHeadSerializer
import math

# sub helping functions


def get_charge_head_rule_object(charge_head, flight_mtow):
    charge_head_rule_objects = ChargeHeadRules.objects.filter(head=charge_head).all()
    if len(charge_head_rule_objects)>0:
        charge_head_rule_object = None
        for rule in charge_head_rule_objects:
            if rule.min <= flight_mtow and rule.max >= flight_mtow:
                charge_head_rule_object = rule
                break
        return charge_head_rule_object
    else:
        return None

# Independent functions for each calculation scenario

def calculate_per_unit_no_rules(charge_head, parameter_value, flight_type):
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

def calculate_per_unit_with_rules(charge_head, **kwargs):
    parameter_value = kwargs.get('parameter_value')
    flight_mtow = kwargs.get('flight_mtow')
    flight_type = kwargs.get('flight_type')
    final_charge = 0
    parent_charge = 0
    independent_charge = 0
    rest_unit = kwargs.get('parameter_value')

    if charge_head.parent_id:
        parent_head = ChargeHead.objects.filter(id=charge_head.parent_id).first()
        parent_charge_head_rule_object = get_charge_head_rule_object(parent_head, parameter_value)

        if parent_charge_head_rule_object:
            parent_charge_object = Charges.objects.filter(based_on='rules', base=charge_head_rule_object.id).first()
            if parent_charge_object:
                charge_unit = math.ceil(float(parameter_value) / float(parent_head.value))
                parent_charge_value_per_unit = float(parent_charge_object.local) if flight_type == 'local' else float(parent_charge_object.international)
                
                if parent_head.max_value != None and parent_head.max_value != "NULL":
                    if float(parent_head.max_value) <= charge_unit:
                        parent_charge += (parent_charge_value_per_unit * float(parent_head.max_value))
                        rest_unit = charge_unit - float(parent_head.max_value)
                    else:
                        parent_charge += (parent_charge_value_per_unit * charge_unit)


    if charge_head.value:
        charge_head_rule_object = get_charge_head_rule_object(charge_head, flight_mtow)
        if charge_head_rule_object:
            charge_object = Charges.objects.filter(based_on='rules', base=charge_head_rule_object.id).first()
            if charge_object:
                print('charge_object',charge_object)
                charge_unit = math.ceil(float(rest_unit) / float(charge_head.value))
                charge_value_per_unit = float(charge_object.local) if flight_type == 'local' else float(charge_object.international)

                if charge_head.max_value != None and charge_head.max_value != "NULL":
                    if float(charge_head.max_value) <= charge_unit:
                        independent_charge = float(charge_head.max_value) * charge_value_per_unit
                    else:
                        independent_charge = charge_unit * charge_value_per_unit
                else:
                    independent_charge = charge_unit * charge_value_per_unit


    final_charge = parent_charge + independent_charge

    return final_charge

def calculate_fixed(charge_head, **kwargs):
    if charge_head.value:
        charge = float(charge_head.value)
        return charge, kwargs.get('currency_type')
    return None, None

def calculate_in_percentage_no_rules(charge_head, **kwargs):
    if kwargs.get('static_percentage'):
        charge = float(kwargs.get('static_percentage'))
        if kwargs.get('min_static_cost') and charge < kwargs.get('min_static_cost'):
            charge = kwargs.get('min_static_cost')
        return charge, kwargs.get('currency_type')
    return None, None

def calculate_in_percentage_with_rules(charge_head, **kwargs):
    if kwargs.get('static_percentage') and kwargs.get('value') and kwargs.get('parent_value'):
        charge = (float(kwargs.get('static_percentage')) / 100) * (float(kwargs.get('value')) + float(kwargs.get('parent_value')))
        charge *= float(kwargs.get('quantity'))
        return charge, kwargs.get('currency_type')
    return None, None

def calculate_in_percentage_with_static_cost(charge_head, **kwargs):
    if kwargs.get('static_cost'):
        charge = float(kwargs.get('static_cost'))
        return charge, kwargs.get('currency_type')
    return None, None

# Common function to decide which independent function to call

def calculating_charge(charge_head, **kwargs):
    serializedHead = ChargeHeadSerializer(charge_head, many=False)
    if charge_head.head_value_type == 'per_unit' and charge_head.has_rules == 0 and charge_head.value:
        return calculate_per_unit_no_rules(charge_head, kwargs.get('parameter_value'), kwargs.get('flight_type'))

    elif charge_head.head_value_type == 'per_unit' and charge_head.has_rules == 1 and charge_head.value:
        return calculate_per_unit_with_rules(charge_head, **kwargs)

    elif charge_head.head_value_type == 'fixed' and charge_head.has_rules == 1 and charge_head.value:
        return calculate_fixed(charge_head, **kwargs)

    elif charge_head.head_value_type == 'in_percentage' and charge_head.has_rules == 0 and charge_head.static_percentage:
        return calculate_in_percentage_no_rules(charge_head, **kwargs)

    elif charge_head.head_value_type == 'in_percentage' and charge_head.has_rules == 0 and charge_head.value:
        return calculate_in_percentage_with_rules(charge_head, **kwargs)

    elif charge_head.head_value_type == 'in_percentage' and charge_head.has_rules == 1 and charge_head.static_cost:
        return calculate_in_percentage_with_static_cost(charge_head, **kwargs)

    else:
        return None, None  # Handle other cases

def calculated_charge():
    head_code = "boarding_bridge_charge"
    parameter_value = 3
    flight_mtow = 5000
    flight_type = "international" # local/international
    currency_type = "local"
    charge_head = ChargeHead.objects.filter(head_code=head_code).first()
    return calculating_charge(charge_head, parameter_value=parameter_value, flight_mtow=flight_mtow, flight_type=flight_type)