#!/usr/bin/python
# coding: utf-8

# set default encodeing to utf-8

NONE_VALUE = '値なし'
SYMBOL_TEXT = '／'
TYPE_LOW_TEMPERATURE = '最低気温'
TYPE_HIGHT_TEMPERATURE = '最高気温'
YEAR_VIEW_FORMAT = '%Y年%m月%d日'
YEAR_VIEW_FORMAT_1 = '%d'
DATE_VIEW_FORMAT = '%m月%d日%H時'
HOUR_QUAKE_FORMAT = '%H時%M分'
HOUR_QUAKE_FORMAT_1 = '%H:%M'
AREA_DEFAULT = '東京都'

HOUR_FLOOD_FORMAT_1 = '%H:%M'


DEFAULT_TIMEZONE = 'Asia/Tokyo'
AREA_NOT_USE = [u'内陸',u'沿岸',u'東部',u'西部',u'会津', u'青森県', u'奄美地方'
	, u'美濃地方', u'飛騨地方',u'伊豆諸島', u'下北・三八上北',u'南部'
	,u'北部',u'中部・南部',u'壱岐・対馬',u'十勝地方',u'釧路・根室・十勝地方'
	,u'南部・北部・五島',u'伊豆諸島北部',u'伊豆諸島南部',u'小笠原諸島',u'三八上北',u'津軽・下北']
WEEK_DAY= ['月','火','水','木','金','土','日']
WEATHER_STATUS_IMAGES = {
    '晴れ':'100.png',
    '晴れ時々曇り': '101.png',
    '晴れ後曇り':'110.png',
    '晴れ後曇り':'111.png',
    '晴れ後雨':'112.png',
    '曇り':'200.png',
    '曇り時々晴れ':'201.png',
    '曇り時々雨':'202.png',
    '曇り時々雨':'203.png',
    '曇り後晴れ':'210.png',
    '曇り後晴れ':'211.png',
    '曇り後一時雨':'212.png',
    '雨時々止む':'302.png',
    '雨後曇り':'313.png'
}

STATION_RELATION_AREA = [
{'station_code': '35426', 'area_code': '060000'},
{'station_code': '93041', 'area_code': '473000'},
{'station_code': '44263', 'area_code': '130100'},
{'station_code': '64036', 'area_code': '290000'},
{'station_code': '83216', 'area_code': '440000'},
{'station_code': '49142', 'area_code': '190000'},
{'station_code': '68132', 'area_code': '320000'},
{'station_code': '34461', 'area_code': '40020'},
{'station_code': '92011', 'area_code': '472000'},
{'station_code': '31602', 'area_code': '20200'},
{'station_code': '87376', 'area_code': '450000'},
{'station_code': '66408', 'area_code': '330000'},
{'station_code': '20432', 'area_code': '014030'},
{'station_code': '11016', 'area_code': '011000'},
{'station_code': '33472', 'area_code': '030100'},
{'station_code': '67437', 'area_code': '340000'},
{'station_code': '40201', 'area_code': '080000'},
{'station_code': '43056', 'area_code': '110000'},
{'station_code': '33431', 'area_code': '030010'},
{'station_code': '88836', 'area_code': '460040'},
{'station_code': '46106', 'area_code': '140000'},
{'station_code': '36361', 'area_code': '070030'},
{'station_code': '52586', 'area_code': '210000'},
{'station_code': '14163', 'area_code': '016000'},
{'station_code': '74181', 'area_code': '390000'},
{'station_code': '69122', 'area_code': '310000'},
{'station_code': '48156', 'area_code': '200000'},
{'station_code': '65042', 'area_code': '300000'},
{'station_code': '71106', 'area_code': '360000'},
{'station_code': '55102', 'area_code': '160000'},
{'station_code': '88317', 'area_code': '460100'},
{'station_code': '91197', 'area_code': '471000'},
{'station_code': '63518', 'area_code': '280000'},
{'station_code': '61286', 'area_code': '260000'},
{'station_code': '44301', 'area_code': '130040'},
{'station_code': '45147', 'area_code': '120000'},
{'station_code': '62078', 'area_code': '270000'},
{'station_code': '94081', 'area_code': '474000'},
{'station_code': '56227', 'area_code': '170000'},
{'station_code': '19432', 'area_code': '014100'},
{'station_code': '53133', 'area_code': '240000'},
{'station_code': '57066', 'area_code': '180000'},
{'station_code': '86141', 'area_code': '430000'},
{'station_code': '44132', 'area_code': '130010'},
{'station_code': '82182', 'area_code': '400000'},
{'station_code': '54232', 'area_code': '150000'},
{'station_code': '36126', 'area_code': '070100'},
{'station_code': '12442', 'area_code': '012000'},
{'station_code': '73166', 'area_code': '380000'},
{'station_code': '51106', 'area_code': '230000'},
{'station_code': '60131', 'area_code': '250000'},
{'station_code': '34392', 'area_code': '040010'},
{'station_code': '23232', 'area_code': '017000'},
{'station_code': '72086', 'area_code': '370000'},
{'station_code': '81428', 'area_code': '350000'},
{'station_code': '17341', 'area_code': '013000'},
{'station_code': '31312', 'area_code': '020010'},
{'station_code': '50331', 'area_code': '220000'},
{'station_code': '41277', 'area_code': '090000'},
{'station_code': '21323', 'area_code': '015000'},
{'station_code': '32402', 'area_code': '050000'},
{'station_code': '85142', 'area_code': '410000'},
{'station_code': '42251', 'area_code': '100000'},
{'station_code': '84496', 'area_code': '420000'}
]

