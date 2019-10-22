import pprint

Value_operand = {
    'BiddingStrategyType': [('Target CPA', 'TARGET_CPA'), ('Target ROAS', 'TARGET_ROAS'),
                            ('cpc', 'MANUAL_CPC'), ('cpv', 'MANUAL_CPV'), ('cpm', 'MANUAL_CPM'),
                            ('Maximum clicks', 'TARGET_SPEND'), ('Maximum Conversions', 'MAXIMIZE_CONVERSIONS'),
                            ('Maximum Conversion Value', 'MAXIMIZE_CONVERSION_VALUE'),
                            ('Target Outranking Share', 'TARGET_OUTRANK_SHARE')],
    'AdvertisingChannelType': [
        ('Search', 'SEARCH'), ('Display', 'DISPLAY'), ('Shopping', 'SHOPPING'), ('Video', 'VIDEO'),
        ('Multi Channel', 'MULTI_CHANNEL'), ('Express', 'EXPRESS')
    ],
    'KeywordMatchType': [
        ('Exact', 'EXACT'), ('Phrase', 'PHRASE'), ('Broad', 'BROAD')
    ]
}

Operations_dictionary = {'label': {'e': 'is equal to',
                                   'ea': 'is equal to any of',
                                   'eic': 'is equal to (ignore case)',
                                   'ne': 'is not equal to',
                                   'nea': 'is not equal to any of',
                                   'nic': 'is not equal to (ignore case)'},
                         'number': {'<': '< less than',
                                    '<=': '<= less than or equal to',
                                    '==': '== equal to',
                                    '>': '> greater than',
                                    '>=': '>= greater than or equal to'},
                         'string': {'$': 'ends with',
                                    '$ic': 'ends with (ignore case)',
                                    '^': 'starts with',
                                    '^ic': 'starts with (ignore case)',
                                    'c': 'contains',
                                    'cic': 'contains (ignore case)',
                                    'e': 'is equal to',
                                    'eic': 'is equal to (ignore case)',
                                    'in': 'in',
                                    'inic': 'in (ignore case)',
                                    'nc': 'does not contain',
                                    'ncic': 'does not contain (ignore case)',
                                    'ne': 'is not equal to',
                                    'neic': 'is not equal to (ignore case)'}}
