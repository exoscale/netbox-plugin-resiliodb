from django.db import migrations

def create_default_indicators(apps, schema_editor):
    Indicator = apps.get_model('netbox_resiliodb', 'Indicator')
    
    default_indicators = [
        {
            'code': 'ADPe',
            'name': 'Abiotic Depletion Potential - elements',
            'unit': 'kg Sb eq',
            'description': 'Measures the depletion of non-renewable mineral resources'
        },
        {
            'code': 'ADPf',
            'name': 'Abiotic Depletion Potential - fossil fuels',
            'unit': 'MJ',
            'description': 'Measures the depletion of non-renewable fossil fuel resources'
        },
        {
            'code': 'AP',
            'name': 'Acidification Potential',
            'unit': 'mol H+ eq',
            'description': 'Measures emissions that cause acidifying effects to the environment'
        },
        {
            'code': 'CTUe',
            'name': 'Comparative Toxic Unit for ecosystems',
            'unit': 'CTUe',
            'description': 'Measures toxic effects on freshwater ecosystems'
        },
        {
            'code': 'CTUh-c',
            'name': 'Comparative Toxic Unit for humans - carcinogenic',
            'unit': 'CTUh',
            'description': 'Measures carcinogenic effects on human health'
        },
        {
            'code': 'CTUh-nc',
            'name': 'Comparative Toxic Unit for humans - non-carcinogenic',
            'unit': 'CTUh',
            'description': 'Measures non-carcinogenic effects on human health'
        },
        {
            'code': 'Epf',
            'name': 'Eutrophication Potential - freshwater',
            'unit': 'kg P eq',
            'description': 'Measures nutrient enrichment in freshwater ecosystems'
        },
        {
            'code': 'Epm',
            'name': 'Eutrophication Potential - marine',
            'unit': 'kg N eq',
            'description': 'Measures nutrient enrichment in marine ecosystems'
        },
        {
            'code': 'Ept',
            'name': 'Eutrophication Potential - terrestrial',
            'unit': 'mol N eq',
            'description': 'Measures nutrient enrichment in terrestrial ecosystems'
        },
        {
            'code': 'GWP',
            'name': 'Global Warming Potential',
            'unit': 'kg CO2 eq',
            'description': 'Measures greenhouse gas emissions contributing to climate change'
        },
        {
            'code': 'IR',
            'name': 'Ionizing Radiation',
            'unit': 'kBq U235 eq',
            'description': 'Measures radioactive substance emissions'
        },
        {
            'code': 'LU',
            'name': 'Land Use',
            'unit': 'Pt',
            'description': 'Measures the environmental impact of land occupation and transformation'
        },
        {
            'code': 'ODP',
            'name': 'Ozone Depletion Potential',
            'unit': 'kg CFC-11 eq',
            'description': 'Measures emissions that deplete the ozone layer'
        },
        {
            'code': 'PM',
            'name': 'Particulate Matter',
            'unit': 'disease inc.',
            'description': 'Measures emissions of particulate matter affecting human health'
        },
        {
            'code': 'POCP',
            'name': 'Photochemical Ozone Creation Potential',
            'unit': 'kg NMVOC eq',
            'description': 'Measures emissions contributing to ground level ozone formation'
        },
        {
            'code': 'WU',
            'name': 'Water Use',
            'unit': 'm³ eq',
            'description': 'Measures water consumption and its environmental impacts'
        },
    ]

    for indicator_data in default_indicators:
        Indicator.objects.create(**indicator_data)

def reverse_default_indicators(apps, schema_editor):
    Indicator = apps.get_model('netbox_resiliodb', 'Indicator')
    Indicator.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('netbox_resiliodb', '0003_add_default_lca_types'),
    ]

    operations = [
        migrations.RunPython(
            create_default_indicators,
            reverse_default_indicators
        )
    ]