SUB_AREA_LIST = [
		{'sub_area_code': '017010', 'sub_area_name': u'渡島地方', 'area_code': '017000', 'area_name': u'渡島・檜山地方'},
		{'sub_area_code': '015010', 'sub_area_name': u'胆振地方', 'area_code': '015000', 'area_name': u'胆振・日高地方'},
		{'sub_area_code': '400010', 'sub_area_name': u'福岡地方', 'area_code': '400000', 'area_name': u'福岡県'},
		{'sub_area_code': '012010', 'sub_area_name': u'上川地方', 'area_code': '012000', 'area_name': u'上川・留萌地方'},
		{'sub_area_code': '474010', 'sub_area_name': u'石垣島地方', 'area_code': '474000', 'area_name': u'八重山地方'},
		{'sub_area_code': '013010', 'sub_area_name': u'網走地方', 'area_code': '013000', 'area_name': u'網走・北見・紋別地方'},
		{'sub_area_code': '016010', 'sub_area_name': u'石狩地方', 'area_code': '016000', 'area_name': u'石狩・空知・後志地方'},
		{'sub_area_code': '430010', 'sub_area_name': u'熊本地方', 'area_code': '430000', 'area_name': u'熊本県'},
		{'sub_area_code': '014020', 'sub_area_name': u'釧路地方', 'area_code': '014100', 'area_name': u'釧路・根室地方'},
		{'sub_area_code': '070010', 'sub_area_name': u'中通り', 'area_code': '070100', 'area_name': u'中通り・浜通り'},
		{'sub_area_code': '260010', 'sub_area_name': u'南部', 'area_code': '260000', 'area_name': u'京都府'},
		{'sub_area_code': '040010', 'sub_area_name': u'東部', 'area_code': '040000', 'area_name': u'宮城県'},
#		{'sub_area_code': '020010', 'sub_area_name': u'津軽', 'area_code': '020000', 'area_name': u'青森県'},
		{'sub_area_code': '020100', 'sub_area_name': u'津軽・下北', 'area_code': '020000', 'area_name': u'青森県'},
		{'sub_area_code': '030010', 'sub_area_name': u'内陸', 'area_code': '030000', 'area_name': u'岩手県'},
		{'sub_area_code': '050010', 'sub_area_name': u'沿岸', 'area_code': '050000', 'area_name': u'秋田県'},
		{'sub_area_code': '060010', 'sub_area_name': u'村山', 'area_code': '060000', 'area_name': u'山形県'},
		{'sub_area_code': '080010', 'sub_area_name': u'北部', 'area_code': '080000', 'area_name': u'茨城県'},
		{'sub_area_code': '090010', 'sub_area_name': u'南部', 'area_code': '090000', 'area_name': u'栃木県'},
		{'sub_area_code': '100010', 'sub_area_name': u'南部', 'area_code': '100000', 'area_name': u'群馬県'},
		{'sub_area_code': '110010', 'sub_area_name': u'南部', 'area_code': '110000', 'area_name': u'埼玉県'},
		{'sub_area_code': '120010', 'sub_area_name': u'北西部', 'area_code': '120000', 'area_name': u'千葉県'},
		{'sub_area_code': '140010', 'sub_area_name': u'東部', 'area_code': '140000', 'area_name': u'神奈川県'},
		{'sub_area_code': '150010', 'sub_area_name': u'下越', 'area_code': '150000', 'area_name': u'新潟県'},
		{'sub_area_code': '160010', 'sub_area_name': u'東部', 'area_code': '160000', 'area_name': u'富山県'},
		{'sub_area_code': '170010', 'sub_area_name': u'加賀', 'area_code': '170000', 'area_name': u'石川県'},
		{'sub_area_code': '180010', 'sub_area_name': u'嶺北', 'area_code': '180000', 'area_name': u'福井県'},
		{'sub_area_code': '190010', 'sub_area_name': u'中・西部', 'area_code': '190000', 'area_name': u'山梨県'},
		{'sub_area_code': '200010', 'sub_area_name': u'北部', 'area_code': '200000', 'area_name': u'長野県'},
		{'sub_area_code': '210010', 'sub_area_name': u'美濃地方', 'area_code': '210000', 'area_name': u'岐阜県'},
		{'sub_area_code': '220010', 'sub_area_name': u'中部', 'area_code': '220000', 'area_name': u'静岡県'},
		{'sub_area_code': '230010', 'sub_area_name': u'西部', 'area_code': '230000', 'area_name': u'愛知県'},
		{'sub_area_code': '240010', 'sub_area_name': u'北中部', 'area_code': '240000', 'area_name': u'三重県'},
		{'sub_area_code': '250010', 'sub_area_name': u'南部', 'area_code': '250000', 'area_name': u'滋賀県'},
		{'sub_area_code': '260010', 'sub_area_name': u'南部', 'area_code': '260000', 'area_name': u'京都府'},
		{'sub_area_code': '280010', 'sub_area_name': u'南部', 'area_code': '280000', 'area_name': u'兵庫県'},
		{'sub_area_code': '290010', 'sub_area_name': u'北部', 'area_code': '290000', 'area_name': u'奈良県'},
		{'sub_area_code': '300010', 'sub_area_name': u'北部', 'area_code': '300000', 'area_name': u'和歌山県'},
		{'sub_area_code': '310010', 'sub_area_name': u'東部', 'area_code': '310000', 'area_name': u'鳥取県'},
		{'sub_area_code': '320010', 'sub_area_name': u'東部', 'area_code': '320000', 'area_name': u'島根県'},
		{'sub_area_code': '330010', 'sub_area_name': u'南部', 'area_code': '330000', 'area_name': u'岡山県'},
		{'sub_area_code': '340010', 'sub_area_name': u'南部', 'area_code': '340000', 'area_name': u'広島県'},
		{'sub_area_code': '350010', 'sub_area_name': u'西部', 'area_code': '350000', 'area_name': u'山口県'},
		{'sub_area_code': '360010', 'sub_area_name': u'北部', 'area_code': '360000', 'area_name': u'徳島県'},
		{'sub_area_code': '380010', 'sub_area_name': u'中予', 'area_code': '380000', 'area_name': u'愛媛県'},
		{'sub_area_code': '390010', 'sub_area_name': u'中部', 'area_code': '390000', 'area_name': u'高知県'},
		{'sub_area_code': '400010', 'sub_area_name': u'福岡地方', 'area_code': '400000', 'area_name': u'福岡県'},
		{'sub_area_code': '410010', 'sub_area_name': u'南部', 'area_code': '410000', 'area_name': u'佐賀県'},
#		{'sub_area_code': '420010', 'sub_area_name': u'南部', 'area_code': '420000', 'area_name': u'長崎県'},
		{'sub_area_code': '420100', 'sub_area_name': u'南部・北部・五島', 'area_code': '420000', 'area_name': u'長崎県'},
		{'sub_area_code': '430010', 'sub_area_name': u'熊本地方', 'area_code': '430000', 'area_name': u'熊本県'},
		{'sub_area_code': '440010', 'sub_area_name': u'中部', 'area_code': '440000', 'area_name': u'大分県'},
		{'sub_area_code': '450010', 'sub_area_name': u'南部平野部', 'area_code': '450000', 'area_name': u'宮崎県'},
		{'sub_area_code': '460010', 'sub_area_name': u'薩摩地方', 'area_code': '460100', 'area_name': u'鹿児島県（奄美地方除く）'},
		{'sub_area_code': '471010', 'sub_area_name': u'本島中南部', 'area_code': '471000', 'area_name': u'沖縄本島地方'}
]