Fields = {'Campaign': [('Campaign ID', 'CampaignId', 'string'),
                       ('Campaign Name', 'CampaignName', 'string'),
                       ('Account ID', 'ExternalCustomerId', 'string'),
                       ('Labels', 'Labels', 'label'),
                       ('Bid Strategy Type', 'BiddingStrategyType', 'string'),
                       ('Advertising Channel', 'AdvertisingChannelType', 'string'),
                       ('Clicks', 'Clicks', 'number'),
                       ('Impressions', 'Impressions', 'number'),
                       ('Cost', 'Cost', 'number'),
                       ('CTR', 'Ctr', 'number'),
                       ('Avg. CPC', 'AverageCpc', 'number'),
                       ('Avg. position', 'AveragePosition', 'number'),
                       ('Impr. (Top) %', 'TopImpressionPercentage', 'number'),
                       ('Impr. (Abs. Top) %',
                        'AbsoluteTopImpressionPercentage',
                        'number'),
                       ('Conversions', 'Conversions', 'number'),
                       ('All conv.', 'AllConversions', 'number'),
                       ('All conv. value', 'AllConversionValue', 'number'),
                       ('All conv. rate', 'AllConversionRate', 'number'),
                       ('Conv. value', 'ConversionValue', 'number'),
                       ('View-through conv.', 'ViewThroughConversions', 'number'),
                       ('Conv. rate', 'ConversionRate', 'number'),
                       ('Value / conv.', 'ValuePerConversion', 'number'),
                       ('Value / all conv.', 'ValuePerAllConversion', 'number'),
                       ('Cost / all conv.', 'CostPerAllConversion', 'number'),
                       ('Cost / conv.', 'CostPerConversion', 'number'),
                       ('ROAS', 'ConversionValue/Cost', 'number'),
                       ('All conv. val/cost', 'all_conversion_value_per_cost', 'number'),
                       ('All conv. val/click',
                        'all_conversion_value_per_click',
                        'number'),
                       ('Conv. val/cost', 'conversion_value_per_cost', 'number'),
                       ('Click Assisted Conv.', 'ClickAssistedConversions', 'number'),
                       ('Impr. Assisted Conv.',
                        'ImpressionAssistedConversions',
                        'number'),
                       ('Search Exact match IS',
                        'SearchExactMatchImpressionShare',
                        'number'),
                       ('Search Impr. share', 'SearchImpressionShare', 'number'),
                       ('Search Lost IS (rank)',
                        'SearchRankLostImpressionShare',
                        'number'),
                       ('Search Lost IS (budget)',
                        'SearchBudgetLostImpressionShare',
                        'number'),
                       ('Content Lost IS (budget)',
                        'ContentBudgetLostImpressionShare',
                        'number'),
                       ('Content Lost IS (rank)',
                        'ContentRankLostImpressionShare',
                        'number'),
                       ('Content Impr. share', 'ContentImpressionShare', 'number'),
                       ('Search abs. top IS',
                        'SearchAbsoluteTopImpressionShare',
                        'number'),
                       ('Click share', 'SearchClickShare', 'number'),
                       ('Search top IS', 'SearchTopImpressionShare', 'number'),
                       ('Search lost top IS (rank)',
                        'SearchRankLostTopImpressionShare',
                        'number'),
                       ('Search lost abs. top IS (rank)',
                        'SearchRankLostAbsoluteTopImpressionShare',
                        'number')],
          'Groups': [('Current Bid', 'CpcBid', 'number'),
                     ('Campaign Name', 'CampaignName', 'string'),
                     ('Ad group Name', 'AdGroupName', 'string'),
                     ('Label Name', 'Labels', 'label'),
                     ('Target ROAS', 'EffectiveTargetRoas', 'number'),
                     ('Target CPA', 'TargetCpa', 'number'),
                     ('Account ID', 'ExternalCustomerId', 'string'),
                     ('Campaign ID', 'CampaignId', 'string'),
                     ('Ad group ID', 'AdGroupId', 'string'),
                     ('Clicks', 'Clicks', 'number'),
                     ('Impressions', 'Impressions', 'number'),
                     ('Cost', 'Cost', 'number'),
                     ('CTR', 'Ctr', 'number'),
                     ('Avg. CPC', 'AverageCpc', 'number'),
                     ('Avg. position', 'AveragePosition', 'number'),
                     ('Impr. (Top) %', 'TopImpressionPercentage', 'number'),
                     ('Impr. (Abs. Top) %', 'AbsoluteTopImpressionPercentage', 'number'),
                     ('Conversions', 'Conversions', 'number'),
                     ('All conv.', 'AllConversions', 'number'),
                     ('All conv. value', 'AllConversionValue', 'number'),
                     ('All conv. rate', 'AllConversionRate', 'number'),
                     ('Conv. value', 'ConversionValue', 'number'),
                     ('View-through conv.', 'ViewThroughConversions', 'number'),
                     ('Conv. rate', 'ConversionRate', 'number'),
                     ('Value / conv.', 'ValuePerConversion', 'number'),
                     ('Value / all conv.', 'ValuePerAllConversion', 'number'),
                     ('Cost / all conv.', 'CostPerAllConversion', 'number'),
                     ('Cost / conv.', 'CostPerConversion', 'number'),
                     ('ROAS', 'ROAS', 'number'),
                     ('All conv. val/cost', 'all_conversion_value_per_cost', 'number'),
                     ('All conv. val/click', 'all_conversion_value_per_click', 'number'),
                     ('Conv. val/cost', 'conversion_value_per_cost', 'number'),
                     ('Click Assisted Conv.', 'ClickAssistedConversions', 'number'),
                     ('Impr. Assisted Conv.', 'ImpressionAssistedConversions', 'number'),
                     ('Search Exact match IS',
                      'SearchExactMatchImpressionShare',
                      'number'),
                     ('Search Impr. share', 'SearchImpressionShare', 'number'),
                     ('Search Lost IS (rank)',
                      'SearchRankLostImpressionShare',
                      'number'),
                     ('Content Impr. share', 'ContentImpressionShare', 'number'),
                     ('Search abs. top IS',
                      'SearchAbsoluteTopImpressionShare',
                      'number'),
                     ('Search top IS', 'SearchTopImpressionShare', 'number'),
                     ('Search lost top IS (rank)',
                      'SearchRankLostTopImpressionShare',
                      'number'),
                     ('Search lost abs. top IS (rank)',
                      'SearchRankLostAbsoluteTopImpressionShare',
                      'number')],
          'Keywords': [('Current Bid', 'CpcBid', 'number'),
                       ('Campaign Name', 'CampaignName', 'string'),
                       ('Ad group Name', 'AdGroupName', 'string'),
                       ('Match Type', 'KeywordMatchType', 'string'),
                       ('First page CPC', 'FirstPageCpc', 'number'),
                       ('Top of page CPC', 'TopOfPageCpc', 'number'),
                       ('First position CPC', 'FirstPositionCpc', 'number'),
                       ('Keyword', 'Criteria', 'string'),
                       ('Label Name', 'Labels', 'label'),
                       ('Account ID', 'ExternalCustomerId', 'string'),
                       ('Campaign ID', 'CampaignId', 'string'),
                       ('Ad group ID', 'AdGroupId', 'string'),
                       ('Keyword ID', 'Id', 'string'),
                       ('Quality score', 'QualityScore', 'number'),
                       ('Quality score (hist.)', 'HistoricalQualityScore', 'number'),
                       ('Exp. CTR', 'SearchPredictedCtr', 'number'),
                       ('Exp. CTR (hist.)', 'HistoricalSearchPredictedCtr', 'number'),
                       ('Landing page exp.', 'PostClickQualityScore', 'number'),
                       ('Landing page exp. (hist.)',
                        'HistoricalLandingPageQualityScore',
                        'number'),
                       ('Ad relevance', 'CreativeQualityScore', 'number'),
                       ('Ad relevance (hist.)',
                        'HistoricalCreativeQualityScore',
                        'number'),
                       ('Clicks', 'Clicks', 'number'),
                       ('Impressions', 'Impressions', 'number'),
                       ('Cost', 'Cost', 'number'),
                       ('CTR', 'Ctr', 'number'),
                       ('Avg. CPC', 'AverageCpc', 'number'),
                       ('Avg. position', 'AveragePosition', 'number'),
                       ('Impr. (Top) %', 'TopImpressionPercentage', 'number'),
                       ('Impr. (Abs. Top) %',
                        'AbsoluteTopImpressionPercentage',
                        'number'),
                       ('Conversions', 'Conversions', 'number'),
                       ('All conv.', 'AllConversions', 'number'),
                       ('All conv. value', 'AllConversionValue', 'number'),
                       ('All conv. rate', 'AllConversionRate', 'number'),
                       ('Conv. value', 'ConversionValue', 'number'),
                       ('View-through conv.', 'ViewThroughConversions', 'number'),
                       ('Conv. rate', 'ConversionRate', 'number'),
                       ('Value / conv.', 'ValuePerConversion', 'number'),
                       ('Cost / all conv.', 'CostPerAllConversion', 'number'),
                       ('Cost / conv.', 'CostPerConversion', 'number'),
                       ('ROAS', 'ROAS', 'number'),
                       ('All conv. val/cost', 'all_conversion_value_per_cost', 'number'),
                       ('All conv. val/click',
                        'all_conversion_value_per_click',
                        'number'),
                       ('Conv. val/cost', 'conversion_value_per_cost', 'number'),
                       ('Click Assisted Conv.', 'ClickAssistedConversions', 'number'),
                       ('Impr. Assisted Conv.',
                        'ImpressionAssistedConversions',
                        'number'),
                       ('Search Exact match IS',
                        'SearchExactMatchImpressionShare',
                        'string'),
                       ('Search Impr. share', 'SearchImpressionShare', 'string'),
                       ('Search Lost IS (rank)',
                        'SearchRankLostImpressionShare',
                        'string'),
                       ('Search abs. top IS',
                        'SearchAbsoluteTopImpressionShare',
                        'string'),
                       ('Search top IS', 'SearchTopImpressionShare', 'string'),
                       ('Search lost top IS (rank)',
                        'SearchRankLostTopImpressionShare',
                        'string'),
                       ('Search lost abs. top IS (rank)',
                        'SearchRankLostAbsoluteTopImpressionShare',
                        'string')]}

