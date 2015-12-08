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

SERVICE_CHOICES = (
    ('', ''),
    ('PRIORITY', 'PRIORITY'),
    ('LIBRARY MAIL', 'LIBRARY MAIL'),
    ('MEDIA MAIL', 'MEDIA MAIL'),
    ('STANDARD POST', 'STANDARD POST'),
    ('FIRST CLASS', 'FIRST CLASS'),
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

class LabelForm(serializers.Serializer):
    from_name = serializers.CharField()
    from_firm = serializers.CharField(required=False)
    from_address1 = serializers.CharField(max_length=120)
    from_address2 = serializers.CharField(required=False)
    from_city = serializers.CharField()
    from_state = serializers.CharField(max_length=2)
    from_zip = serializers.CharField(max_length=5, min_length=5)
    from_zip4 = serializers.CharField(max_length=4, min_length=4, required=False)
    to_name = serializers.CharField()
    to_firm = serializers.CharField(required=False)
    to_address1 = serializers.CharField(max_length=120)
    to_address2 = serializers.CharField(required=False)
    to_city = serializers.CharField()
    to_state = serializers.CharField(max_length=2)
    to_zip = serializers.CharField(max_length=5, min_length=5)
    to_zip4 = serializers.CharField(max_length=4, min_length=4, required=False)
    weight = serializers.DecimalField(min_value=0.01, decimal_places=2, max_digits=5)
    width = serializers.DecimalField(required=False, min_value=0.01, decimal_places=2, max_digits=5)
    height = serializers.DecimalField(required=False, min_value=0.01, decimal_places=2, max_digits=5)
    depth = serializers.DecimalField(required=False, min_value=0.01, decimal_places=2, max_digits=5)
    girth = serializers.DecimalField(required=False, min_value=0.01, decimal_places=2, max_digits=5)
    container = serializers.ChoiceField(required=False, choices=CONTAINER_CHOICES, default='')
    service_type = serializers.ChoiceField(required=False, choices=SERVICE_CHOICES)
