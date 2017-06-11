from rest_framework import serializers

from tandlr.promotions.models import PromotionCode


class PromotionCodeV2Serializer(serializers.ModelSerializer):

    class Meta:
        model = PromotionCode
        fields = (
            'id',
            'expiration_date',
            'code',
            'is_active',
            'discount'
        )
