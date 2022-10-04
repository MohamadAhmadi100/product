from app.helpers.redis_connection import RedisConnection

mock = {'Accessory': {'en_us': 'Accessory', 'fa_ir': 'اکسسوری'},
        'Component': {'en_us': 'Component', 'fa_ir': 'کامپوننت'},
        'Device': {'en_us': 'Device', 'fa_ir': 'دستگاه'}, 'Network': {'en_us': 'Network', 'fa_ir': 'شبکه'},
        'Office Machines': {'en_us': 'Office Machines', 'fa_ir': 'ماشین های اداری'},
        'Access Point': {'en_us': 'Access Point', 'fa_ir': 'اکسس پوینت'},
        'All in One': {'en_us': 'All in One', 'fa_ir': 'کامپیوتر همه کاره'},
        'BackPack/HandyBag': {'en_us': 'BackPack/HandyBag', 'fa_ir': 'کوله پشتی/کیف دستی'},
        'Band': {'en_us': 'Band', 'fa_ir': 'بند'},
        'Barcode Reader': {'en_us': 'Barcode Reader', 'fa_ir': 'بارکدخوان'},
        'Battery': {'en_us': 'Battery', 'fa_ir': 'باتری'}, 'CPU': {'en_us': 'CPU', 'fa_ir': 'پردازنده'},
        'CPU FAN': {'en_us': 'CPU FAN', 'fa_ir': 'فن پردازنده'}, 'Cable': {'en_us': 'Cable', 'fa_ir': 'کابل'},
        'Camera': {'en_us': 'Camera', 'fa_ir': 'دوربین'}, 'Cartridge': {'en_us': 'Cartridge', 'fa_ir': 'کارتریج'},
        'Case': {'en_us': 'Case', 'fa_ir': 'کیس'}, 'Charger': {'en_us': 'Charger', 'fa_ir': 'شارژر'},
        'Converter': {'en_us': 'Converter', 'fa_ir': 'مبدل'}, 'Cooling': {'en_us': 'Cooling', 'fa_ir': 'خنک کننده'},
        'Copy-Machine': {'en_us': 'Copy-Machine', 'fa_ir': 'دستگاه کپی'},
        'Cover/Case': {'en_us': 'Cover/Case', 'fa_ir': 'محافظ/قاب'},
        'Data Video Projector': {'en_us': 'Data Video Projector', 'fa_ir': ' ویدئو پروژکتور'},
        'External DVD': {'en_us': 'External DVD', 'fa_ir': 'دی وی دی خارجی'},
        'External HDD': {'en_us': 'External HDD', 'fa_ir': 'هارد خارجی'},
        'External SSD': {'en_us': 'External SSD', 'fa_ir': 'اس اس دی خارجی'},
        'Fax': {'en_us': 'Fax', 'fa_ir': 'فکس'},
        'Flash Memory': {'en_us': 'Flash Memory', 'fa_ir': 'فلش مموری'},
        'Gajet': {'en_us': 'Gajet', 'fa_ir': 'گجت'},
        'Game Console': {'en_us': 'Game Console', 'fa_ir': 'کنسول بازی'},
        'Game/Software': {'en_us': 'Game/Software', 'fa_ir': 'بازی/نرم افزار'},
        'Gaming': {'en_us': 'Gaming', 'fa_ir': 'گیمینگ'},
        'Graphic Card': {'en_us': 'Graphic Card', 'fa_ir': 'کارت گرافیک'},
        'Headphone/Headset/Hands Free': {'en_us': 'Headphone/Headset/Hands Free',
                                         'fa_ir': 'هدفون / هدست / هندزفری'},
        'Internal DVD': {'en_us': 'Internal DVD', 'fa_ir': 'دی وی دی داخلی'},
        'Internal HDD': {'en_us': 'Internal HDD', 'fa_ir': 'هارد داخلی'},
        'Internal SSD': {'en_us': 'Internal SSD', 'fa_ir': 'اس اس دی داخلی'},
        'Keyboard': {'en_us': 'Keyboard', 'fa_ir': 'صفحه کلید'},
        'Keyboard & Mouse': {'en_us': 'Keyboard & Mouse', 'fa_ir': 'صفحه کلید و ماوس'},
        'LAN Card': {'en_us': 'LAN Card', 'fa_ir': 'کارت شبکه'},
        'Memory Card/Stick': {'en_us': 'Memory Card/Stick', 'fa_ir': 'کارت حافظه'},
        'Mobile': {'en_us': 'Mobile', 'fa_ir': 'موبایل'}, 'Modem': {'en_us': 'Modem', 'fa_ir': 'مودم'},
        'Monitor': {'en_us': 'Monitor', 'fa_ir': 'مانیتور'},
        'Motherboard': {'en_us': 'Motherboard', 'fa_ir': 'مادربرد'},
        'Mouse': {'en_us': 'Mouse', 'fa_ir': 'ماوس'}, 'Mouse Pad': {'en_us': 'Mouse Pad', 'fa_ir': 'پد ماوس'},
        'NB Battery': {'en_us': 'NB Battery', 'fa_ir': 'باتری NB'},
        'Notebook': {'en_us': 'Notebook', 'fa_ir': 'نوت بوک'},
        'PC': {'en_us': 'PC', 'fa_ir': 'کامپیوتر'}, 'Power Port': {'en_us': 'Power Port', 'fa_ir': 'چند راهی برق'},
        'Power Supply': {'en_us': 'Power Supply', 'fa_ir': 'منبع تغذیه'},
        'PowerBank': {'en_us': 'PowerBank', 'fa_ir': 'پاوربانک'}, 'Printer': {'en_us': 'Printer', 'fa_ir': 'چاپگر'},
        'RAM': {'en_us': 'RAM', 'fa_ir': 'رم'}, 'Scanner': {'en_us': 'Scanner', 'fa_ir': 'اسکنر'},
        'Screen Protector': {'en_us': 'Screen Protector', 'fa_ir': 'محافظ صفحه'},
        'Server': {'en_us': 'Server', 'fa_ir': 'سرور'}, 'Speaker': {'en_us': 'Speaker', 'fa_ir': 'اسپیکر'},
        'Stand/Holder': {'en_us': 'Stand/Holder', 'fa_ir': 'پایه / استند'},
        'Switch/Router': {'en_us': 'Switch/Router', 'fa_ir': 'سوئیچ/روتر'},
        'TV': {'en_us': 'TV', 'fa_ir': 'تلویزیون'},
        'Tablet': {'en_us': 'Tablet', 'fa_ir': 'تبلت'}, 'Telephone': {'en_us': 'Telephone', 'fa_ir': 'تلفن'},
        'USB HUB': {'en_us': 'USB HUB', 'fa_ir': 'هاب یو اس بی'},
        'Vacuum Cleaner': {'en_us': 'Vacuum Cleaner', 'fa_ir': 'جارو برقی'},
        'Watch': {'en_us': 'Watch', 'fa_ir': 'ساعت'},
        'WebCam': {'en_us': 'WebCam', 'fa_ir': 'وبکم'},
        'ANKER Cable': {'en_us': 'ANKER Cable', 'fa_ir': 'کابل انکر'},
        'Android box': {'en_us': 'Android box', 'fa_ir': 'باکس اندروید'},
        'Apple cable': {'en_us': 'Apple cable', 'fa_ir': 'کابل اپل'},
        'Cable ProOne': {'en_us': 'Cable ProOne', 'fa_ir': 'کابل پرو وان'},
        'Charger ANKER': {'en_us': 'Charger ANKER', 'fa_ir': 'شارژر انکر'},
        'Charger Energizer': {'en_us': 'Charger Energizer', 'fa_ir': 'شارژر انرژایزر'},
        'Charger Koluman': {'en_us': 'Charger Koluman', 'fa_ir': 'شارژر کلومن'},
        'Charger ProOne': {'en_us': 'Charger ProOne', 'fa_ir': 'شارژر پرو وان'},
        'Charger TSCO': {'en_us': 'Charger TSCO', 'fa_ir': 'شارژر تسکو'},
        'Charger Xiaomi': {'en_us': 'Charger Xiaomi', 'fa_ir': 'شارژر شیائومی'},
        'Dongle  ProOne': {'en_us': 'Dongle  ProOne', 'fa_ir': 'دانگل پرو وان'},
        'EarBuds Xiaomi': {'en_us': 'EarBuds Xiaomi', 'fa_ir': 'ایربادز شیائومی'},
        'Energizer Cable': {'en_us': 'Energizer Cable', 'fa_ir': 'کابل انرجایزر'},
        'Flash Memory SanDisk': {'en_us': 'Flash Memory SanDisk', 'fa_ir': 'فلش مموری سن دیسک'},
        'Gajet ProOne': {'en_us': 'Gajet ProOne', 'fa_ir': 'گجت پرو وان'},
        'Glass': {'en_us': 'Glass', 'fa_ir': 'محافظ صفحه نمایش'},
        'HDD CoverProOne': {'en_us': 'HDD CoverProOne', 'fa_ir': 'کاور هارد پرو وان'},
        'HDD WD': {'en_us': 'HDD WD', 'fa_ir': 'هارد وسترن دیجیتال'},
        'Headphone ANKER': {'en_us': 'Headphone ANKER', 'fa_ir': 'هدفون انکر'},
        'Headphone Apple': {'en_us': 'Headphone Apple', 'fa_ir': 'هدفون اپل'},
        'Headphone JBL': {'en_us': 'Headphone JBL', 'fa_ir': 'هدفون جی بی ال'},
        'Headphone Koluman': {'en_us': 'Headphone Koluman', 'fa_ir': 'هدفون کلومن'},
        'Headphone ProOne': {'en_us': 'Headphone ProOne', 'fa_ir': 'هدفون پرو وان'},
        'Headphone TSCO': {'en_us': 'Headphone TSCO', 'fa_ir': 'هدفون تسکو'},
        'Headset Haylou': {'en_us': 'Headset Haylou', 'fa_ir': 'هدست هایلو'},
        'Headset Logitech': {'en_us': 'Headset Logitech', 'fa_ir': 'هدست لاجیتک'},
        'Holder Koluman': {'en_us': 'Holder Koluman', 'fa_ir': 'نگهدارنده کلومن'},
        'Honor Band': {'en_us': 'Honor Band', 'fa_ir': 'بند آنر'}, 'Huawei': {'en_us': 'Huawei', 'fa_ir': 'هواوی'},
        'Keyboard Logitech': {'en_us': 'Keyboard Logitech', 'fa_ir': 'صفحه کلید لاجیتک'},
        'Koluman Cable': {'en_us': 'Koluman Cable', 'fa_ir': 'کابل کلومن'},
        'Koluman Power Port': {'en_us': 'Koluman Power Port', 'fa_ir': 'چند راهی برق کلومن'},
        'Mobile Apple': {'en_us': 'Mobile Apple', 'fa_ir': 'موبایل اپل'},
        'Mobile Blu': {'en_us': 'Mobile Blu', 'fa_ir': 'موبایل بلو'},
        'Mobile CAT': {'en_us': 'Mobile CAT', 'fa_ir': 'موبایل کت'},
        'Mobile Energizer': {'en_us': 'Mobile Energizer', 'fa_ir': 'انرجایزر موبایل'},
        'Mobile G Plus': {'en_us': 'Mobile G Plus', 'fa_ir': 'موبایل جی پلاس'},
        'Mobile Honor': {'en_us': 'Mobile Honor', 'fa_ir': 'موبایل آنر'},
        'Mobile Huawei': {'en_us': 'Mobile Huawei', 'fa_ir': 'موبایل هواوی'},
        'Mobile LG': {'en_us': 'Mobile LG', 'fa_ir': 'موبایل ال جی'},
        'Mobile Nokia': {'en_us': 'Mobile Nokia', 'fa_ir': 'موبایل نوکیا'},
        'Mobile OROD': {'en_us': 'Mobile OROD', 'fa_ir': 'موبایل اورود'},
        'Mobile Realme': {'en_us': 'Mobile Realme', 'fa_ir': 'موبایل ریلمی'},
        'Mobile Smart': {'en_us': 'Mobile Smart', 'fa_ir': 'موبایل اسمارت'},
        'Mobile Sumsung': {'en_us': 'Mobile Sumsung', 'fa_ir': 'موبایل سامسونگ'},
        'Mobile Xiaomi': {'en_us': 'Mobile Xiaomi', 'fa_ir': 'موبایل شیاومی'},
        'Mouse Logitech': {'en_us': 'Mouse Logitech', 'fa_ir': 'ماوس لاجیتک'},
        'MousePad Logitech': {'en_us': 'MousePad Logitech', 'fa_ir': 'ماوس پد لاجیتک'},
        'Notebook Lenovo': {'en_us': 'Notebook Lenovo', 'fa_ir': 'نوت بوک لنوو'},
        'Omthing': {'en_us': 'Omthing', 'fa_ir': 'Omthing'},
        'Other Stand/Holder': {'en_us': 'Other Stand/Holder', 'fa_ir': 'پایه / استند دیگر'},
        'Power Converter  ProOne': {'en_us': 'Power Converter  ProOne', 'fa_ir': 'مبدل برق پرو وان'},
        'PowerBank  ProOne': {'en_us': 'PowerBank  ProOne', 'fa_ir': 'پاوربانک پرو وان'},
        'PowerBank ANKER': {'en_us': 'PowerBank ANKER', 'fa_ir': 'پاوربانک انکر'},
        'PowerBank Koluman': {'en_us': 'PowerBank Koluman', 'fa_ir': 'پاوربانک کلومن'},
        'PowerBank TSCO': {'en_us': 'PowerBank TSCO', 'fa_ir': 'پاوربانک تسکو'},
        'PowerBank Xiaomi': {'en_us': 'PowerBank Xiaomi', 'fa_ir': 'پاوربانک شیائومی'},
        'Racing': {'en_us': 'Racing', 'fa_ir': 'فرمان'},
        'Samsung case': {'en_us': 'Samsung case', 'fa_ir': 'قاب سامسونگ'},
        'SanDisk Memory': {'en_us': 'SanDisk Memory', 'fa_ir': 'حافظه سن دیسک'},
        'Scale': {'en_us': 'Scale', 'fa_ir': 'ترازو'},
        'Speaker ANKER': {'en_us': 'Speaker ANKER', 'fa_ir': 'اسپیکر انکر'},
        'Speaker Koluman': {'en_us': 'Speaker Koluman', 'fa_ir': 'اسپیکر کلومن'},
        'Speaker Logitech': {'en_us': 'Speaker Logitech', 'fa_ir': 'اسپیکر لاجیتک'},
        'Speaker ProOne': {'en_us': 'Speaker ProOne', 'fa_ir': 'اسپیکر پرو وان'},
        'Speaker TSCO': {'en_us': 'Speaker TSCO', 'fa_ir': 'اسپیکر تسکو'},
        'Speaker Xiaomi': {'en_us': 'Speaker Xiaomi', 'fa_ir': 'اسپیکر شیائومی'},
        'Stand/Holder  ProOne': {'en_us': 'Stand/Holder  ProOne', 'fa_ir': 'استند/پایه پرو وان'},
        'TSCO Cable': {'en_us': 'TSCO Cable', 'fa_ir': 'کابل تسکو'},
        'Tablet Lenovo': {'en_us': 'Tablet Lenovo', 'fa_ir': 'تبلت لنوو'},
        'Tablet SAMSUNG': {'en_us': 'Tablet SAMSUNG', 'fa_ir': 'تبلت سامسونگ'},
        'Vacuum Cleaner Xiaomi': {'en_us': 'Vacuum Cleaner Xiaomi', 'fa_ir': 'جاروبرقی شیائومی'},
        'Watch Amazfit': {'en_us': 'Watch Amazfit', 'fa_ir': 'ساعت امیزفیت'},
        'Watch Haylou': {'en_us': 'Watch Haylou', 'fa_ir': 'Haylou ساعت '},
        'Watch Omthing': {'en_us': 'Watch Omthing', 'fa_ir': 'ساعت اومتینگ'},
        'Watch Xiaomi': {'en_us': 'Watch Xiaomi', 'fa_ir': 'ساعت شیائومی '},
        'Xiaomi Band': {'en_us': 'Xiaomi Band', 'fa_ir': 'بند شیائومی'},
        'Xiaomi Cable': {'en_us': 'Xiaomi Cable', 'fa_ir': 'کابل شیائومی'},
        'Xiaomi Case': {'en_us': 'Xiaomi Case', 'fa_ir': 'قاب شیائومی'},
        'aura glow': {'en_us': 'aura glow', 'fa_ir': 'هفت رنگ'},
        'bedone rang': {'en_us': 'bedone rang', 'fa_ir': 'بدون رنگ'}, 'black': {'en_us': 'black', 'fa_ir': 'سیاه'},
        'black red': {'en_us': 'black red', 'fa_ir': 'قرمز مشکی'},
        'black/blue': {'en_us': 'black/blue', 'fa_ir': 'آبی مشکی'},
        'black/red': {'en_us': 'black/red', 'fa_ir': 'قرمز مشکی'}, 'blue': {'en_us': 'blue', 'fa_ir': 'آبی'},
        'boronz': {'en_us': 'boronz', 'fa_ir': 'برنز'},
        'breathing crystal': {'en_us': 'breathing crystal', 'fa_ir': 'آبی گوهری'},
        'bronze': {'en_us': 'bronze', 'fa_ir': 'برنز'}, 'brown': {'en_us': 'brown', 'fa_ir': ' قهوه ای'},
        'charcoal': {'en_us': 'charcoal', 'fa_ir': 'ذغالی'}, 'color': {'en_us': 'color', 'fa_ir': 'رنگ'},
        'coral': {'en_us': 'coral', 'fa_ir': 'مرجانی'}, 'cyan': {'en_us': 'cyan', 'fa_ir': 'فیروزه ای'},
        'dark blue': {'en_us': 'dark blue', 'fa_ir': 'آبی تیره'},
        'dark nebula': {'en_us': 'dark nebula', 'fa_ir': 'بنفش کیهانی'},
        'dark night': {'en_us': 'dark night', 'fa_ir': 'مشکی'}, 'dusk': {'en_us': 'dusk', 'fa_ir': 'بنفش'},
        'fjord': {'en_us': 'fjord', 'fa_ir': 'آبی'}, 'gold': {'en_us': 'gold', 'fa_ir': 'طلایی'},
        'gold black': {'en_us': 'gold black', 'fa_ir': 'طلایی تیره'},
        'gold coffe': {'en_us': 'gold coffe', 'fa_ir': 'قهوه ای طلایی'},
        'gray': {'en_us': 'gray', 'fa_ir': 'خاکستری'},
        'green': {'en_us': 'green', 'fa_ir': 'سبز'},
        'haze silver': {'en_us': 'haze silver', 'fa_ir': ' نقره ای مات'},
        'ice': {'en_us': 'ice', 'fa_ir': 'یخی'}, 'iceberg blue': {'en_us': 'iceberg blue', 'fa_ir': 'آبی یخی'},
        'military': {'en_us': 'military', 'fa_ir': 'چریکی'}, 'mix': {'en_us': 'mix', 'fa_ir': 'میکس'},
        'ocean blue': {'en_us': 'ocean blue', 'fa_ir': 'آبی اقیانوسی'},
        'olive': {'en_us': 'olive', 'fa_ir': 'زیتونی'},
        'orange': {'en_us': 'orange', 'fa_ir': 'نارنجی'}, 'pink': {'en_us': 'pink', 'fa_ir': ' صورتی'},
        'purple': {'en_us': 'purple', 'fa_ir': ' بنفش'}, 'red': {'en_us': 'red', 'fa_ir': 'قرمز'},
        'rose gold': {'en_us': 'rose gold', 'fa_ir': 'رزگلد'}, 'sand': {'en_us': 'sand', 'fa_ir': 'شنی'},
        'silver': {'en_us': 'silver', 'fa_ir': 'نقره اي'}, 'titanium': {'en_us': 'titanium', 'fa_ir': 'تیتانیوم'},
        'Mint': {'en_us': 'Mint', 'fa_ir': 'سبز نعنایی'}, 'Peach': {'en_us': 'Peach', 'fa_ir': 'هلویی'},
        'violet': {'en_us': 'violet', 'fa_ir': 'بنفش'}, 'white': {'en_us': 'white', 'fa_ir': 'سفید'},
        'white red': {'en_us': 'white red', 'fa_ir': 'قرمز سفید'},
        'white/blue': {'en_us': 'white/blue', 'fa_ir': 'آبی سفید'},
        'white/red': {'en_us': 'white/red', 'fa_ir': 'قرمز سفید'}, 'yellow': {'en_us': 'yellow', 'fa_ir': ' زرد'},
        'aban digi': {'en_us': 'aban digi', 'fa_ir': 'آبان دیجی'},
        'abandigi': {'en_us': 'abandigi', 'fa_ir': 'آبان دیجی'},
        'asli': {'en_us': 'asli', 'fa_ir': 'اصلی'}, 'awat': {'en_us': 'awat', 'fa_ir': 'آوات'},
        'life time': {'en_us': 'life time', 'fa_ir': 'مادام العمر'},
        'nabeghe': {'en_us': 'nabeghe', 'fa_ir': 'نابغه'},
        'nog': {'en_us': 'nog', 'fa_ir': 'بدون گارانتی'}, 'sazgar': {'en_us': 'sazgar', 'fa_ir': 'سازگار'},
        'sherkati': {'en_us': 'sherkati', 'fa_ir': 'شرکتی'},
        'sherkati 01': {'en_us': 'sherkati 01', 'fa_ir': 'شرکتی ۰۱'},
        'storage': {'en_us': 'storage', 'fa_ir': 'حافظه داخلی'},
        'ram': {'en_us': 'ram', 'fa_ir': 'رم'},
        'guarantee': {'en_us': 'guarantee', 'fa_ir': 'گارانتی'},
        'seller': {'en_us': 'storage', 'fa_ir': 'فروشنده'},
        'warehouse': {'en_us': 'warehouse', 'fa_ir': 'انبار'},
        'images': {'en_us': 'images', 'fa_ir': 'تصاویر'},
        'Hamrah Gharb': {'en_us': 'Hamrah Gharb', 'fa_ir': 'همراه غرب'},
        'TejaratKhane Haj Ghasem': {'en_us': 'TejaratKhane Haj Ghasem', 'fa_ir': 'تجارت خانه حاجی قاسم'},
        'Aban Digi': {'en_us': 'Aban Digi', 'fa_ir': 'آبان دیجی'}, 'Aasood': {'en_us': 'Aasood', 'fa_ir': 'آسود'},
        'Awat': {'en_us': 'Awat', 'fa_ir': 'آوات'}, 'Nabeghe': {'en_us': 'Nabeghe', 'fa_ir': 'نابغه'},
        'GB': {'en_us': 'GigaByte', 'fa_ir': 'گیگابایت'},
        'TB': {'en_us': 'TeraByte', 'fa_ir': 'ترابایت'},
        'MB': {'en_us': 'MegaByte', 'fa_ir': 'مگابایت'},
        }

