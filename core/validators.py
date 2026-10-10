from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


def validate_uploaded_image(value):
    if not value:
        return

    if getattr(value, "_committed", False):
        return

    if value.size > MAX_IMAGE_BYTES:
        raise ValidationError("Размер изображения не должен превышать 5 МиБ.")

    position = value.tell()

    try:
        value.seek(0)

        with Image.open(value) as image:
            if image.format not in ALLOWED_IMAGE_FORMATS:
                raise ValidationError("Допустимы изображения JPEG, PNG и WebP.")

            width, height = image.size

            if width * height > MAX_IMAGE_PIXELS:
                raise ValidationError("Изображение слишком большое по разрешению.")

            image.verify()

    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValidationError("Файл не является корректным изображением.") from exc
    finally:
        value.seek(position)