Condition_scope = {
    'Campaign': [
        ('Campaign', 'Campaign'),
    ],
    'Groups': [
        ('Adgroup', 'Groups'),
        ('Campaign', 'Campaign'),
    ],
    'Keywords': [
        ('Keyword', 'Keywords'),
        ('Adgroup', 'Groups'),
        ('Campaign', 'Campaign'),

    ]
}
Action_scope = {
    'Campaign': [
        ('Campaign', 'Campaign'),
        ('All Ad group(s) of the Campaign', 'Groups'),
        ('All Keyword(s) of the Campaign', 'Keywords'),
    ],
    'Groups': [
        ('Adgroup', 'Groups'),
        ('All Keyword(s) of the Campaign', 'Keywords')
    ],
    'Keywords': [
        ('Keyword', 'Keywords')
    ]
}
Action_dictionary = {
    'Campaign': [
        ('Modify status', 'status'),
        ('Modify label', 'label')
    ],
    'Groups': [
        ('Modify CPC Bids', 'cpc'),
        ('Modify Label', 'label'),
        ('Modify Status', 'status'),
        ('Modify ROAS', 'roas'),
        ('Modify Target CPA', 'cpa'),
        ('Modify CPM Bids', 'cpm')
    ],
    'Keywords': [
        ('Modify CPC Bids', 'cpc'),
        ('Modify Label', 'label'),
        ('Modify Status', 'status'),
        ('Modify CPM Bids', 'cpm')
    ]
}