mock = {
    "Black": {"en_us": "Black", "fa_ir": "مشکی"},
    "Phantom black": {"en_us": "Phantom black", "fa_ir": "مشکی"},
    "Gray": {"en_us": "Gray", "fa_ir": "خاکستری"},
    "Graphite": {"en_us": "Graphite", "fa_ir": "نوک مدادی"},
    "Blue": {"en_us": "Blue", "fa_ir": "آبی"},
    "Sky blue": {"en_us": "Sky blue", "fa_ir": "آبی آسمانی"},
    "Green": {"en_us": "Green", "fa_ir": "سبز"},
    "Mint": {"en_us": "Mint", "fa_ir": "نعنایی"},
    "Peach": {"en_us": "Peach", "fa_ir": "هلویی"},
    "Pink": {"en_us": "Pink", "fa_ir": "صورتی"},
    "Pink gold": {"en_us": "Pink gold", "fa_ir": "طلای صورتی"},
    "Lavender": {"en_us": "Lavender", "fa_ir": "بنفش"},
    "Violet": {"en_us": "Violet", "fa_ir": "بنفش"},
    "Burgundy": {"en_us": "Burgundy", "fa_ir": "شرابی"},
    "Cream": {"en_us": "Cream", "fa_ir": "کرم"},
    "White": {"en_us": "White", "fa_ir": "سفید"},
    "Red": {"en_us": "Red", "fa_ir": "قرمز"},
    "Icy Blue": {"en_us": "Icy Blue", "fa_ir": "آبی"},
    "Blazing Black": {"en_us": "Blazing Black", "fa_ir": "مشکی"},
    "Light Blue": {"en_us": "Light Blue", "fa_ir": "آبی"},
    "Graphite Gray": {"en_us": "Graphite Gray", "fa_ir": "خاکستری"},
    "Polar White": {"en_us": "Polar White", "fa_ir": "سفید"},
    "Atlantic Blue": {"en_us": "Atlantic Blue", "fa_ir": "آبی اطلسی"},
    "Star Blue": {"en_us": "Star Blue", "fa_ir": "آبی روشن (ستاره ای)"},
    "Pearl White": {"en_us": "Pearl White", "fa_ir": "سفید"},
    "Twilight Blue": {"en_us": "Twilight Blue", "fa_ir": "آبی تیره"},
    "Carbon Gray": {"en_us": "Carbon Gray", "fa_ir": "خاکستری"},
    "Pebble White": {"en_us": "Pebble White", "fa_ir": "سفید"},
    "Sea Blue": {"en_us": "Sea Blue", "fa_ir": "آبی"},
    "Power Black": {"en_us": "Power Black", "fa_ir": "مشکی"},
    "POCO Yellow": {"en_us": "POCO Yellow", "fa_ir": "زرد"},
    "Cool Blue": {"en_us": "Cool Blue", "fa_ir": "آبی"},
    "Carbon Black": {"en_us": "Carbon Black", "fa_ir": "مشکی"},
    "Coral Green": {"en_us": "Coral Green", "fa_ir": "سبز"},
    "Metallic Blue": {"en_us": "Metallic Blue", "fa_ir": "آبی"},
    "Truffle Black ": {"en_us": "Truffle Black ", "fa_ir": "مشکی"},
    "Bubblegum Blue": {"en_us": "Bubblegum Blue", "fa_ir": "آبی"},
    "Peach Pink": {"en_us": "Peach Pink", "fa_ir": "صورتی"},
    "Snowflake White": {"en_us": "Snowflake White", "fa_ir": "سفید"},
    "Astral White": {"en_us": "Astral White", "fa_ir": "سفید"},
    "Bifrost Blue": {"en_us": "Bifrost Blue", "fa_ir": "آبی"},
    "Royal Blue": {"en_us": "Royal Blue", "fa_ir": "آبی"},
    "Shadow Gray": {"en_us": "Shadow Gray", "fa_ir": "خاکستری"},
    "Silver": {"en_us": "Silver", "fa_ir": "نقره ای"},
    "Cyber Yellow": {"en_us": "Cyber Yellow", "fa_ir": "زرد"},
    "Knight Silver": {"en_us": "Knight Silver", "fa_ir": "نقره ای"},
    "Stealth Black": {"en_us": "Stealth Black", "fa_ir": "مشکی"},
    "Purple": {"en_us": "Purple", "fa_ir": "بنفش"},
    "Laser Blue": {"en_us": "Laser Blue", "fa_ir": "آبی"},
    "Laser Black": {"en_us": "Laser Black", "fa_ir": "مشکی"},
    "Deep Ocean Blue": {"en_us": "Deep Ocean Blue", "fa_ir": "آبی"},
    "Moonlight Silver": {"en_us": "Moonlight Silver", "fa_ir": "نقره ای"},
    " Arctic White": {"en_us": " Arctic White", "fa_ir": "سفید"},
    "Midnight": {"en_us": "Midnight", "fa_ir": "مشکی"},
    "Starlight": {"en_us": "Starlight", "fa_ir": "سفید"},
    "Alpine Green": {"en_us": "Alpine Green", "fa_ir": "سبز"},
    "Gold": {"en_us": "Gold", "fa_ir": "طلایی"},
    "Sierra Blue": {"en_us": "Sierra Blue", "fa_ir": "آبی"},
    "Aawaat": {"en_us": "Aawaat", "fa_ir": "آوات"},
    "ASD": {"en_us": "ASD", "fa_ir": "آسود"},
    "Sherkati": {"en_us": "Sherkati", "fa_ir": "شرکتی"},
}

