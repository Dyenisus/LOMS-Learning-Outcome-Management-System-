from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assessment",
            name="type",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("QUIZ", "Quiz"),
                    ("MIDTERM", "Midterm"),
                    ("FINAL", "Final"),
                    ("PROJECT", "Project"),
                    ("ATTENDANCE", "Attendance"),
                ],
                default="ATTENDANCE",
            ),
        ),
    ]
