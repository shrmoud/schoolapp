# -*- coding: utf-8 -*-
import random
import string

from datetime import timedelta

from django import forms
from django.utils import timezone

from tandlr.promotions.models import BatchPromotionCode, PromotionCode


class BatchPromotionCodeForm(forms.ModelForm):
    """
    Form create Batch PromotionCode
    """
    number = forms.IntegerField(
        max_value=100,
        min_value=1
    )

    uses_per_user = forms.IntegerField(
        min_value=1
    )

    discount = forms.IntegerField(
        max_value=100
    )

    def clean_expiration_date(self):
        now = timezone.localtime(timezone.now()) + timedelta(minutes=15)
        if self.cleaned_data['expiration_date'] < now:
            raise forms.ValidationError(
                'The date "{}" is incorrect.'
                'The date should be greater or equal than today'.format(
                    self.cleaned_data['expiration_date'].date()
                )
            )
        return self.cleaned_data['expiration_date']

    def save(self, commit=True):
        instance = super(BatchPromotionCodeForm, self).save(commit=False)
        data = self.cleaned_data
        instance.expiration_date = data['expiration_date']
        instance.discount = data['discount']
        current_code_list = PromotionCode.objects.all().values('code')

        code_list = self._create_code(current_code_list, [], data['number'])
        #
        # Create PromotionCode
        #
        for code in code_list:
            PromotionCode.objects.create(
                code=code,
                uses_per_user=data['uses_per_user'],
                discount=data['discount'],
                expiration_date=data['expiration_date']
            )
        if commit:
            instance.save()
        return instance

    def _create_code(self, current_code_list, code_list, limit):
        if len(code_list) >= limit:
            return code_list
        else:
            #
            # Create code of ten digits
            #
            code = ''.join([
                random.choice(
                    string.ascii_letters + string.digits
                ) for n in xrange(10)
            ])

            if code not in current_code_list and code not in code_list:
                code_list.append(code)

            return self._create_code(current_code_list, code_list, limit)

    class Meta:
        fields = ['expiration_date', 'discount', 'number', 'uses_per_user']
        model = BatchPromotionCode