a = {
    "colors": [
        {
            "label": "مشکی",
            "name": "Black",
            "hex": "#000000"
        },
        {
            "label": "مشکی",
            "name": "Phantom Black",
            "hex": "#39373b"
        },
        {
            "label": "خاکستری",
            "name": "Gray",
            "hex": "#808080"
        },
        {
            "label": "نوک مدادی",
            "name": "Graphite",
            "hex": "#251607"
        },
        {
            "label": "آبی",
            "name": "Blue",
            "hex": "#1c1cbf"
        },
        {
            "label": "آبی آسمانی",
            "name": "Sky blue",
            "hex": "#87CEEB"
        },
        {
            "label": "سبز",
            "name": "Green",
            "hex": "#0b6c0b"
        },
        {
            "label": "نعنایی",
            "name": "Mint",
            "hex": "#3EB489"
        },
        {
            "label": "هلویی",
            "name": "Peach",
            "hex": "#FFE5B4"
        },
        {
            "label": "صورتی",
            "name": "Pink",
            "hex": "#ffc0cb"
        },
        {
            "label": "طلای صورتی",
            "name": "Pink gold",
            "hex": "#e6c7c2"
        },
        {
            "label": "بنفش",
            "name": "Lavender",
            "hex": "#E6E6FA"
        },
        {
            "label": "بنفش",
            "name": "Violet",
            "hex": "#8F00FF"
        },
        {
            "label": "شرابی",
            "name": "Burgundy",
            "hex": "#800020"
        },
        {
            "label": "کرم",
            "name": "Cream",
            "hex": "#FFFDD0"
        },
        {
            "label": "سفید",
            "name": "White",
            "hex": "#ffffff"
        },
        {
            "label": "قرمز",
            "name": "Red",
            "hex": "#ff0000"
        },
        {
            "label": "آبی",
            "name": "Icy Blue",
            "hex": "#C8E9E9"
        },
        {
            "label": "مشکی",
            "name": "Blazing Black",
            "hex": "#121212"
        },
        {
            "label": "آبی",
            "name": "Light Blue",
            "hex": "#ADD8E6"
        },
        {
            "label": "خاکستری",
            "name": "Graphite Gray",
            "hex": "#53565b"
        },
        {
            "label": "سفید",
            "name": "Polar White",
            "hex": "#eef4f4"
        },
        {
            "label": "آبی اطلسی",
            "name": "Atlantic Blue",
            "hex": "#0c325b"
        },
        {
            "label": "آبی روشن (ستاره ای)",
            "name": "Star Blue",
            "hex": "#9ab4c2"
        },
        {
            "label": "سفید",
            "name": "Pearl White",
            "hex": "#F8F6F0"
        },
        {
            "label": "آبی تیره",
            "name": "Twilight Blue",
            "hex": "#6a7a8c"
        },
        {
            "label": "خاکستری",
            "name": "Carbon Gray",
            "hex": "#625D5D"
        },
        {
            "label": "سفید",
            "name": "Pebble White",
            "hex": "#f0e9da"
        },
        {
            "label": "آبی",
            "name": "Sea Blue",
            "hex": "#006994"
        },
        {
            "label": "مشکی",
            "name": "Power Black",
            "hex": "#01030E"
        },
        {
            "label": "زرد",
            "name": "POCO Yellow",
            "hex": "#ffd400"
        },
        {
            "label": "آبی",
            "name": "Cool Blue",
            "hex": "#71c7ec"
        },
        {
            "label": "مشکی",
            "name": "Carbon Black",
            "hex": "#545351"
        },
        {
            "label": "سبز",
            "name": "Coral Green",
            "hex": "#c8ecc7"
        },
        {
            "label": "آبی",
            "name": "Metallic Blue",
            "hex": "#32527b"
        },
        {
            "label": "آبی",
            "name": "Bubblegum Blue",
            "hex": "#2035d7"
        },
        {
            "label": "صورتی",
            "name": "Peach Pink",
            "hex": "#FF9899"
        },
        {
            "label": "سفید",
            "name": "Snowflake White",
            "hex": "#E4E2DD"
        },
        {
            "label": "سفید",
            "name": "Astral White",
            "hex": "#D1D1D9"
        },
        {
            "label": "آبی",
            "name": "Bifrost Blue",
            "hex": "#5286D8"
        },
        {
            "label": "آبی",
            "name": "Royal Blue",
            "hex": "#4169e1"
        },
        {
            "label": "خاکستری",
            "name": "Shadow Gray",
            "hex": "#595953"
        },
        {
            "label": "نقره ای",
            "name": "Silver",
            "hex": "#c0c0c0"
        },
        {
            "label": "زرد",
            "name": "Cyber Yellow",
            "hex": " #ffd300"
        },
        {
            "label": "نقره ای",
            "name": "Knight Silver",
            "hex": " #C3D2E1"
        },
        {
            "label": "مشکی",
            "name": "Stealth Black",
            "hex": " #3c3c3e"
        },
        {
            "label": "بنفش",
            "name": "Purple",
            "hex": " #800080"
        },
        {
            "label": "آبی",
            "name": "Laser Blue",
            "hex": " #144b9f"
        },
        {
            "label": "مشکی",
            "name": "Laser Black",
            "hex": " #010203"
        },
        {
            "label": "آبی",
            "name": "Deep Ocean Blue",
            "hex": " #0D395A"
        },
        {
            "label": "نقره ای",
            "name": "Moonlight Silver",
            "hex": " #CDCDCD"
        },
        {
            "label": "سفید",
            "name": "Arctic White",
            "hex": " #F2F2F2"
        },
        {
            "label": "مشکی",
            "name": "Midnight",
            "hex": " #1E1F22"
        },
        {
            "label": "سفید",
            "name": "Starlight",
            "hex": " #EBECE0"
        },
        {
            "label": "سبز",
            "name": "Alpine Green",
            "hex": " #456549"
        },
        {
            "label": "طلايی",
            "name": "Gold",
            "hex": " #ffd900"
        },
        {
            "label": "آبی",
            "name": "Sierra Blue",
            "hex": " #64A2C3"
        }
    ]
}


