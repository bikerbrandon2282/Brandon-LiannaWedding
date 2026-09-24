from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0002_photo_cloudinary_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="photo",
            name="cloudinary_etag",
            field=models.CharField(blank=True, db_index=True, max_length=64),
        ),
    ]