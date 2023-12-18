# Generated by Django 4.1.13 on 2023-12-18 15:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Model', '0016_remove_commande_confirmer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProduitLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('ajout', 'Ajout'), ('modification', 'Modification'), ('suppression', 'Suppression')], max_length=50)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('nom_produit', models.CharField(max_length=255, null=True)),
                ('prix_produit', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='produit',
            name='employer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='produits_ajoutes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='produitlog',
            name='produit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='produit_logs', to='Model.produit'),
        ),
        migrations.AddField(
            model_name='produitlog',
            name='utilisateur',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