def gettrtredis():
    tmplist = list()
    with RedisConnection() as redis:
        keys_of_redis = redis.client.keys()
        for key in keys_of_redis:
            val = redis.client.hget(key, "hex")
            if not val:
                tmplist.append(key)
    return tmplist


def update_redis_database():
    list_of_words = mock
    with RedisConnection() as redis_db:
        for key, value in list_of_words.items():
            for in_key, in_value in value.items():
                redis_db.client.hset(key, in_key, in_value)


# colors = [
#     {
#         "color": "Nebula Green",
#         "fa": "سبز",
#         "HEX Code": "#80cba4"
#     },
#     {
#         "color": "Space Black",
#         "fa": "مشکی",
#         "HEX Code": "#212321"
#     },
#     {
#         "color": "Cosmic White",
#         "fa": "سفید",
#         "HEX Code": "#ffffff"
#     },
#     {
#         "color": "Thunder Purple",
#         "fa": "بنفش",
#         "HEX Code": "#351374"
#     },
#     {
#         "color": "Deep space blue ",
#         "fa": "آبی",
#         "HEX Code": "#237b9e"
#     },
#     {
#         "color": "Nebula Purpel",
#         "fa": "بنفش کهکشانی ",
#         "HEX Code": "#351374"
#     }
# ]
#
#
# with RedisConnection() as redis_db:
#     for color in colors:
#         key = color.get("color")
#         value = {"en_us": key, "fa_ir": color.get("fa"), 'hex': color.get("HEX Code")}
#         for in_key, in_value in value.items():
#             redis_db.client.hset(key, in_key, in_value)


