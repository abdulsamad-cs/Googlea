import datetime

from googleads import adwords

from googleadwordssamad.celery_tasks import app
from googleadwordssamad.myproject.models import AdwordsCampaign, KeywordPerformanceReportModel, \
    CampaignPerformanceReportModel

client = adwords.AdWordsClient.LoadFromStorage()
NOT_ENTERED = -999


def getDate(str):
    from datetime import date, timedelta
    start = None
    end = None
    print(str)
    if str == 'Today':
        start = date.today().strftime('%Y-%m-%d')
        end = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    elif str == 'Yesterday':
        start = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        end = date.today().strftime('%Y-%m-%d')
    elif str == 'Last 7 days':
        start = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        end = date.today().strftime('%Y-%m-%d')
    elif str == 'Last 14 days':
        start = (date.today() - timedelta(days=14)).strftime('%Y-%m-%d')
        end = date.today().strftime('%Y-%m-%d')
    elif str == 'Last 30 days':
        start = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        end = date.today().strftime('%Y-%m-%d')
    elif str == 'This Month':
        start = date.today().replace(day=1).strftime('%Y-%m-%d')
        end = date.today().strftime('%Y-%m-%d')
    elif str == 'Last Month':
        start = date.today().replace(month=(date.today().month - 1) % 12, day=1).strftime('%Y-%m-%d')
        end = (date.today().replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')

    return start, end


def update_campaign_status(campaign_id, status):
    # Initialize appropriate service.
    campaign_service = client.GetService('CampaignService', version='v201809')

    # Construct operations and update campaign.
    operations = [{
        'operator': 'SET',
        'operand': {
            'id': campaign_id,
            'status': status
        }
    }]
    campaign_service.mutate(operations)


def update_keyword_status(keyword_id, status):
    # print(ad_group_id, keyword_id, status, "[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[")
    # Initialize appropriate service.
    ad_group_criterion_service = client.GetService(
        'AdGroupCriterionService', version='v201809')
    ad_group_id = KeywordPerformanceReportModel.objects.get(Id=keyword_id).AdGroupId

    # Construct operations and update bids.

    operations = [{
        'operator': 'SET',
        'operand': {
            'xsi_type': 'BiddableAdGroupCriterion',
            'adGroupId': ad_group_id,
            'criterion': {
                'id': keyword_id,
            },
            'userStatus': status,
        }
    }]

    ad_group_criterion_service.mutate(operations)


def update_adgroup_status(ad_group_id, status):
    ad_group_service = client.GetService('AdGroupService', version='v201809')

    # Construct operations and update an ad group.
    operations = [{
        'operator': 'SET',
        'operand': {
            'id': ad_group_id,
            'status': status,
        }
    }]
    print("********DEBUGGING 1****** : Adgroup id=", ad_group_id)
    ad_group_service.mutate(operations)
    print("******* Complete 1****** : Adgroup id=", ad_group_id)


def update_campaign_labels(campaign_id, operation, labels):
    # Initialize appropriate service.
    campaign_service = client.GetService('CampaignService', version='v201809')
    # Construct operations and update campaign.
    label_service = client.GetService('LabelService', version='v201809')
    label_id = None
    if operation == 'ADD':
        try:
            LabelOperation = [{
                'operator': operation,
                'operand': {'xsi_type': 'TextLabel', 'name': labels}
            }]
            print("doing===")
            response = label_service.mutate(LabelOperation)
            label_id = response['value'][0]['id']
            print(response['value'][0]['id'])
        except Exception as e:
            print(e)
            print("Sorry Try again.")
            # a = CampaignPerformanceReportModel.objects.get(Labels__icontains=labels).LabelIds
            # index = eval(a.Labels).index(labels)
            # label_id = eval(a.LabelIds)[index]
        else:
            operations = [{
                'operator': operation,
                'operand': {
                    'campaignId': campaign_id,
                    'labelId': label_id
                }
            }]
            result = campaign_service.mutateLabel(operations)
    else:
        a = CampaignPerformanceReportModel.objects.get(Labels__icontains=labels).LabelIds
        index = eval(a.Labels).index(labels)
        label_id = eval(a.LabelIds)[index]
        LabelOperation = [{
            'operator': operation,
            'operand': {'xsi_type': 'TextLabel', 'name': labels, 'label_id': label_id}
        }]
        response = label_service.mutate(LabelOperation)


def update_keyword_labels(keyword_id, operation, labels):
    # Initialize appropriate service.
    keyword_service = client.GetService('AdGroupCriterionService', version='v201809')
    # Construct operations and update campaign.
    label_service = client.GetService('LabelService', version='v201809')
    ad_group_id = KeywordPerformanceReportModel.objects.get(Id=keyword_id).AdGroupId
    label_id = None
    if operation == 'ADD':
        try:
            LabelOperation = [{
                'operator': operation,
                'operand': {'xsi_type': 'TextLabel', 'name': labels}
            }]
            print("doing===")
            response = label_service.mutate(LabelOperation)
            label_id = response['value'][0]['id']
            print(response['value'][0]['id'])
        except Exception as e:
            print(e)
            print("Sorry Try again.")
            # a = CampaignPerformanceReportModel.objects.get(Labels__icontains=labels).LabelIds
            # index = eval(a.Labels).index(labels)
            # label_id = eval(a.LabelIds)[index]
        else:
            operations = [{
                'operator': operation,
                'operand': {
                    'adGroupId': ad_group_id,
                    'criterionId': keyword_id,
                    'labelId': label_id
                }
            }]
            result = keyword_service.mutateLabel(operations)
    else:
        a = CampaignPerformanceReportModel.objects.get(Labels__icontains=labels).LabelIds
        index = eval(a.Labels).index(labels)
        label_id = eval(a.LabelIds)[index]
        LabelOperation = [{
            'operator': operation,
            'operand': {'xsi_type': 'TextLabel', 'name': labels, 'label_id': label_id}
        }]
        response = label_service.mutate(LabelOperation)


def update_adgroup_labels(ad_group_id, operation, labels):
    # Initialize appropriate service.
    adgroup_service = client.GetService('AdGroupService', version='v201809')
    # Construct operations and update campaign.
    label_service = client.GetService('LabelService', version='v201809')
    label_id = None
    if operation == 'ADD':
        try:
            LabelOperation = [{
                'operator': operation,
                'operand': {'xsi_type': 'TextLabel', 'name': labels}
            }]
            print("doing===")
            response = label_service.mutate(LabelOperation)
            label_id = response['value'][0]['id']
            print(response['value'][0]['id'])
        except Exception as e:
            print(e)
            print("Sorry Try again.")
            # a = CampaignPerformanceReportModel.objects.get(Labels__icontains=labels).LabelIds
            # index = eval(a.Labels).index(labels)
            # label_id = eval(a.LabelIds)[index]
        else:
            operations = [{
                'operator': operation,
                'operand': {
                    'adGroupId': ad_group_id,
                    'labelId': label_id
                }
            }]
            result = adgroup_service.mutateLabel(operations)
    else:
        a = CampaignPerformanceReportModel.objects.get(Labels__icontains=labels).LabelIds
        index = eval(a.Labels).index(labels)
        label_id = eval(a.LabelIds)[index]
        LabelOperation = [{
            'operator': operation,
            'operand': {'xsi_type': 'TextLabel', 'name': labels, 'label_id': label_id}
        }]
        response = label_service.mutate(LabelOperation)


def increaseCPCbids():
    pass


def decreaseCPCbids():
    pass


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

    ad_groups = ad_group_service.mutate(operations)


def PauseAdGroups(ad_group_id):
    # Initialize appropriate service.
    ad_group_service = client.GetService('AdGroupService', version='v201809')

    # Construct operations and update an ad group.
    operations = [{
        'operator': 'SET',
        'operand': {
            'id': ad_group_id,
            'status': 'PAUSED',
        }
    }]

    ad_group_service.mutate(operations)


def EnableAdGroups(ad_group_id):
    # Initialize appropriate service.
    ad_group_service = client.GetService('AdGroupService', version='v201809')

    # Construct operations and update an ad group.
    operations = [{
        'operator': 'SET',
        'operand': {
            'id': ad_group_id,
            'status': 'ENABLED',
        }
    }]

    ad_group_service.mutate(operations)


def PAUSE_CAMPAIGN(campaign_id):
    # Initialize appropriate service.
    campaign_service = client.GetService('CampaignService', version='v201809')

    # Construct operations and update campaign.
    operations = [{
        'operator': 'SET',
        'operand': {
            'id': campaign_id,
            'status': 'PAUSED'
        }
    }]
    campaign_service.mutate(operations)


def enable_pause_all_adgroups_based_on_conversion(campaign_name, data_report):
    campaignid = AdwordsCampaign.objects.get(name=campaign_name).campaign_id

    for key, val in data_report.items():
        if val[9] == campaignid:
            if float(val[2]) < 10:
                PauseAdGroups(key[0])
                print("making pause")
            else:
                EnableAdGroups(key[0])
                print("making enable")


def pause_adgroup_based_on_ctr_and_current_date(adgroup_name, CTR, DATE, data_report):
    for key, val in data_report.items():
        if val[5] == adgroup_name and float(val[6].strip('%')) < CTR and datetime.datetime.now().date() == DATE:
            PauseAdGroups(key[0])


'''
def pause_keyword_based_on_cpc(keyword,MAX_CPC,data_report):
    for key, val in data_report.items():
        if val[0] == keyword and int(val[3]) > MAX_CPC:
            pass
            #PAUSEKEYWORD(key[0], key[1])


def pause_keyword_based_on_impressions(keyword,MIN_Impressions,data_report):
    for key, val in data_report.items():
        if val[0] == keyword and int(val[3]) < MIN_Impressions:
            pass
            #PAUSEKEYWORD(key[0], key[1])
'''


#
# @app.task
# def update_keyword_based_on_rule(keyword_id, group_id, action, max_cpc, max_impressions, data_report):
#     cpc_on_platform = data_report[3]  # cpc cost
#     impressions_on_platform = data_report[1]  # impressions
#     if max_cpc != NOT_ENTERED:
#         if int(cpc_on_platform) > max_cpc:
#             update_keyword(group_id, keyword_id, action)
#     if impressions_on_platform != NOT_ENTERED:
#         if int(impressions_on_platform) < max_impressions:
#             update_keyword(group_id, keyword_id, action)


def get_all_campaign(client):
    PAGE_SIZE = 100
    # Initialize appropriate service.
    campaign_service = client.GetService('CampaignService', version='v201809')

    # Construct selector and get all campaigns.
    offset = 0
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'paging': {
            'startIndex': str(offset),
            'numberResuglts': str(PAGE_SIZE)
        }
    }

    more_pages = True
    while more_pages:
        page = campaign_service.get(selector)

        # Display results.
        if 'entries' in page:
            for campaign in page['entries']:
                try:
                    obj = AdwordsCampaign.objects.get(campaign_id=campaign['id'])
                except AdwordsCampaign.DoesNotExist:
                    obj = AdwordsCampaign()
                obj.campaign_id = campaign['id']
                obj.name = campaign['name']
                obj.budget = campaign['budget']
                obj.start_date = campaign['startDate']
                obj.end_date = campaign['endDate']
                obj.status = campaign['status']
                obj.save()

                print('Campaign with id "%s", name "%s",startdate "%s", and status "%s" was ' 'found.' % (
                    campaign['id'], campaign['name'], campaign['startDate'], campaign['status']))
                print('(IN DB)Campaign with id "%s", name "%s",startdate "%s", and status "%s" was ' 'saved.' % (
                    obj.campaign_id, obj.name, obj.start_date, obj.status))

        else:
            print('No campaigns were found.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])


'''
@app.task
def update_adgroup_based_on_rule(group_id, action,max_ctr, location,target_date, data_report):
    ctr_on_platform=data_report[6] #cpc cost
    impressions_on_platform=data_report[1] #impressions
    if max_cpc!=NOT_ENTERED:
        if int(cpc_on_platform) > max_cpc:
            update_keyword(group_id,keyword_id,action)
    if impressions_on_platform!=NOT_ENTERED:
        if int(impressions_on_platform) < max_impressions:
            update_keyword(group_id, keyword_id, action)

def pause_campaign_based_on_date_intervals(campaign_name,start_time,end_time,data_report):
    now=datetime.datetime.now()
    for key, val in data_report.items():
        if val[8] == campaign_name and now.hour>=start_time and now.hour<=end_time:
            PAUSE_CAMPAIGN(val[9])


'''
if __name__ == '__main__':
    client = adwords.AdWordsClient.LoadFromStorage()
    get_all_campaign(client)
