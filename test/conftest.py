import pytest

from source.models import Product


@pytest.fixture
def create_and_delete_product_fixture():
    product = Product()
    system_code = product.create_product(system_code='100101030001')
    yield product
    product.delete_product(system_code=system_code)


@pytest.fixture
def create_product_fixture():
    product = Product()
    system_code = product.create_product(system_code='100101030001')
    yield product


@pytest.fixture
def create_and_delete_products_fixture():
    product = Product()
    system_codes = []
    for i in range(1, 4):
        system_codes.append((product.create_product(system_code='10010103000' + str(i))))
    yield product
    for system_code in system_codes:
        product.delete_product(system_code=system_code)


@pytest.fixture
def conf_dict_sample():
    conf_sample = {
        'storage': ['512gb', '512 gb', '256gb', '256 gb', '128gb', '128 gb', '64gb', '64 gb', '32gb', '32 gb',
                    '16gb', '16 gb', '1gb', '1 gb', '32mg', '1tb', '1 tb', '2tb', '2 tb', '4tb', '4 tb', '5tb',
                    '5 tb'],
        'color': ['dark blue', 'white/blue', 'haze silver', 'iceberg blue', 'gold coffe', 'gold black', 'rose gold',
                  'black/red', 'ocean blue', 'white red', 'white/red',
                  'black/blue', 'black red', 'orange', 'breathing crystal', 'white', 'green', 'blue',
                  'black', 'color', 'gray', 'violet', 'gold',
                  'silver', 'red', 'pink', 'bronze', 'purple', 'yellow', 'charcoal', 'brown', 'mix', 'aura glow',
                  'coral', 'boronz', 'dark nebula', 'olive', 'cyan', 'rose', 'dusk', 'military', 'sand',
                  'dark night', 'bedone rang', 'ice', 'titanium', 'fjord'],
        'guarantee': ['sherkati 01', 'sherkati', 'aban digi', 'abandigi', 'life time', 'awat', 'asli', 'nog',
                      'sazgar',
                      'nabeghe'],
        'ram': ['16gb', '12gb', '8gb', '6gb', '4gb', '3gb', '2gb', '1gb'],
        'network': ['5g', '4g'],
        'capacity': ['20k', '10000mah', '10k', '2600mah', '6800mah', '20100 mah', '10400mah', '5000mah'],
        'sim': ['dual sim'],
        'year': ['2018', '2019', '2020'],
        'type': ['wireless', 'wireless headphones'],
        'power': ['10w', '18w'],
        'part_number': ['zaa'],
        'processor': ['7020u'],
        'ignore_case': ['case', 'glass', 'headphones', 'smart band', 'smart watch', 'i3', 'intel', 'tamam']
    }
    return conf_sample


@pytest.fixture
def words_dict():
    words = {'64': 'storage', 'orange': 'color', 'sherkati': 'guarantee', '128GB': 'storage',
             'breathing crystal': 'color', '6GB': 'ram',
             '64GB': 'storage', 'white': 'color', 'sherkati 01': 'guarantee', '4GB': 'ram', 'green': 'color',
             '3GB': 'ram',
             '32GB': 'storage', 'blue': 'color', 'black': 'color',
             'aban digi': 'guarantee', '32': 'storage', '8': 'ram', 'color': 'color',
             'life time': 'guarantee', '128': 'storage', '5g': 'network',
             'gray': 'color', 'awat': 'guarantee', 'Smart': '-', 'Band': '-', 'asli': 'guarantee',
             '8GB': 'ram',
             'violet': 'color', '256GB': 'storage',
             '2GB': 'ram', '20k': 'capacity', 'nog': 'guarantee', '': '-', 'gold': 'color', '16': 'storage',
             '10000mah': 'capacity', 'dual sim': 'sim',
             '10k': 'capacity', 'silver': 'color', '2019': 'year', 'red': 'color', 'pink': 'color',
             '256': 'storage',
             'bronze': 'color',
             'purple': 'color', '16GB': 'storage', 'black': 'color', '512': 'storage', 'Glas': '-',
             '128GBBlackAWAT': '-', 'Yellow': 'color',
             'Charcoal': 'color', 'Brown': 'color', '32MG': 'storage', 'GB': '-', 'silver': 'color',
             'Mix': 'color',
             'NoG]': 'guarantee', 'Cas': '-',
             '1TB': 'storage', 'BLACK': 'color', 'Aura Glow': 'color', '64GBBlueSHERKATI': '-',
             '4G': 'network',
             '12GB': 'ram', '64GBGreenSHERKATI': '', 'Black/Blue': 'color', 'Coral': 'color',
             'Boronz': 'color',
             'Dark Nebula': 'color', '2020': 'year', '128GBBlueAWAT': '', '1GB': 'ram',
             '128GBWhiteAWAT': '', '256GBBlackSHERKATI': '',
             'Olive': 'color', '256GBBlackAWAT': '', '256GBPurpleSHERKATI': '', 'red': 'color',
             'cyan': 'color',
             '128GBPurpleSHERKATI': '', 'Rose': 'color', 'Dusk': 'color', '20': '', 'Cyan': 'color',
             '128GBBlueSHERKATI': '',
             'Wireless': 'type', '10W': 'power', 'Military': 'color', 'pink': 'color', 'Gray': 'color',
             'AWAT]': '',
             '4 TB': 'storage', 'SAZGAR': 'guarantee', '2600mAh': 'capacity', '5 TB': 'storage',
             '20k': 'capacity',
             'Sand': 'color', 'Wireless Headphones': 'type',
             'gray': 'color',
             'ZAA': 'part number', '6800mAh': 'capacity', 'Dark Night': 'color', 'Bedone rang': 'color',
             '256GBBlueSHERKATI': '',
             '5g': 'network', '512GB': 'storage', 'Nabeghe': 'guarantee', '64GBBlueAWAT': '',
             'White/Red': 'color',
             '256GBBlueAWAT': '',
             '256GBWhiteSHERKATI': '', '20100 mAh': 'capacity', 'AWA': 'ffffffffffffffff', '18W': 'power',
             'NOG': 'guarantee', '2018': 'year',
             'Ocean Blue': 'color', 'ICE': 'color', '64GBRedAWAT': '', '10k': 'capacity', 'WHITE': 'color',
             'Black/Red': 'color',
             'i3': 'processor', '7020U': 'processor',
             'Intel': 'processor', '10400mAh': 'capacity', '256GBWhiteAWAT': '-', 'White/Blue': 'color',
             '128GBGreenSHERKATI': '', '2': '',
             'Sherkati': 'guarantee', '5000mAh': 'capacity', '128GBPurpleAWAT': '', '64GBBlackAWAT': '',
             'Titanium': 'color',
             'Gold Coffe': 'color', 'Fjord': 'color', 'Haze silver': 'color', 'Iceberg Blue': 'color'}
    return words