Action_options = {
    'status': [
        ('Enable Status', 'enable', 'ENABLED'),
        ('Pause Status', 'pause', 'DISABLED')
    ],
    'label': [
        ('Add Labels', 'ADD'),
        ('Remove Labels', 'REMOVE')
    ],
    'cpc': [
        ('Increase CPC Bids', 'increase'),
        ('Decrease CPC Bids', 'decrease'),
        ('Set Bids', 'set')
    ],
    'roas': [
        ('Increase Target ROAS', 'increase'),
        ('Decrease Target ROAS', 'decrease'),
        ('Set Target ROAS', 'set')
    ],
    'cpa': [
        ('Increase Target CPA', 'increase'),
        ('Decrease Target CPA', 'decrease'),
        ('Set Target CPA', 'set')
    ],
    'cpm': [
        ('Increase CPM Bids', 'increase'),
        ('Decrease CPM Bids', 'decrease'),
        ('Set CPM Bids', 'set')
    ],

}
Name_of_Days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
Action_values = {

}
# Fields=dict()
# Fields['Campaign']=list()
# Fields['Groups']=list()
# Fields['Keywords']=list()
#
#
# my_path = os.path.dirname(os.getcwd())
#
# FILENAME = my_path + "/res/Campaign.txt"
# with open(FILENAME) as f:
#     for line in f:
#         token = line.strip().split(",")
#         Fields['Campaign'].append((token[0],token[1],token[2]))
# FILENAME = my_path + "/res/Groups.txt"
# with open(FILENAME) as f:
#     for line in f:
#         token = line.strip().split(",")
#         Fields['Groups'].append((token[0],token[1],token[2]))
# FILENAME = my_path + "/res/Keywords.txt"
# with open(FILENAME) as f:
#     for line in f:
#         token = line.strip().split(",")
#         Fields['Keywords'].append((token[0],token[1],token[2]))

if __name__ == '__main__':
    # print(json.dumps(Operations_dictionary))
    pprint.pprint(Fields)
