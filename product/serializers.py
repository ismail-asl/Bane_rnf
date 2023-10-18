from rest_framework import serializers
from .models import *

class ChargeHeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChargeHead
        fields = '__all__'