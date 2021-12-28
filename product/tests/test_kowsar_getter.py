from product.module.kowsar_getter import KowsarGetter


def test_read_excel():
    kowsar_getter = KowsarGetter()
    sheet = kowsar_getter.read_excel(file_name='گروه کالا.xls')
    assert sheet is not None


def test_product_group_getter():
    kowsar_getter = KowsarGetter()
    kowsar_getter.product_group_getter()
    assert kowsar_getter.main_category_dict is not None
    assert kowsar_getter.main_category_dict['10'] == 'Device'
    assert kowsar_getter.sub_category_dict is not None
    assert kowsar_getter.sub_category_dict['1001'] == 'Mobile'
    assert kowsar_getter.brand_category_dict is not None
    assert kowsar_getter.brand_category_dict['100105'] == 'Mobile Huawei'
    assert kowsar_getter.model_dict is not None
    assert kowsar_getter.model_dict['100105005'] == 'P30 Lite'


def test_product_config_getter():
    kowsar_getter = KowsarGetter()
    name_config_code_with_bracket, name_config_code_without_bracket = kowsar_getter.product_config_getter()
    assert name_config_code_with_bracket is not None
    assert type(name_config_code_with_bracket) == list
    assert type(name_config_code_with_bracket[0]) == list
    assert name_config_code_with_bracket[0] == ['100104021006', 'Mobile Xiaomi Redmi 9C [64-Orange-SHERKATI]']
    assert name_config_code_without_bracket is not None
    assert type(name_config_code_with_bracket) == list
    assert type(name_config_code_with_bracket[0]) == list
    assert name_config_code_without_bracket[0] == ['100104012010', 'Mobile Xiaomi Note 9s 64-Gray-AWAT]']


def test_name_config_separator():
    kowsar_getter = KowsarGetter()
    kowsar_getter.product_group_getter()
    name_configs_codes_with_brackets, name_configs_codes_without_brackets = kowsar_getter.product_config_getter()
    config_list = kowsar_getter.name_config_separator(name_configs_codes_with_brackets,
                                                      name_configs_codes_without_brackets)
    assert config_list is not None
    assert type(config_list) == list
    assert config_list[0] == ['100104021006', 'Xiaomi Redmi 9c', '64-orange-sherkati']
    configs = kowsar_getter.configs
    assert configs is not None
    assert type(configs) == list
    assert configs[0] == '64-orange-sherkati'


def test_bag_of_words():
    kowsar_getter = KowsarGetter()
    kowsar_getter.product_group_getter()
    name_configs_codes_with_brackets, name_configs_codes_without_brackets = kowsar_getter.product_config_getter()
    kowsar_getter.name_config_separator(name_configs_codes_with_brackets, name_configs_codes_without_brackets)
    words_dict = kowsar_getter.bag_of_words()
    assert words_dict is not None
    assert type(words_dict) == dict
    assert words_dict.get('bedone') == ''


def test_bag_of_words_organizer(words_dict):
    kowsar_getter = KowsarGetter()
    new_dict = kowsar_getter.bag_of_words_organizer(words_dict)
    assert new_dict is not None
    assert type(new_dict) is dict
    assert new_dict.get('storage')[0] == '64'


def test_config_matcher(conf_dict_sample):
    kowsar_getter = KowsarGetter()
    config = '6-color-life time'
    new_conf = {}
    config, new_conf = kowsar_getter.config_matcher(config, new_conf, conf_dict_sample, 'guarantee')
    assert new_conf == {'guarantee': 'life time'}
    assert config == '6-color-'


def test_check_conf_is_empty():
    kowsar_getter = KowsarGetter()
    assert kowsar_getter.check_conf_is_empty('- ') is True
    assert kowsar_getter.check_conf_is_empty('-f') is False


def test_configs_list_maker():
    kowsar_getter = KowsarGetter()
    kowsar_getter.product_getter()
    assert kowsar_getter.config_dict is not None
    assert type(kowsar_getter.config_dict) is dict
    assert kowsar_getter.config_dict.get('100104021006') == {'storage': '64', 'color': 'orange',
                                                             'guarantee': 'sherkati'}


