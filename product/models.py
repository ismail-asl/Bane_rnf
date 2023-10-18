from django.db import models

class ChargeHead(models.Model):
    parent = models.ForeignKey('self', related_name="childChargeHeads", on_delete=models.RESTRICT, null=True, blank=True)
    name = models.CharField(max_length=255)
    head_code = models.CharField(max_length=255,unique=True,null=True)
    head_value_type = models.CharField(max_length=255, null=True, blank=True)
    has_rules = models.BooleanField(null=True,blank=True,default=False)
    unit_labels = models.CharField(max_length=150,null=True)
    value = models.CharField(max_length=50)
    currency_type = models.CharField(max_length=255, blank=True, null=True)
    perform=models.CharField(max_length=100, blank=True,null=True)
    max_value=models.CharField(max_length=100, blank=True,null=True)
    static_percentage = models.CharField(max_length=255, blank=True, null=True)
    min_static_cost = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.head_code


class Charges(models.Model):
    based_on = models.CharField(max_length=100, null=True, blank=True)
    base = models.PositiveBigIntegerField(null=True, blank=True)
    any_condition = models.CharField(max_length=150, null=True, blank=True)
    local = models.FloatField(null=True, default=0)
    international = models.FloatField(null=True, default=0)
    minimum_cost = models.FloatField(null=True, default=0)
    static_cost = models.FloatField(null=True, default=0)


class ChargeHeadRules(models.Model):
    head = models.ForeignKey(ChargeHead, related_name="chargeHeadRules", on_delete=models.DO_NOTHING, null=False, blank=False)
    min = models.FloatField()
    max = models.FloatField(null=True)
