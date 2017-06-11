# -*- conding: utf-8 -*-
from tandlr.api.v2.routers import router
from tandlr.core.api import mixins
from tandlr.core.api.viewsets import GenericViewSet

from .models import University
from .serializers import UniversityV2Serializers


class UniversityViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet):

    serializer_class = UniversityV2Serializers
    list_serializer_class = UniversityV2Serializers
    retrieve_serializer_class = UniversityV2Serializers

    def get_queryset(self):
        q = self.request.query_params.get('q', None)

        queryset = University.objects.filter(is_active=True)
        if q:
            return queryset.filter(name__icontains=q)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Returns a list of universities
        ---
        request_serializer: UniversityV2Serializers
        response_serializer: UniversityV2Serializers

        parameters:
            - name: university
              required: false
              in: query

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(UniversityViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Returns the detail of an University
        ---
        request_serializer: UniversityV2Serializers
        response_serializer: UniversityV2Serializers

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(UniversityViewSet, self).retrieve(
            request, *args, **kwargs)


router.register(
    r'catalogues/universities',
    UniversityViewSet,
    base_name="universities"
)
