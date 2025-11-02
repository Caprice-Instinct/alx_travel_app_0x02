"""
Serializers for the listings app models.
"""
from rest_framework import serializers
from .models import Booking, Payment


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for the Booking model."""

    class Meta:
        model = Booking
        fields = [
            'id',
            'booking_reference',
            'user_email',
            'property_name',
            'check_in_date',
            'check_out_date',
            'guests',
            'total_price',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'booking_reference', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate booking dates."""
        if data.get('check_out_date') and data.get('check_in_date'):
            if data['check_out_date'] <= data['check_in_date']:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )

        if data.get('guests', 0) <= 0:
            raise serializers.ValidationError(
                "Number of guests must be at least 1."
            )

        if data.get('total_price', 0) <= 0:
            raise serializers.ValidationError(
                "Total price must be greater than 0."
            )

        return data


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model."""

    class Meta:
        model = Payment
        fields = [
            'id',
            'booking_reference',
            'amount',
            'transaction_id',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
