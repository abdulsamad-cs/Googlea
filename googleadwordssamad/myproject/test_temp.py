from googleads import adwords
from googleadwordssamad import settings

from .models import CampaignPerformanceReportModel

PAGE_SIZE = 100
client = adwords.AdWordsClient.LoadFromStorage("/home/oem/Documents/va8ive/googleadwordssamad/google-ads.yaml")


def main(client):
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
            response = label_service.mutate(LabelOperation)
            label_id = response['value'][0]['id']
            print(response['value'][0]['id'])
        except Exception as e:
            print(e)
            print("Sorry Try again.")
            a = CampaignPerformanceReportModel.objects.get(Labels__icontains=labels).LabelIds
            index = eval(a.Labels).index(labels)
            label_id=eval(a.LabelIds)[index]
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
            'operand': {'xsi_type': 'TextLabel', 'name': labels,'label_id':label_id}
        }]
        response = label_service.mutate(LabelOperation)



if __name__ == '__main__':
    adwords_client = adwords.AdWordsClient.LoadFromStorage("/home/oem/Documents/va8ive/googleadwordssamad/google-ads.yaml")
    # main(adwords_client)
    update_campaign_labels('6454212146', 'ADD', 'Samad')
