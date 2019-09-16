from __future__ import absolute_import, unicode_literals
from googleadwordssamad.celery_tasks import app
from googleads import adwords
from .add_budget import AddBudget
#from adwords_campaign.helpers import AddBudget, GetCampaigns
#import logging

#logger = logging.getLogger(__name__)

client = adwords.AdWordsClient.LoadFromStorage()
@app.task
def AddCampaign(campaign_name, status, ad_channel, start_date, end_date,budget):
    campaign_service = client.GetService('CampaignService')
    client.SetClientCustomerId(client.client_customer_id)
    budget_id = AddBudget(client, budget)

    try:

        operations = [{
            'operator': 'ADD',
            'operand': {
                'name': campaign_name,
                'status': status,
                'biddingStrategyConfiguration': {
                    'biddingStrategyType': 'MANUAL_CPC',
                    'biddingScheme': {
                        'xsi_type': 'ManualCpcBiddingScheme',
                        'enhancedCpcEnabled': 'false'
                    }
                },

                'budget': {
                    'budgetId': budget_id
                },
                'advertisingChannelType': ad_channel
                ,
                'startDate': start_date,
                'endDate': end_date,
            }
        }]

        campaign_service.mutate(operations)
    except Exception as ex:
        print("Error:")