class RamStorageTranslater:
    def __init__(self, Phrase: str, lang: str):
        self.english_numbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
        self.Phrase = Phrase
        self.lang = lang

    def translate(self) -> str:
        with RedisConnection() as redis_db:
            self.Phrase = self.Phrase.split(" ")
            list_of_numbers = list(str(self.Phrase[0]))
            translated_list = [self.english_numbers[int(num)] for num in
                               list_of_numbers] if self.lang == 'fa_ir' else list_of_numbers
            translated_word = redis_db.client.hget(self.Phrase[1], self.lang)
            translated_list += [" "] + [translated_word]
            return "".join(translated_list)

# if __name__ == '__main__':
#     z = gettrtredis()
#     w = 0
#     a = ['Onyx', 'Glacier Blue', 'Phantom White', 'Onyx Gray', "Bronze"]

# from deep_translator import GoogleTranslator
# from tqdm import tqdm
#
# from app.helpers.mongo_connection import MongoConnection
#
#
# def words_getter():
#     with MongoConnection() as mongo:
#         words_list = list()
#         words_list.extend(mongo.kowsar_collection.distinct("main_category"))
#         words_list.extend(mongo.kowsar_collection.distinct("sub_category"))
#         words_list.extend(mongo.kowsar_collection.distinct("brand"))
#         words_list.extend(mongo.kowsar_collection.distinct("config.color"))
#         words_list.extend(mongo.kowsar_collection.distinct("config.guarantee"))
#         return words_list
#
#
# def words_to_dict(words):
#     words_dict = dict()
#     for i in tqdm(range(len(words))):
#         if words[i]:
#             words_dict[words[i]] = translate(words[i])
#     print(words_dict)
#
#
# def translate(word):
#     translator = GoogleTranslator(source='en', target='fa')
#     return translator.translate(word)


