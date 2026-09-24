from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="photo",
            name="cloudinary_url",
            field=models.URLField(blank=True),
        ),
    ]