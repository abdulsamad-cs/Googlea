from googleads import adwords

PAGE_SIZE = 100
client = adwords.AdWordsClient.LoadFromStorage()


def main():
    # Initialize appropriate service.
    campaign_service = client.GetService('CampaignService', version='v201809')

    # Construct selector and get all campaigns.
    offset = 0
    selector = {
        'fields': ['Id'],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        }
    }

    more_pages = True
    while more_pages:
        page = campaign_service.get(selector)

        # Display results.
        if 'entries' in page:
            for campaign in page['entries']:
                print(campaign)
                print("***********")
                # print('Campaign with id "%s", name "%s", and status "%s" was '
                #       'found.' % (campaign['id'], campaign['name'],
                #                   campaign['status']))
        else:
            print('No campaigns were found.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])


# def update_campaign_labels(campaign_id,operation, labels):
#     # Initialize appropriate service.
#     campaign_service = client.GetService('CampaignService', version='v201809')
#
#     # Construct operations and update campaign.
#
#     label_service = client.GetService('LabelService',version='v201809')
#     label_id=None
#     try:
#         LabelOperation=[{
#             'operator': operation,
#             'operand':  {'xsi_type':'TextLabel','name': labels}
#         }]
#         response=label_service.mutate(LabelOperation)
#         label_id=response['value'][0]['id']
#         print(response['value'][0]['id'])
#     except Exception as e:
#         print(e)
#         print("Sorry Try again.")
#         a=CampaignPerformanceReportModel.objects.get(Labels__icontains=labels).LabelIds
#         print(a)
#     else:
#         operations = [{
#             'operator': operation,
#             'operand': {
#                 'campaignId': campaign_id,
#                 'labelId': label_id
#             }
#         }]
#         result=campaign_service.mutateLabel(operations)
#         #print(result)

def setCPCbids(id, bid_micro_amount):
    # Initialize appropriate service.
    ad_group_service = client.GetService('AdGroupService', version='v201809')

    # Construct operations and update an ad group.
    operations = [{
        'operator': 'SET',
        'operand': {
            'id': id
        }
    }]

    if bid_micro_amount:
        operations[0]['operand']['biddingStrategyConfiguration'] = {
            'bids': [{
                'xsi_type': 'CpcBid',
                'bid': {
                    'microAmount': bid_micro_amount,
                }
            }]
        }

    ad_group_service.mutate(operations)


def setCPMbids(id, bid_micro_amount):
    # Initialize appropriate service.
    ad_group_service = client.GetService('AdGroupService', version='v201809')

    # Construct operations and update an ad group.
    operations = [{
        'operator': 'SET',
        'operand': {
            'id': id
        }
    }]

    if bid_micro_amount:
        operations[0]['operand']['biddingStrategyConfiguration'] = {
            'bids': [{
                'xsi_type': 'CpmBid',
                'bid': {
                    'microAmount': bid_micro_amount,
                }
            }]
        }

    ad_group_service.mutate(operations)


def setCPAbids(id, bid_micro_amount):
    # Initialize appropriate service.
    ad_group_service = client.GetService('AdGroupService', version='v201809')

    # Construct operations and update an ad group.
    operations = [{
        'operator': 'SET',
        'operand': {
            'id': id
        }
    }]

    if bid_micro_amount:
        operations[0]['operand']['biddingStrategyConfiguration'] = {
            'bids': [{
                'xsi_type': 'CpaBid',
                'bid': {
                    'microAmount': bid_micro_amount,
                }
            }]
        }

    ad_group_service.mutate(operations)


def increaseCPCbids():
    temp_list = set()
    # Initialize appropriate service.
    ad_group_bid_modifier_service = client.GetService(
        'AdGroupBidModifierService', version='v201809')

    # Get all ad group bid modifiers for the campaign.
    selector = {
        'fields': ['CampaignName', 'CampaignId', 'AdGroupId', 'BidModifier', 'Id'],
        "predicates": {
            "field": "CampaignStatus",
            "operator": "IN",
            "values": [
                "ENABLED",
                "PAUSED",
            ]
        },

    }

    # Set initial values.
    # offset, page = 0, {}
    # more_results = True

    # while more_results:
    page = ad_group_bid_modifier_service.get(selector)
    print(page)
    #
    # if page['entries']:
    #     # break
    #     for modifier in page['entries']:
    #         print(modifier)
    #         value = (modifier['bidModifier'] if 'bidModifier' in modifier
    #                  else 'unset')
    #         # print('Campaign ID %s, AdGroup ID %s, Criterion ID %s has ad group '
    #         #       'level modifier: %s' %
    #         #       (modifier['campaignId'], modifier['adGroupId'],
    #         #        modifier['criterion']['id'], value))
    #         temp_list.add(modifier['campaignId'])
    #
    #         # Increment values to request the next page.
    #         # offset += PAGE_SIZE
    #         # selector['paging']['startIndex'] = str(offset)
    # else:
    #     print('No ad group bid modifiers returned.')
    #     # more_results = int(page['totalNumEntries']) > offset
    # print("campaign ids: ", temp_list)


if __name__ == '__main__':
    adwords_client = adwords.AdWordsClient.LoadFromStorage()
    # main(adwords_client)
    # update_campaign_labels('6454212146', 'AD-D', 'Usa')
    setCPCbids('75822879265', 50000000)
    setCPMbids('75822879265', 50000000)
    setCPAbids('75822879265', 50000000)
    increaseCPCbids()

# Campaign ID 2030405009, AdGroup ID 72728417180, Criterion ID 30000 has ad group level modifier: None
