from rest_framework import serializers

class LinkSerializer(serializers.Serializer):
    link = serializers.CharField(max_length=512, help_text="Исходная ссылка")
    length = serializers.IntegerField(
        min_value=6,
        max_value=20,
        required=True,  
        help_text="Длина новой ссылки от 6 до 20 включительно"
    )
    use_numeric = serializers.BooleanField(
        default=True,
        required=False,
        help_text="Использовать цифры в новой ссылке"
    )
