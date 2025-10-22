from rest_framework.response import Response
from rest_framework.views import APIView
from siteinfo.models import SiteSettings, AboutPage, ContactPage
from .api_serializers import SiteSettingsSerializer, AboutPageSerializer, ContactPageSerializer

class SiteSettingsView(APIView):
    def get(self, request):
        data = SiteSettings.get_solo()
        return Response(SiteSettingsSerializer(data).data)

class AboutPageView(APIView):
    def get(self, request):
        data = AboutPage.get_solo()
        return Response(AboutPageSerializer(data).data)

class ContactPageView(APIView):
    def get(self, request):
        data = ContactPage.get_solo()
        return Response(ContactPageSerializer(data).data)
