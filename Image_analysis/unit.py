platform1 = ['iOS', 'Android']
platform_type = platform1[0]

urlType1 = ['Malicious', 'Benign']
urlType = urlType1[0]

appType1 = ['APP', 'Browser']
appType = appType1[0]

# urlfileType = ['csv','txt']
region1 = ['china', 'phishtank', 'Tranco']
region = region1[1]

# urlSetType1 = ['Malicious_url', 'Benign_url']
urlSetType = f"{urlType}_url"

# urlSet = '/phishtank/url501-600.csv'

base_location = "E:/"

page_load_time = 2
page_load_max_time = 20
little_time = 0.3

# init_counter = 500
start_counter = 551
end_counter = 600

database_host = '10.130.183.146'
# database_host = '192.168.0.108'

phone_id = '1C071FDF60020H'

VPN_region = ['DIRECT', '香港', '日本', '新加坡', '美国']
vpn_global = VPN_region[0]

split_words = '$^&$'

allow_list = ['301', '302', '400', '401', '404', '408', '检查网络']

'301$^&$302$^&$400$^&$401$^&$404$^&$408$^&$检查网络'