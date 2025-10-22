from rest_framework import serializers
from leads.models import Application, ApplicationAttachment, ContactMessage

class ApplicationAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationAttachment
        fields = ["file", "title"]

class ApplicationCreateSerializer(serializers.ModelSerializer):
    attachments = ApplicationAttachmentSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Application
        fields = [
            "full_name", "phone", "email", "country", "city", "preferred_contact",
            "tour", "alt_destination", "desired_start_date", "days",
            "adults", "children", "infants",
            "currency", "budget_from", "budget_to",
            "message",
            "utm_source", "utm_medium", "utm_campaign",
            "attachments",
        ]

    def create(self, validated_data):
        files = validated_data.pop("attachments", [])
        request = self.context.get("request")
        # texnik izlar
        validated_data["client_ip"] = request.META.get("REMOTE_ADDR")
        validated_data["user_agent"] = request.META.get("HTTP_USER_AGENT")
        validated_data["referrer"] = request.META.get("HTTP_REFERER", "")
        obj = Application.objects.create(**validated_data)
        for f in files:
            ApplicationAttachment.objects.create(application=obj, **f)
        return obj

class ContactMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["full_name", "email", "phone", "subject", "message"]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["client_ip"] = request.META.get("REMOTE_ADDR")
        validated_data["user_agent"] = request.META.get("HTTP_USER_AGENT")
        validated_data["referrer"] = request.META.get("HTTP_REFERER", "")
        return super().create(validated_data)