# def words_setter():
#     data = {'Accessory': 'اکسسوری', 'Component': 'کامپوننت', 'Device': 'دستگاه', 'Network': 'شبکه',
#             'Office Machines': 'ماشین های اداری', 'Access Point': 'اکسس پوینت', 'All in One': 'کامپیوتر همه کاره',
#             'BackPack/HandyBag': 'کوله پشتی/کیف دستی', 'Band': 'بند', 'Barcode Reader': 'بارکدخوان',
#             'Battery': 'باتری',
#             'CPU': 'پردازنده', 'CPU FAN': 'فن پردازنده', 'Cable': 'کابل', 'Camera': 'دوربین', 'Cartridge': 'کارتریج',
#             'Case': 'کیس',
#             'Charger': 'شارژر', 'Converter': 'مبدل', 'Cooling': 'خنک کننده', 'Copy-Machine': 'دستگاه کپی',
#             'Cover/Case': 'محافظ/قاب', 'Data Video Projector': ' ویدئو پروژکتور', 'External DVD': 'دی وی دی خارجی',
#             'External HDD': 'هارد خارجی', 'External SSD': 'اس اس دی خارجی', 'Fax': 'فکس',
#             'Flash Memory': 'فلش مموری',
#             'Gajet': 'گجت', 'Game Console': 'کنسول بازی', 'Game/Software': 'بازی/نرم افزار', 'Gaming': 'گیمینگ',
#             'Graphic Card': 'کارت گرافیک', 'Headphone/Headset/Hands Free': 'هدفون / هدست / هندزفری',
#             'Internal DVD': 'دی وی دی داخلی', 'Internal HDD': 'هارد داخلی', 'Internal SSD': 'اس اس دی داخلی',
#             'Keyboard': 'صفحه کلید', 'Keyboard & Mouse': 'صفحه کلید و ماوس', 'LAN Card': 'کارت شبکه',
#             'Memory Card/Stick': 'کارت حافظه', 'Mobile': 'موبایل', 'Modem': 'مودم', 'Monitor': 'مانیتور',
#             'Motherboard': 'مادربرد', 'Mouse': 'ماوس', 'Mouse Pad': 'پد ماوس', 'NB Battery': 'باتری NB',
#             'Notebook': 'نوت بوک', 'PC': 'کامپیوتر', 'Power Port': 'چند راهی برق', 'Power Supply': 'منبع تغذیه',
#             'PowerBank': 'پاوربانک', 'Printer': 'چاپگر', 'RAM': 'رم', 'Scanner': 'اسکنر',
#             'Screen Protector': 'محافظ صفحه',
#             'Server': 'سرور', 'Speaker': 'اسپیکر', 'Stand/Holder': 'پایه / استند', 'Switch/Router': 'سوئیچ/روتر',
#             'TV': 'تلویزیون', 'Tablet': 'تبلت', 'Telephone': 'تلفن', 'USB HUB': 'هاب یو اس بی',
#             'Vacuum Cleaner': 'جارو برقی',
#             'Watch': 'ساعت', 'WebCam': 'وبکم', 'ANKER Cable': 'کابل انکر', 'Android box': 'باکس اندروید',
#             'Apple cable': 'کابل اپل', 'Cable ProOne': 'کابل پرو وان', 'Charger ANKER': 'شارژر انکر',
#             'Charger Energizer': 'شارژر انرژایزر', 'Charger Koluman': 'شارژر کلومن',
#             'Charger ProOne': 'شارژر پرو وان',
#             'Charger TSCO': 'شارژر تسکو', 'Charger Xiaomi': 'شارژر شیائومی', 'Dongle  ProOne': 'دانگل پرو وان',
#             'EarBuds Xiaomi': 'ایربادز شیائومی', 'Energizer Cable': 'کابل انرجایزر',
#             'Flash Memory SanDisk': 'فلش مموری سن دیسک', 'Gajet ProOne': 'گجت پرو وان', 'Glass': 'محافظ صفحه نمایش',
#             'HDD CoverProOne': 'کاور هارد پرو وان', 'HDD WD': 'هارد وسترن دیجیتال', 'Headphone ANKER': 'هدفون انکر',
#             'Headphone Apple': 'هدفون اپل', 'Headphone JBL': 'هدفون جی بی ال', 'Headphone Koluman': 'هدفون کلومن',
#             'Headphone ProOne': 'هدفون پرو وان', 'Headphone TSCO': 'هدفون تسکو', 'Headset Haylou': 'هدست هایلو',
#             'Headset Logitech': 'هدست لاجیتک', 'Holder Koluman': 'نگهدارنده کلومن', 'Honor Band': 'بند آنر',
#             'Huawei': 'هواوی', 'Keyboard Logitech': 'صفحه کلید لاجیتک', 'Koluman Cable': 'کابل کلومن',
#             'Koluman Power Port': 'چند راهی برق کلومن', 'Mobile Apple': 'موبایل اپل', 'Mobile Blu': 'موبایل بلو',
#             'Mobile CAT': 'موبایل کت', 'Mobile Energizer': 'انرجایزر موبایل', 'Mobile G Plus': 'موبایل جی پلاس',
#             'Mobile Honor': 'موبایل آنر', 'Mobile Huawei': 'موبایل هواوی', 'Mobile LG': 'موبایل ال جی',
#             'Mobile Nokia': 'موبایل نوکیا', 'Mobile OROD': 'موبایل اورود', 'Mobile Realme': 'موبایل ریلمی',
#             'Mobile Smart': 'موبایل اسمارت', 'Mobile Sumsung': 'موبایل سامسونگ', 'Mobile Xiaomi': 'موبایل کلومن',
#             'Mouse Logitech': 'ماوس لاجیتک', 'MousePad Logitech': 'ماوس پد لاجیتک',
#             'Notebook Lenovo': 'نوت بوک لنوو',
#             'Omthing': 'Omthing', 'Other Stand/Holder': 'پایه / استند دیگر',
#             'Power Converter  ProOne': 'مبدل برق پرو وان', 'PowerBank  ProOne': 'پاوربانک پرو وان',
#             'PowerBank ANKER': 'پاوربانک انکر', 'PowerBank Koluman': 'پاوربانک کلومن',
#             'PowerBank TSCO': 'پاوربانک تسکو',
#             'PowerBank Xiaomi': 'پاوربانک شیائومی', 'Racing': 'فرمان', 'Samsung case': 'قاب سامسونگ',
#             'SanDisk Memory': 'حافظه سن دیسک', 'Scale': 'ترازو', 'Speaker ANKER': 'اسپیکر انکر',
#             'Speaker Koluman': 'اسپیکر کلومن', 'Speaker Logitech': 'اسپیکر لاجیتک',
#             'Speaker ProOne': 'اسپیکر پرو وان',
#             'Speaker TSCO': 'اسپیکر تسکو', 'Speaker Xiaomi': 'اسپیکر شیائومی',
#             'Stand/Holder  ProOne': 'استند/پایه پرو وان', 'TSCO Cable': 'کابل تسکو', 'Tablet Lenovo': 'تبلت لنوو',
#             'Tablet SAMSUNG': 'تبلت سامسونگ', 'Vacuum Cleaner Xiaomi': 'جاروبرقی شیائومی',
#             'Watch Amazfit': 'ساعت امیزفیت', 'Watch Haylou': 'Haylou ساعت ',
#             'Watch Omthing': 'ساعت اومتینگ', 'Watch Xiaomi': 'ساعت شیائومی ', 'Xiaomi Band': 'بند شیائومی',
#             'Xiaomi Cable': 'کابل شیائومی', 'Xiaomi Case': 'قاب شیائومی', 'aura glow': 'هفت رنگ',
#             'bedone rang': 'بدون رنگ', 'black': 'سیاه', 'black red': 'قرمز مشکی', 'black/blue': 'آبی مشکی',
#             'black/red': 'قرمز مشکی', 'blue': 'آبی', 'boronz': 'برنز', 'breathing crystal': 'آبی گوهری',
#             'bronze': 'برنز', 'brown': ' قهوه ای', 'charcoal': 'ذغالی', 'color': 'رنگ', 'coral': 'مرجانی',
#             'cyan': 'فیروزه ای', 'dark blue': 'آبی تیره', 'dark nebula': 'بنفش کیهانی', 'dark night': 'مشکی',
#             'dusk': 'بنفش', 'fjord': 'آبی', 'gold': 'طلایی', 'gold black': 'طلایی تیره',
#             'gold coffe': 'قهوه ای طلایی',
#             'gray': 'خاکستری', 'green': 'سبز', 'haze silver': ' نقره ای مات', 'ice': 'یخی',
#             'iceberg blue': 'آبی یخی',
#             'military': 'چریکی', 'mix': 'میکس', 'ocean blue': 'آبی اقیانوسی', 'olive': 'زیتونی', 'orange': 'نارنجی',
#             'pink': ' صورتی', 'purple': ' بنفش', 'red': 'قرمز', 'rose gold': 'رزگلد', 'sand': 'شنی',
#             'silver': 'نقره اي', 'titanium': 'تیتانیوم', 'violet': 'بنفش', 'white': 'سفید', 'white red': 'قرمز سفید',
#             'white/blue': 'آبی سفید', 'white/red': 'قرمز سفید', 'yellow': ' زرد', 'aban digi': 'آبان دیجی',
#             'abandigi': 'آبان دیجی', 'asli': 'اصلی', 'awat': 'آوات', 'life time': 'مادام العمر', 'nabeghe': 'نابغه',
#             'nog': 'بدون گارانتی',
#             'sazgar': 'سازگار', 'sherkati': 'شرکتی', 'sherkati 01': 'شرکتی ۰۱'}
#     with MongoConnection() as mongo:
#         result = mongo.kowsar_collection.find({}, {"_id": 0})
#         for i in result:
#             new_result = i.copy()
#             new_result["main_category"] = data.get(i["main_category"])
#             new_result["sub_category"] = data.get(i["sub_category"])
#             new_result["brand"] = data.get(i["sub_category"])
#             if not new_result["config"]:
#                 pass
#             new_result["config"]["color"] = data.get(i.get("config", {}).get("color"))
#             new_result["config"]["guarantee"] = data.get(i.get("config", {}).get("guarantee"))
#             mongo.db["kowsar_collection_fa"].insert_one(new_result)