def test_system_code_name_getter():
    kowsar_getter = KowsarGetter()
    kowsar_getter.product_getter()
    assert kowsar_getter.system_code_name_getter('100101030001') == {
        'system_code': '100101030001',
        'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'},
        'model': 'A022',
        'brand': 'Mobile Sumsung',
        'sub_category': 'Mobile',
        'main_category': 'Device',
        'attributes': {}}

    assert kowsar_getter.system_code_name_getter('100104021') == {
        'system_code': '100104021',
        'model': 'Xiaomi Redmi 9c',
        'brand': 'Mobile Xiaomi',
        'sub_category': 'Mobile',
        'main_category': 'Device',
        'attributes': {}}

    assert kowsar_getter.system_code_name_getter('100104') == {
        'system_code': '100104',
        'brand': 'Mobile Xiaomi',
        'sub_category': 'Mobile',
        'main_category': 'Device',
        'attributes': {}}

    assert kowsar_getter.system_code_name_getter('1001') == {
        'system_code': '1001',
        'sub_category': 'Mobile',
        'main_category': 'Device'}

    assert kowsar_getter.system_code_name_getter('10') == {
        'system_code': '10',
        'main_category': 'Device',
        'attributes': {}}


def test_system_code_items_getter():
    kowsar_getter = KowsarGetter()
    kowsar_getter.product_group_getter()
    assert kowsar_getter.system_code_items_getter('10')[0] == {
        'system_code': '1001',
        'sub_category': 'Mobile',
        'main_category': 'Device'}
    assert kowsar_getter.system_code_items_getter('1001')[0] == {
        'system_code': '100101',
        'brand': 'Mobile Sumsung',
        'sub_category': 'Mobile',
        'main_category': 'Device',
        'attributes': {}}
    assert kowsar_getter.system_code_items_getter('100101')[0] == {
        'system_code': '100101001',
        'model': 'A260',
        'brand': 'Mobile Sumsung',
        'sub_category': 'Mobile',
        'main_category': 'Device',
        'attributes': {}}
    assert kowsar_getter.system_code_items_getter('100101001') == [
        {'system_code': '100101001002',
         'config': {'color': 'blue',
                    'guarantee': 'awat',
                    'storage': '16'},
         'model': 'A260',
         'brand': 'Mobile Sumsung',
         'sub_category': 'Mobile',
         'main_category': 'Device',
         'attributes': {}},
        {'system_code': '100101001009',
         'config': {'storage': '1gb',
                    'color': 'gray',
                    'guarantee': 'sherkati',
                    'ram': '8gb'},
         'model': 'A260', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
         'attributes': {}},
        {'system_code': '100101001001', 'config': {'color': 'black', 'guarantee': 'awat', 'storage': '16'},
         'model': 'A260', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
         'attributes': {}},
        {'system_code': '100101001005', 'config': {'color': 'black', 'guarantee': 'sherkati', 'storage': '16'},
         'model': 'A260', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
         'attributes': {}},
        {'system_code': '100101001004', 'config': {'color': 'gold', 'guarantee': 'awat', 'storage': '16'},
         'model': 'A260', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
         'attributes': {}},
        {'system_code': '100101001008', 'config': {'color': 'gray', 'guarantee': 'sherkati', 'storage': '16'},
         'model': 'A260', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
         'attributes': {}},
        {'system_code': '100101001007', 'config': {'color': 'red', 'guarantee': 'sherkati', 'storage': '16'},
         'model': 'A260', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
         'attributes': {}},
        {'system_code': '100101001003', 'config': {'color': 'red', 'guarantee': 'awat', 'storage': '16'},
         'model': 'A260', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
         'attributes': {}},
        {'system_code': '100101001006', 'config': {'color': 'blue', 'guarantee': 'sherkati', 'storage': '16'},
         'model': 'A260', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
         'attributes': {}}]
