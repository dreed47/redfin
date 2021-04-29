from redfin import Redfin
import pprint

pp = pprint.PrettyPrinter(indent=4)

client = Redfin()

#address = '4544 Radnor St, Detroit Michigan'
#address = '224 Old Farm Rd, Cranberry Twp, PA 16066'
#address = '217 Northfield Rd, Cranberry Twp, PA 16066'
#address = '14512 Limestone Ln, Pineville, NC 28134'
address = '1712 Glen Echo Rd Unit C,Nashville, TN 37215'

response = client.search(address)
url = response['payload']['exactMatch']['url']
initial_info = client.initial_info(url)

property_id = initial_info['payload']['propertyId']
mls_data = client.below_the_fold(property_id)
above_the_fold = client.above_the_fold(property_id, "")
info_panel = client.info_panel(property_id, "")

if 'url' in info_panel["payload"]["mainHouseInfo"]:
    refinUrl = 'https://www.redfin.com' + \
        info_panel["payload"]["mainHouseInfo"]['url']
else:
    redfinUrl = 'Not Set'

if 'streetViewUrl' in above_the_fold["payload"]["mediaBrowserInfo"]["streetView"]:
    streetViewUrl = above_the_fold["payload"]["mediaBrowserInfo"]["streetView"]["streetViewUrl"]
else:
    streetViewUrl = 'Not Set'

if 'listingId' in initial_info['payload']:
    listing_id = initial_info['payload']['listingId']
    avm_details = client.avm_details(property_id, listing_id)
else:
    avm_details = client.avm_details(property_id, "")

if 'predictedValue' in avm_details["payload"]:
    predictedValue = avm_details["payload"]["predictedValue"]
else:
    predictedValue = 'Not Set'

if 'sectionPreviewText' in avm_details["payload"]:
    amountFormatted = avm_details["payload"]["sectionPreviewText"]
else:
    amountFormatted = 'Not Set'

pp.pprint(initial_info)
pp.pprint(mls_data)
pp.pprint(above_the_fold)
pp.pprint(avm_details)

print("...end of tests")
