from django.db import migrations, models


def migrate_old_questions(apps, schema_editor):
    Question = apps.get_model('app01', 'Question')
    mappings = [
        ('QuestionType', '爆破'),
        ('JskjgQuestion', '井工'),
        ('WxpzxQuestion', '危装'),
    ]
    for old_model_name, category in mappings:
        try:
            OldModel = apps.get_model('app01', old_model_name)
            for obj in OldModel.objects.all():
                Question.objects.create(
                    category=category,
                    question_type=obj.question_type,
                    tihao=obj.tihao,
                    question=obj.question,
                    options=obj.options,
                    correct_answer=obj.correct_answer,
                )
        except LookupError:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('app01', '0034_staff_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(help_text='爆破/井工/危装', max_length=10, verbose_name='题库类别')),
                ('question_type', models.CharField(max_length=20, verbose_name='题型')),
                ('tihao', models.CharField(max_length=20, verbose_name='题号')),
                ('question', models.TextField(verbose_name='题目')),
                ('options', models.CharField(max_length=200, verbose_name='选项')),
                ('correct_answer', models.CharField(max_length=20, verbose_name='正确答案')),
            ],
            options={
                'verbose_name': '题库',
                'db_table': 'app01_question',
            },
        ),
        migrations.RunPython(migrate_old_questions, migrations.RunPython.noop),
        migrations.DeleteModel(name='JskjgQuestion'),
        migrations.DeleteModel(name='QuestionType'),
        migrations.DeleteModel(name='WxpzxQuestion'),
        migrations.DeleteModel(name='Blaster'),
        migrations.AlterModelOptions(
            name='blastingcertificate',
            options={'verbose_name': '爆破员', 'verbose_name_plural': '爆破员'},
        ),
    ]
