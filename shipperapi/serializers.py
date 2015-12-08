from rest_framework import serializers

CONTAINER_CHOICES = (
    ('', ''),
    ('RECTANGULAR', 'RECTANGULAR'),
    ('NONRECTANGULAR', 'NONRECTANGULAR'),
    ('Flat Rate Envelope', 'Flat Rate Envelope '),
    (' Padded Flat Rate Envelope', 'Padded Flat Rate Envelope'),
    (' Legal Flat Rate Envelope', 'Legal Flat Rate Envelope'),
    ('Sm Flat Rate Envelope', 'Sm Flat Rate Envelope'),
    (' Window Flat Rate Envelope', 'Window Flat Rate Envelope'),
    (' Gift Card Flat Rate Envelope', 'Gift Card Flat Rate Envelope'),
    ('Flat Rate Box', 'Flat Rate Box' ),
    (' Sm Flat Rate Box', 'Sm Flat Rate Box' ),
    (' Md Flat Rate Box', 'Md Flat Rate Box' ),
    (' Lg Flat Rate Box', 'Lg Flat Rate Box'),
)

class RateForm(serializers.Serializer):
    from_zip = serializers.CharField(max_length=5, min_length=5)
    to_zip = serializers.CharField(max_length=5, min_length=5)
    weight = serializers.DecimalField(required=False, min_value=0.01, decimal_places=2, max_digits=5)
    width = serializers.DecimalField(required=False, min_value=0.01, decimal_places=2, max_digits=5)
    height = serializers.DecimalField(required=False, min_value=0.01, decimal_places=2, max_digits=5)
    depth = serializers.DecimalField(required=False, min_value=0.01, decimal_places=2, max_digits=5)
    girth = serializers.DecimalField(required=False, min_value=0.01, decimal_places=2, max_digits=5)
    container = serializers.ChoiceField(required=False, choices=CONTAINER_CHOICES, default='')
