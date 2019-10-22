from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from googleads import adwords

logger = get_task_logger(__name__)

client = adwords.AdWordsClient.LoadFromStorage("/home/oem/Documents/va8ive/googleadwordssamad/google-ads.yaml")


# @app.task
def get_all_campaign():
    PAGE_SIZE = 100
    # Initialize appropriate service.
    campaign_service = client.GetService('CampaignService', version='v201809')

    # Construct selector and get all campaigns.
    offset = 0
    selector = {
        'fields': ['Id', 'Name', 'Status'],
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
                # try:
                #     obj = AdwordsCampaign.objects.get(campaign_id=campaign['id'])
                # except AdwordsCampaign.DoesNotExist:
                #     obj = AdwordsCampaign()
                # obj.campaign_id = campaign['id']
                # obj.name = campaign['name']
                # obj.budget = campaign['budget']
                # obj.start_date = campaign['startDate']
                # obj.end_date = campaign['endDate']
                # obj.status = campaign['status']
                # obj.save()

                # print('Campaign with id "%s", name "%s",startdate "%s", and status "%s" was ' 'found.' % (campaign['id'], campaign['name'],campaign['startDate'],campaign['status']))
                # print('(IN DB)Campaign with id "%s", name "%s",startdate "%s", and status "%s" was ' 'saved.' % (obj.campaign_id, obj.name,obj.start_date,obj.status))

        else:
            print('No campaigns were found.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])