MAPPING_AREA_LABEL = [
    {'area_code': u'130010', 'area_name': u'東京地方' , 'label': u'東京都'},
    {'area_code': u'014100', 'area_name': u'釧路・根室地方' , 'label': u'釧路/根室'},
    {'area_code': u'460040', 'area_name': u'奄美地方' , 'label': u'奄美'},
    {'area_code': u'014030', 'area_name': u'十勝地方' , 'label': u'十勝'},
    {'area_code': u'011000', 'area_name': u'宗谷地方' , 'label': u'宗谷'},
    {'area_code': u'016000', 'area_name': u'石狩・空知・後志地方' , 'label': u'石狩/空知/後志'},
    {'area_code': u'014000', 'area_name': u'釧路・根室・十勝地方' , 'label': u'釧路/根室/十勝'},
    {'area_code': u'460100', 'area_name': u'鹿児島県（奄美地方除く）' , 'label': u'鹿児島県'},
    {'area_code': u'472000', 'area_name': u'大東島地方' , 'label': u'大東島'},
    {'area_code': u'013000', 'area_name': u'網走・北見・紋別地方' , 'label': u'網走/北見/紋別'},
    {'area_code': u'474000', 'area_name': u'八重山地方' , 'label': u'八重山'},
    {'area_code': u'017000', 'area_name': u'渡島・檜山地方' , 'label': u'渡島/檜山'},
    {'area_code': u'471000', 'area_name': u'沖縄本島地方' , 'label': u'沖縄本島'},
    {'area_code': u'473000', 'area_name': u'宮古島地方' , 'label': u'宮古島'},
    {'area_code': u'015000', 'area_name': u'胆振・日高地方' , 'label': u'胆振/日高'},
    {'area_code': u'012000', 'area_name': u'上川・留萌地方' , 'label': u'上川/留萌'},
    {'area_code': u'070100', 'area_name': u'中通り・浜通り' , 'label': u'福島県'},
    {'area_code': u'020010', 'area_name': u'津軽' , 'label': u'青森県'},
]
