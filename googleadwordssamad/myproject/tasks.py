import csv
import datetime
import os
import uuid
import pandas as pd

from celery.utils.log import get_task_logger

from googleadwordssamad import settings
from googleadwordssamad.celery_tasks import app
from googleadwordssamad.myproject.add_budget import AddBudget
from googleadwordssamad.myproject.models import AdwordsCampaign, AdwordsCampaignGroup, \
    AdgroupPerformanceReportModel, KeywordPerformanceReportModel
from googleads import adwords

from .models import AdwordsCampaignKeywords, CampaignPerformanceReportModel, \
    Rule_Engine_Recipe, Rule_Engine_Rules, Rule_Engine_Conditions, Rule_Engine_Action
from .utils.utils import PauseAdGroups, update_campaign_status, update_adgroup_status, \
    update_keyword_status, update_campaign_labels, update_adgroup_labels, update_keyword_labels

from datetime import datetime

logger = get_task_logger(__name__)
client = adwords.AdWordsClient.LoadFromStorage()


@app.task
def Add_new_Campaign(campaign_name, status, ad_channel, start_date, end_date, budget):
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
                'advertisingChannelType': ad_channel,
                'startDate': start_date,
                'endDate': end_date,
            }
        }]

        campaign_service.mutate(operations)
    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured'.format(repr(ex)))


@app.task
def get_all_campaign():
    PAGE_SIZE = 100
    # Initialize appropriate service.
    campaign_service = client.GetService('CampaignService', version='v201809')

    # Construct selector and get all campaigns.
    offset = 0
    selector = {
        'fields': ['Id', 'Name', 'Status', 'StartDate', 'EndDate', 'Amount', 'Labels', 'Eligible'],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        }
    }
    MICROAMMOUNT = 1000000.00
    more_pages = True
    while more_pages:
        page = campaign_service.get(selector)

        # Display results.
        if 'entries' in page:
            for campaign in page['entries']:
                print(campaign)
                try:
                    obj = AdwordsCampaign.objects.get(campaign_id=campaign['id'])
                except AdwordsCampaign.DoesNotExist:
                    obj = AdwordsCampaign()
                obj.campaign_id = campaign['id']
                obj.name = campaign['name']
                obj.budget = campaign['budget']['amount']['microAmount'] / MICROAMMOUNT
                obj.start_date = datetime.strptime(campaign['startDate'], '%Y%m%d').strftime('%Y-%m-%d')
                obj.end_date = datetime.strptime(campaign['endDate'], '%Y%m%d').strftime('%Y-%m-%d')
                obj.status = campaign['status']
                obj.label = campaign['labels']
                print(type(campaign['conversionOptimizerEligibility']))
                print('check', campaign['conversionOptimizerEligibility'])
                obj.conversion_optimizer_eligibility = campaign['conversionOptimizerEligibility']['eligible']
                obj.save()

                # print('Campaign with id "%s", name "%s",startdate "%s", and status "%s" was ' 'found.' % (
                #     campaign['id'], campaign['name'], campaign['startDate'], campaign['status']))
                # print('(IN DB)Campaign with id "%s", name "%s",startdate "%s", and status "%s" was ' 'saved.' % (
                #     obj.campaign_id, obj.name, obj.start_date, obj.status))

        else:
            print('No campaigns were found.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])


@app.task
def Add_new_group(campaign_id, group_name, group_status):
    client.SetClientCustomerId(client.client_customer_id)
    ad_group_service = client.GetService('AdGroupService')
    try:

        operations = [{
            'operator': 'ADD',
            'operand': {
                'campaignId': campaign_id,
                'name': group_name,
                'status': group_status
            }
        }]
        ad_group_service.mutate(operations)
    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occurred'.format(repr(ex)))


@app.task
def GetAdGroups(campaign_id):
    selector = {
        'fields': ['Id', 'Name', 'Status', 'CpcBid'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': [campaign_id]
            },
            {
                'field': 'Status',
                'operator': 'NOT_EQUALS',
                'values': ['REMOVED']
            }
        ]
    }
    adgroups = client.GetService('AdGroupService').get(selector)
    # Display results.
    # if 'entries' in adgroups:
    #     for ad_group in adgroups['entries']:
    #         print('Ad group with name "%s", id "%s" and status "%s" was '
    #               'found.' % (ad_group['name'], ad_group['id'],
    #                           ad_group['status']))
    # else:
    #     print("No ad groups were found.")
    if int(adgroups['totalNumEntries']) > 0:
        return adgroups['entries']
    else:
        return {}


@app.task
def get_all_groups():
    try:
        ad_campain_ids = AdwordsCampaign.objects.values_list('campaign_id')

        print(ad_campain_ids)
        for ad_campain_id in ad_campain_ids:

            ad_groups = GetAdGroups(ad_campain_id[0])

            for ad_group in ad_groups:

                try:
                    ad_group_obj = AdwordsCampaignGroup.objects.get(group_id=ad_group.id)
                except AdwordsCampaignGroup.DoesNotExist:
                    ad_group_obj = AdwordsCampaignGroup()

                ad_group_obj.campaign = AdwordsCampaign.objects.get(campaign_id=ad_campain_id[0])

                ad_group_obj.status = ad_group.status
                ad_group_obj.group_id = ad_group.id
                ad_group_obj.name = ad_group.name
                ad_group_obj.save()

    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured while creating adgroup {} .'.format(repr(ex)))


@app.task
def Add_new_keyword(ad_group_id, text, status):
    ad_group_criterion_service = client.GetService(
        'AdGroupCriterionService', version='v201809')
    try:
        # Construct keyword ad group criterion object.
        keyword1 = {
            'xsi_type': 'BiddableAdGroupCriterion',
            'adGroupId': ad_group_id,
            'criterion': {
                'xsi_type': 'Keyword',
                'matchType': 'BROAD',
                'text': text
            },
            'userStatus': status,
        }
        operations = [
            {
                'operator': 'ADD',
                'operand': keyword1
            }
        ]
        ad_group_criterion_service.mutate(operations)

        # ad_group_criteria = ad_group_criterion_service.mutate(operations)['value']
        # Display results.
        # for criterion in ad_group_criteria:
        #     print(criterion)
        #     print('Keyword ad group criterion with ad group id "%s", criterion id '
        #           '"%s", text "%s", and match type "%s" was added.'
        #           % (criterion['adGroupId'], criterion['criterion']['id'],
        #              criterion['criterion']['text'],
        #              criterion['criterion']['matchType']))
    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured'.format(repr(ex)))


@app.task
def get_keyword(adgroup_id):
    PAGE_SIZE = 500
    try:
        ad_group_criterion_service = client.GetService(
            'AdGroupCriterionService', version='v201809')
        # Construct selector and get all ad group criteria.
        offset = 0
        selector = {
            'fields': ['Id', 'CriteriaType', 'KeywordMatchType', 'KeywordText'],
            'predicates': [
                {
                    'field': 'AdGroupId',
                    'operator': 'EQUALS',
                    'values': [adgroup_id]
                },
                {
                    'field': 'CriteriaType',
                    'operator': 'EQUALS',
                    'values': ['KEYWORD']
                }
            ],
            'paging': {
                'startIndex': str(offset),
                'numberResults': str(PAGE_SIZE)
            },
            'ordering': [{'field': 'KeywordText', 'sortOrder': 'ASCENDING'}]
        }

        page = ad_group_criterion_service.get(selector)
        # # Display results.
        # if 'entries' in page:
        #     # print(page)
        #     for keyword in page['entries']:
        #         print('Keyword ID "%s", type "%s", text "%s", and match type '
        #               '"%s" was found.' % (
        #                   keyword['criterion']['id'],
        #                   keyword['criterion']['type'],
        #                   keyword['criterion']['text'],
        #                   keyword['criterion']['matchType']))
        # else:
        #     print('No keywords were found.')

        if int(page['totalNumEntries']) > 0:

            print(page['entries'])

            return page['entries']
        else:
            return {}

    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured while getting keywords {}.'.format(repr(ex)))


'''
@app.task
def get_all_keywords():
    try:
        ad_group_ids = AdwordsCampaignGroup.objects.values_list('group_id')
        for ad_group_id in ad_group_ids:
            ad_keywords = get_keyword(ad_group_id[0])
            #print(ad_keywords)
            print("-------------------------------------------")
            for ad_keyword in ad_keywords:
                print(ad_keyword['criterion']['id'])
                print("-------------***------------------------------")
                try:
                    ad_keyword_obj = AdwordsCampaignKeywords.objects.get(keyword_id=ad_keyword['criterion']['id'])
                except AdwordsCampaignKeywords.DoesNotExist:
                    ad_keyword_obj = AdwordsCampaignKeywords()
                    print("===============Group id========", ad_group_id[0])
                ad_keyword_obj.group = AdwordsCampaignGroup.objects.get(group_id=ad_group_id[0])
                ad_keyword_obj.status = ad_keyword['userStatus']
                ad_keyword_obj.keyword_id = ad_keyword['criterion']['id']
                ad_keyword_obj.text = ad_keyword['criterion']['text']
                ad_keyword_obj.clicks=ad_keywords
                ad_keyword_obj.save()
                print("=====================Data saved.")
    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured while creating========================== adgroup {} .'.format(repr(ex)))
'''


@app.task
def updateKeywordsInDatabase():
    try:
        report_downloader = client.GetReportDownloader(version='v201809')
        report_query = (adwords.ReportQueryBuilder()
                        .Select('CampaignId', 'AdGroupId', 'Id', 'Criteria',
                                'CriteriaType', 'FinalUrls', 'Impressions', 'Clicks',
                                'Cost', 'Status')
                        .From('CRITERIA_PERFORMANCE_REPORT')
                        .Where('Status').In('ENABLED', 'PAUSED')
                        .During('LAST_7_DAYS')
                        .Build())
        if not os.path.exists(settings.STATIC_ROOT + '/keywords/'):
            os.makedirs(settings.STATIC_ROOT + '/keywords/')

        id = uuid.uuid4()
        file_name = '%s/keywords/%s.csv' % (settings.STATIC_ROOT, id)
        file = open('%s' % file_name, 'w+')
        report_downloader.DownloadReportWithAwql(
            report_query, 'CSV', file, skip_report_header=True,
            skip_column_header=False, skip_report_summary=True,
            include_zero_impressions=True)

        file.close()
        data = {}

        with open(file_name, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                # keys : ad_group_id, keyword_id,
                # values : Text, Impressions', Clicks, Cost, Status
                data[(row[1], row[2])] = (row[3], row[6], row[7], row[8], row[9])
        os.remove(file_name)
        if data:
            print(data)
            for key, val in data.items():
                try:
                    ad_keyword_obj = AdwordsCampaignKeywords.objects.get(keyword_id=key[1])
                except AdwordsCampaignKeywords.DoesNotExist:
                    ad_keyword_obj = AdwordsCampaignKeywords()
                    ad_keyword_obj.keyword_id = key[1]
                ad_keyword_obj.text = val[0]
                ad_keyword_obj.impressions = int(val[1])
                ad_keyword_obj.clicks = int(val[2])
                ad_keyword_obj.max_cpc = int(val[3])
                ad_keyword_obj.status = (val[4].upper())
                try:
                    ad_keyword_obj.group = AdwordsCampaignGroup.objects.get(group_id=key[0])
                except AdwordsCampaignGroup.DoesNotExist:
                    continue
                ad_keyword_obj.save()




    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured while creating adgroup {} .'.format(repr(ex)))


#
# @app.task
# def rule_engine():
#     try:
#         report_downloader = client.GetReportDownloader(version='v201809')
#         report_query = (adwords.ReportQueryBuilder()
#                         .Select('CampaignId', 'AdGroupId', 'Id', 'Criteria',
#                                 'CriteriaType', 'FinalUrls', 'Impressions', 'Clicks',
#                                 'Cost', 'Status',
#                                 'AdGroupName', 'Ctr', 'Conversions',
#                                 'CampaignName'
#                                 )
#                         .From('CRITERIA_PERFORMANCE_REPORT')
#                         .Where('Status').In('ENABLED', 'PAUSED')
#                         .During('LAST_7_DAYS')
#                         .Build())
#         if not os.path.exists(settings.STATIC_ROOT + '/keywords/'):
#             os.makedirs(settings.STATIC_ROOT + '/keywords/')
#
#         id = uuid.uuid4()
#         file_name = '%s/keywords/%s.csv' % (settings.STATIC_ROOT, id)
#         file = open('%s' % (file_name), 'w+')
#         report_downloader.DownloadReportWithAwql(
#             report_query, 'CSV', file, skip_report_header=True,
#             skip_column_header=False, skip_report_summary=True,
#             include_zero_impressions=True)
#
#         file.close()
#         data_for_keywords = dict()
#         data_for_adgroups = dict()
#
# with open(file_name, 'r') as csv_file: csv_reader = csv.reader(csv_file, delimiter=',') next(csv_reader) for row in
# csv_reader: # keys : ad_group_id, keyword_id, # values : Text 0, Impressions 1', Clicks 2, Cost 3,status 4,
# adgroupname 5,ctr 6,conversions 7,campaignname 8,campaign id 9 data_for_keywords[(row[1], row[2])] = ( row[3],
# row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[0]) # row[11]=ctr data_for_adgroups[(row[
# 0], row[1])] = (row[11])
#
#         os.remove(file_name)
#         for rule in AdwordsCampaignRuleEngine_keywords.objects.all():
#             ad_group_id = AdwordsCampaignGroup.objects.get(pk=rule.group_id).group_id
#             update_keyword_based_on_rule.delay(rule.keyword_id, ad_group_id, rule.action, rule.max_cpc,
#                                                rule.impressions, data_for_keywords[(ad_group_id, rule.keyword_id)])
#
#         for rule in AdwordsCampaignRuleEngine_adgroups.objects.all():
#             campaign_id = AdwordsCampaign.objects.get(pk=rule.campaign_id).campaign_id
#             # update_adgroup_based_on_rule.delay(rule.group_id, rule.action, rule.max_ctr, rule.location,
#             #                                  rule.target_date, data_for_adgroups[(campaign_id, rule.group_id)])
#
#         # =========================================================
#         '''
#         # Conditions
#         # 1
#         MAX_CPC = 50
#         pause_keyword_based_on_cpc('zkeyword', MAX_CPC, data)
#         print("1")
#         # 2
#         MIN_Impressions = 5
#         pause_keyword_based_on_impressions('zkeyword', MIN_Impressions, data)
#         print("2")
#         # 3
#         DATE = datetime(2019, 7, 18).date()
#         pause_adgroup_based_on_ctr_and_current_date('samadgroup', 10, DATE, data)
#         print("3")
#         # 4
#         enable_pause_all_adgroups_based_on_conversion('my1', data)
#         print("4")
#         # 5
#         pause_campaign_based_on_date_intervals('samadcampaign', 14, 16, data)
#         print("5")
#         '''
#
#
#     except Exception as ex:
#         print(repr(ex))
#         logger.error('Exception occured while creating========================== adgroup {} .'.format(repr(ex)))


'''
@app.task
def pause_adgroup():
    try:
        # now = datetime.datetime.now()
        # today_date = now.date()
        report_downloader = client.GetReportDownloader(version='v201809')
        report_query = (adwords.ReportQueryBuilder()
                        .Select('CampaignId', 'AdGroupId', 'AdGroupName', 'Ctr', 'Conversions')
                        .From('ADGROUP_PERFORMANCE_REPORT')
                        .Where('AdGroupStatus').In('ENABLED', 'PAUSED')
                        .Where('CampaignStatus').In('ENABLED', 'PAUSED')
                        .Build())

        if not os.path.exists(settings.STATIC_ROOT + '/keywords/'):
            os.makedirs(settings.STATIC_ROOT + '/keywords/')

        id = uuid.uuid4()
        file_name = '%s/keywords/%s.csv' % (settings.STATIC_ROOT, id)
        file = open('%s' % (file_name), 'w+')
        report_downloader.DownloadReportWithAwql(
            report_query, 'CSV', file, skip_report_header=True,
            skip_column_header=False, skip_report_summary=True,
            include_zero_impressions=True)

        file.close()
        data = {}
        try:
            with open(file_name, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                next(csv_reader)
                for row in csv_reader:
                    # keys : campaign_id, ad_group_id
                    # values : Text, Impressions', Clicks, Cost
                    data[(row[0], row[1])] = (row[2], row[3], row[4])
        except:
            pass
        if data:
            print(data)
        os.remove(file_name)
        # ================================================================

        DATE = datetime(2019, 7, 18).date()
        pause_adgroup_based_on_ctr_and_current_date('samadgroup', 10, DATE, data)

        # enable_pause_based_on_conversion('my1', data)




    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured while creating========================== adgroup {} .'.format(repr(ex)))

'''


@app.task
def pause_adgroup_location():
    PAGE_SIZE = 500
    campaign_criterion_service = client.GetService(
        'CampaignCriterionService', version='v201809')

    # Construct selector and get all campaign targets.
    offset = 0
    selector = {
        'fields': ['CampaignId', 'Id', 'CriteriaType', 'PlatformName',
                   'LanguageName', 'LocationName', 'KeywordText'],
        'predicates': [{
            'field': 'CriteriaType',
            'operator': 'IN',
            'values': ['KEYWORD', 'LANGUAGE', 'LOCATION', 'PLATFORM']
        }],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        }
    }
    more_pages = True
    while more_pages:
        page = campaign_criterion_service.get(selector)

        # Display results.
        if 'entries' in page:
            for campaign_criterion in page['entries']:
                print(campaign_criterion)
                negative = ''
                if (campaign_criterion['CampaignCriterion.Type']
                        == 'NegativeCampaignCriterion'):
                    negative = 'Negative '
                criterion = campaign_criterion['criterion']
                criteria = (criterion['text'] if 'text' in criterion else
                            criterion['platformName'] if 'platformName' in criterion
                            else criterion['name'] if 'name' in criterion else
                            criterion['locationName'] if 'locationName' in criterion
                            else None)
                print('%sCampaign Criterion found for Campaign ID %s with type %s and '
                      'criteria "%s".' % (negative, campaign_criterion['campaignId'],
                                          criterion['type'], criteria))

                location = 'Saudi Arabia'
                if criterion['type'] == 'LOCATION':
                    if criteria == location:
                        print("===========YES============")
                        print(campaign_criterion['campaignId'])
                        campaign_id_pk = AdwordsCampaign.objects.get(campaign_id=campaign_criterion['campaignId']).id
                        print(campaign_id_pk)
                        adgroup_id = AdwordsCampaignGroup.objects.get(campaign_id=campaign_id_pk).group_id
                        print(adgroup_id)
                        PauseAdGroups(adgroup_id)
        else:
            print('No campaign targets were found.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])


@app.task
def get_adgroup_location():
    campaign_criterion_service = client.GetService(
        'CampaignCriterionService', version='v201809')
    selector = {
        'fields': ['CampaignId', 'Id', 'CriteriaType', 'PlatformName',
                   'LanguageName', 'LocationName', 'KeywordText'],
        'predicates': [{
            'field': 'CriteriaType',
            'operator': 'IN',
            'values': ['KEYWORD', 'LANGUAGE', 'LOCATION', 'PLATFORM']
        }],

    }
    page = campaign_criterion_service.get(selector)

    # Display results.
    if 'entries' in page:
        for campaign_criterion in page['entries']:
            criterion = campaign_criterion['criterion']
            criteria = (criterion['text'] if 'text' in criterion else
                        criterion['platformName'] if 'platformName' in criterion
                        else criterion['name'] if 'name' in criterion else
                        criterion['locationName'] if 'locationName' in criterion
                        else None)
            # c_id = campaign_criterion['campaignId']
            if criterion['type'] == 'LOCATION':
                return criteria
        else:
            print('No campaign targets were found.')


@app.task
def get_all_attributes_campaign():
    REPORT_TYPE = 'CAMPAIGN_PERFORMANCE_REPORT'
    # Initialize appropriate service.
    # report_definition_service = client.GetService(
    #     'ReportDefinitionService', version='v201809')

    # Get report fields.
    # fields = report_definition_service.getReportFields(REPORT_TYPE)

    my_path = os.path.abspath(os.path.dirname(__file__))
    # print(my_path)
    FILENAME = my_path + "/res/campaign_attributes.txt"

    with open(FILENAME) as f:
        content = f.readlines()
    requiredFields = [x.strip() for x in content]
    # print(requiredFields)
    try:
        # Initialize appropriate service.
        report_downloader = client.GetReportDownloader(version='v201809')

        # Create report query.
        report = {
            'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
            'dateRangeType': 'LAST_7_DAYS',
            'reportType': REPORT_TYPE,
            'downloadFormat': 'CSV',

            'selector': {
                'fields': requiredFields,

            }
        }
        if not os.path.exists(settings.STATIC_ROOT + '/campaigns/'):
            os.makedirs(settings.STATIC_ROOT + '/campaigns/')

        id = uuid.uuid4()
        file_name = '%s/campaigns/%s.csv' % (settings.STATIC_ROOT, id)
        file = open('%s' % file_name, 'w+')
        report_downloader.DownloadReport(
            report, file, skip_report_header=True,
            skip_column_header=False, skip_report_summary=True,
            include_zero_impressions=True)

        file.close()
        # data = {}
        data = pd.read_csv(file_name)
        # os.remove(file_name)

        for index, row in data.iterrows():

            # access data using column names
            # attributes = [row[l] for l in list(data.columns)]
            # print(index,*attributes)

            try:
                campaign_report = CampaignPerformanceReportModel.objects.get(CampaignId=row["Campaign ID"])

            except CampaignPerformanceReportModel.DoesNotExist:
                campaign_report = CampaignPerformanceReportModel()
                campaign_report.CampaignId = row["Campaign ID"]
            campaign_report.ExternalCustomerId = row["Customer ID"]
            campaign_report.CampaignName = row['Campaign']
            campaign_report.BiddingStrategyType = row['Bid Strategy Type']
            campaign_report.AdvertisingChannelType = row['Advertising Channel']
            campaign_report.Clicks = row['Clicks']

            campaign_report.Impressions = row['Impressions']
            campaign_report.Cost = row['Cost']
            campaign_report.Ctr = row['CTR']
            campaign_report.AverageCpc = row['Avg. CPC']
            campaign_report.AveragePosition = row['Avg. position']
            campaign_report.TopImpressionPercentage = row['Impr. (Top) %']
            campaign_report.AbsoluteTopImpressionPercentage = row['Impr. (Abs. Top) %']
            campaign_report.Conversions = row['Conversions']
            campaign_report.AllConversions = row['All conv.']

            campaign_report.AllConversionRate = row['All conv. rate']
            campaign_report.AllConversionValue = row['All conv. value']
            campaign_report.ConversionValue = row['Total conv. value']
            campaign_report.ViewThroughConversions = row['View-through conv.']
            campaign_report.ConversionRate = row['Conv. rate']
            campaign_report.ValuePerConversion = row['Value / conv.']
            campaign_report.ValuePerAllConversion = row['Value / all conv.']
            campaign_report.CostPerAllConversion = row['Cost / all conv.']
            campaign_report.CostPerConversion = row['Cost / conv.']
            campaign_report.MaximizeConversionValueTargetRoas = row['Target ROAS (Maximize Conversion Value)']
            campaign_report.ClickAssistedConversions = row['Click Assisted Conv.']
            campaign_report.ImpressionAssistedConversions = row['Impr. Assisted Conv.']

            campaign_report.SearchExactMatchImpressionShare = row['Search Exact match IS']
            campaign_report.SearchImpressionShare = row['Search Impr. share']
            campaign_report.SearchRankLostImpressionShare = row['Search Lost IS (rank)']
            campaign_report.SearchBudgetLostImpressionShare = row['Search Lost IS (budget)']

            campaign_report.ContentBudgetLostImpressionShare = row['Content Lost IS (budget)']
            campaign_report.ContentRankLostImpressionShare = row['Content Lost IS (rank)']
            campaign_report.ContentImpressionShare = row['Content Impr. share']
            campaign_report.SearchAbsoluteTopImpressionShare = row['Search abs. top IS']
            campaign_report.SearchClickShare = row['Click share']

            campaign_report.SearchTopImpressionShare = row['Search top IS']
            campaign_report.SearchRankLostTopImpressionShare = row['Search lost top IS (rank)']
            campaign_report.SearchRankLostAbsoluteTopImpressionShare = row['Search lost abs. top IS (rank)']

            if campaign_report.Clicks > 0:
                campaign_report.all_conversion_value_per_click = campaign_report.AllConversionValue / campaign_report.Clicks
            else:
                campaign_report.all_conversion_value_per_click = 0

            if campaign_report.Cost > 0:
                campaign_report.conversion_value_per_cost = campaign_report.ConversionValue / campaign_report.Cost
                campaign_report.all_conversion_value_per_cost = campaign_report.AllConversionValue / campaign_report.Cost
            else:
                campaign_report.all_conversion_value_per_cost = 0
                campaign_report.conversion_value_per_cost = 0

            # row_label = eval(row['Labels']) if row['Labels'][0] == '[' else row['Labels']
            campaign_report.Labels = row['Labels']
            campaign_report.LabelIds = row['Label IDs']

            # row_label=row['Labels']
            # print(row_label,'--')
            # if row['Labels'][0]=='[':
            #     print("inside")
            #     row_label = eval(row['Labels'])

            # print(row_label)
            # label='["usama"]'
            # print(label)
            # label=eval(label)
            # print(type(row_label))
            campaign_report.save()


    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured while getting campaign attributes ---> {} .'.format(repr(ex)))


'''
    # Display results.
    print('Report type "%s" contains the following fields:' % REPORT_TYPE)
    print("Fieldes length: " ,len(fields))
    for field in fields:
        print(' - %s (%s)' % (field['fieldName'], field['fieldType']))
        if 'enumValues' in field:
            print('  := [%s]' % ', '.join(field['enumValues']))
    '''


@app.task
def get_all_attributes_adgroup1():
    campaign_criterion_service = client.GetService(
        'CampaignCriterionService', version='v201809')
    selector = {
        'fields': ['CampaignId', 'Id', 'CriteriaType', 'PlatformName',
                   'LanguageName', 'LocationName', 'KeywordText'],
        'predicates': [{
            'field': 'CriteriaType',
            'operator': 'IN',
            'values': ['KEYWORD', 'LANGUAGE', 'LOCATION', 'PLATFORM']
        }],

    }
    page = campaign_criterion_service.get(selector)

    # Display results.
    if 'entries' in page:
        for campaign_criterion in page['entries']:
            criterion = campaign_criterion['criterion']
            criteria = (criterion['text'] if 'text' in criterion else
                        criterion['platformName'] if 'platformName' in criterion
                        else criterion['name'] if 'name' in criterion else
                        criterion['locationName'] if 'locationName' in criterion
                        else None)
            # c_id = campaign_criterion['campaignId']
            if criterion['type'] == 'LOCATION':
                return criteria
        else:
            print('No campaign targets were found.')


@app.task
def get_all_attributes_adgroup():
    REPORT_TYPE = 'ADGROUP_PERFORMANCE_REPORT'
    # Initialize appropriate service.
    # report_definition_service = client.GetService(
    #     'ReportDefinitionService', version='v201809')

    # Get report fields.
    # fields = report_definition_service.getReportFields(REPORT_TYPE)

    my_path = os.path.abspath(os.path.dirname(__file__))
    # print(my_path)
    FILENAME = my_path + "/res/group_attributes.txt"

    with open(FILENAME) as f:
        content = f.readlines()
    requiredFields = [x.strip() for x in content]
    # print(requiredFields)
    try:
        # Initialize appropriate service.
        report_downloader = client.GetReportDownloader(version='v201809')

        # Create report query.
        report = {
            'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
            'dateRangeType': 'LAST_7_DAYS',
            'reportType': REPORT_TYPE,
            'downloadFormat': 'CSV',

            'selector': {
                'fields': requiredFields,
                "predicates": [{
                    "field": "AdGroupStatus",
                    "operator": "IN",
                    "values": [
                        "ENABLED",
                        "PAUSED"
                    ]

                }, {
                    "field": "CampaignStatus",
                    "operator": "IN",
                    "values": [
                        "ENABLED",
                        "PAUSED"
                    ]

                }]

            }
        }
        if not os.path.exists(settings.STATIC_ROOT + '/adgroups/'):
            os.makedirs(settings.STATIC_ROOT + '/adgroups/')

        id = uuid.uuid4()
        file_name = '%s/adgroups/%s.csv' % (settings.STATIC_ROOT, id)
        file = open('%s' % file_name, 'w+')
        report_downloader.DownloadReport(
            report, file, skip_report_header=True,
            skip_column_header=False, skip_report_summary=True,
            include_zero_impressions=True)

        file.close()
        # data = {}
        data = pd.read_csv(file_name)
        # print(len(data.columns))
        # os.remove(file_name)

        for index, row in data.iterrows():
            # access data using column names
            # attributes = [row[l] for l in list(data.columns)]
            # print(index,*attributes)

            try:
                group_report = AdgroupPerformanceReportModel.objects.get(AdGroupId=row["Ad group ID"])

            except AdgroupPerformanceReportModel.DoesNotExist:
                group_report = AdgroupPerformanceReportModel()
                group_report.AdGroupId = row["Ad group ID"]
            # group_report.ExternalCustomerId = row["ExternalCustomerId"]

            print("==========================samad testing now cpc===================")
            print(type(row['Default max. CPC']))
            group_report.CpcBid = row['Default max. CPC']
            group_report.CampaignName = row['Campaign']
            group_report.AdGroupName = row['Ad group']
            group_report.Labels = row['Labels']
            group_report.LabelIds = row['Label IDs']
            group_report.EffectiveTargetRoas = row['Target ROAS']
            group_report.TargetCpa = row['Target CPA']
            group_report.ExternalCustomerId = row['Customer ID']
            group_report.CampaignId = row['Campaign ID']
            group_report.Clicks = row['Clicks']
            group_report.Impressions = row['Impressions']
            group_report.Cost = row['Cost']
            group_report.Ctr = row['CTR']
            group_report.AverageCpc = row['Avg. CPC']
            group_report.AveragePosition = row['Avg. position']
            group_report.TopImpressionPercentage = row['Impr. (Top) %']
            group_report.AbsoluteTopImpressionPercentage = row['Impr. (Abs. Top) %']
            group_report.Conversions = row['Conversions']
            group_report.AllConversions = row['All conv.']
            group_report.AllConversionValue = row['All conv. value']
            group_report.AllConversionRate = row['All conv. rate']
            group_report.ConversionValue = row['Total conv. value']
            group_report.ViewThroughConversions = row['View-through conv.']
            group_report.ConversionRate = row['Conv. rate']
            group_report.ValuePerConversion = row['Value / conv.']
            group_report.ValuePerAllConversion = row['Value / all conv.']
            group_report.CostPerAllConversion = row['Cost / all conv.']
            group_report.CostPerConversion = row['Cost / conv.']
            # roas,all,all,conpv
            # group_report.ConvValPerCost = #######################################
            group_report.ClickAssistedConversions = row['Click Assisted Conv.']
            group_report.ImpressionAssistedConversions = row['Impr. Assisted Conv.']
            group_report.SearchExactMatchImpressionShare = row['Search Exact match IS']
            group_report.SearchImpressionShare = row['Search Impr. share']
            group_report.SearchRankLostImpressionShare = row['Search Lost IS (rank)']
            group_report.ContentImpressionShare = row['Content Impr. share']
            group_report.SearchAbsoluteTopImpressionShare = row['Search abs. top IS']
            group_report.SearchTopImpressionShare = row['Search top IS']
            group_report.SearchRankLostTopImpressionShare = row['Search lost top IS (rank)']
            group_report.SearchRankLostAbsoluteTopImpressionShare = row['Search lost abs. top IS (rank)']
            if group_report.Cost > 0:
                group_report.all_conversion_value_per_cost = group_report.AllConversionValue / group_report.Cost
                group_report.ROAS = group_report.ConversionValue / group_report.Cost
                group_report.conversion_value_per_cost = group_report.ConversionValue / group_report.Cost
            else:
                group_report.ROAS = 0
                group_report.ConvValPerCost = 0
                group_report.conversion_value_per_cost = 0

            if group_report.Clicks > 0:
                group_report.all_conversion_value_per_click = group_report.AllConversionValue / group_report.Clicks

            else:
                group_report.all_conversion_value_per_click = 0

            group_report.save()
            # group_report.save()


    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured while getting campaign attributes ---> {} .'.format(repr(ex)))


@app.task
def get_all_attributes_keyword():
    REPORT_TYPE = 'KEYWORDS_PERFORMANCE_REPORT'
    # Initialize appropriate service.
    # report_definition_service = client.GetService(
    #     'ReportDefinitionService', version='v201809')

    # Get report fields.
    # fields = report_definition_service.getReportFields(REPORT_TYPE)

    my_path = os.path.abspath(os.path.dirname(__file__))
    # print(my_path)
    FILENAME = my_path + "/res/keyword_attributes.txt"

    with open(FILENAME) as f:
        content = f.readlines()
    requiredFields = [x.strip() for x in content]
    # print(requiredFields)
    try:
        # Initialize appropriate service.
        report_downloader = client.GetReportDownloader(version='v201809')

        # Create report query.
        report = {
            'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
            'dateRangeType': 'LAST_7_DAYS',
            'reportType': REPORT_TYPE,
            'downloadFormat': 'CSV',

            'selector': {
                'fields': requiredFields,
                "predicates": [{
                    "field": "Status",
                    "operator": "IN",
                    "values": [
                        "ENABLED",
                        "PAUSED"
                    ]

                },

                    {
                        "field": "AdGroupStatus",
                        "operator": "IN",
                        "values": [
                            "ENABLED",
                            "PAUSED"
                        ]

                    }, {
                        "field": "CampaignStatus",
                        "operator": "IN",
                        "values": [
                            "ENABLED",
                            "PAUSED"
                        ]

                    }]

            }
        }
        if not os.path.exists(settings.STATIC_ROOT + '/keywords/'):
            os.makedirs(settings.STATIC_ROOT + '/keywords/')

        id = uuid.uuid4()
        file_name = '%s/keywords/%s.csv' % (settings.STATIC_ROOT, id)
        file = open('%s' % file_name, 'w+')
        report_downloader.DownloadReport(
            report, file, skip_report_header=True,
            skip_column_header=False, skip_report_summary=True,
            include_zero_impressions=True)

        file.close()
        # data = {}
        data = pd.read_csv(file_name)
        # print(len(data.columns))
        # os.remove(file_name)

        for index, row in data.iterrows():
            # access data using column names
            # attributes = [row[l] for l in list(data.columns)]
            # print(index,*attributes)

            try:
                keyword_report = KeywordPerformanceReportModel.objects.get(Id=row["Keyword ID"])

            except KeywordPerformanceReportModel.DoesNotExist:
                keyword_report = KeywordPerformanceReportModel()
                keyword_report.Id = row["Keyword ID"]
            keyword_report.CpcBid = row['Max. CPC']
            keyword_report.CampaignName = row['Campaign']
            keyword_report.AdGroupName = row['Ad group']
            keyword_report.KeywordMatchType = row['Match type']
            keyword_report.FirstPageCpc = row['First page CPC']
            keyword_report.TopOfPageCpc = row['Top of page CPC']
            keyword_report.FirstPositionCpc = row['First position CPC']
            keyword_report.Criteria = row['Keyword']
            keyword_report.Labels = row['Labels']
            keyword_report.LabelIds = row['Label IDs']
            keyword_report.ExternalCustomerId = row['Customer ID']
            keyword_report.CampaignId = row['Campaign ID']
            keyword_report.AdGroupId = row['Ad group ID']
            keyword_report.QualityScore = row['Quality score']
            keyword_report.HistoricalQualityScore = row['Qual. score (hist.)']
            keyword_report.SearchPredictedCtr = row['Expected clickthrough rate']
            keyword_report.HistoricalSearchPredictedCtr = row['Expected clickthrough rate (hist.)']
            keyword_report.PostClickQualityScore = row['Landing page experience']
            keyword_report.HistoricalLandingPageQualityScore = row['Landing page experience (hist.)']
            keyword_report.CreativeQualityScore = row['Ad relevance']
            keyword_report.HistoricalCreativeQualityScore = row['Ad relevance (hist.)']
            keyword_report.Clicks = row['Clicks']
            keyword_report.Impressions = row['Impressions']
            keyword_report.Cost = row['Cost']
            keyword_report.Ctr = row['CTR']
            keyword_report.AverageCpc = row['Avg. CPC']
            keyword_report.AveragePosition = row['Avg. position']
            keyword_report.TopImpressionPercentage = row['Impr. (Top) %']
            keyword_report.AbsoluteTopImpressionPercentage = row['Impr. (Abs. Top) %']
            keyword_report.Conversions = row['Conversions']
            keyword_report.AllConversions = row['All conv.']
            keyword_report.AllConversionValue = row['All conv. value']
            keyword_report.AllConversionRate = row['All conv. rate']
            keyword_report.ConversionValue = row['Total conv. value']
            keyword_report.ViewThroughConversions = row['View-through conv.']
            keyword_report.ConversionRate = row['Conv. rate']
            keyword_report.ValuePerConversion = row['Value / conv.']
            keyword_report.CostPerAllConversion = row['Cost / all conv.']
            keyword_report.CostPerConversion = row['Cost / conv.']
            keyword_report.ClickAssistedConversions = row['Click Assisted Conv.']
            keyword_report.ImpressionAssistedConversions = row['Impr. Assisted Conv.']
            keyword_report.SearchExactMatchImpressionShare = row['Search Exact match IS']
            keyword_report.SearchImpressionShare = row['Search Impr. share']
            keyword_report.SearchRankLostImpressionShare = row['Search Lost IS (rank)']
            keyword_report.SearchAbsoluteTopImpressionShare = row['Search abs. top IS']
            keyword_report.SearchTopImpressionShare = row['Search top IS']
            keyword_report.SearchRankLostTopImpressionShare = row['Search lost top IS (rank)']
            keyword_report.SearchRankLostAbsoluteTopImpressionShare = row['Search lost abs. top IS (rank)']
            if keyword_report.Cost > 0:
                keyword_report.all_conversion_value_per_cost = keyword_report.AllConversionValue / keyword_report.Cost
                keyword_report.ROAS = keyword_report.ConversionValue / keyword_report.Cost
                keyword_report.conversion_value_per_cost = keyword_report.ConversionValue / keyword_report.Cost
            else:
                keyword_report.ROAS = 0
                keyword_report.ConvValPerCost = 0
                keyword_report.conversion_value_per_cost = 0

            if keyword_report.Clicks > 0:
                keyword_report.all_conversion_value_per_click = keyword_report.AllConversionValue / keyword_report.Clicks

            else:
                keyword_report.all_conversion_value_per_click = 0

            keyword_report.save()
    except Exception as ex:
        print(repr(ex))
        logger.error('Exception occured while getting campaign attributes ---> {} .'.format(repr(ex)))


# def do_action_on_status(entitiy_id,value,scope,action_scope,):
#     # Initialize appropriate service.
#
#     service = client.GetService('CampaignService', version='v201809')
#
#     # Construct operations and update campaign.
#     operations = [{
#         'operator': 'SET',
#         'operand': {
#             'id': campaign_id,
#             'status': 'PAUSED'
#         }
#     }]
#     campaign_service.mutate(operations)
def get_all_groups_ids(campaign_ids):
    adgroup_ids = []
    for id in campaign_ids:
        objs = AdgroupPerformanceReportModel.objects.filter(CampaignId=id)
        for record in objs:
            adgroup_ids.append(record.AdGroupId)
    return adgroup_ids


def get_all_keywords_ids(group_ids):
    keyword_ids = []
    for id in group_ids:
        objs = KeywordPerformanceReportModel.objects.filter(AdGroupId=id)
        for record in objs:
            keyword_ids.append(record.Id)
    return keyword_ids


def apply_action(action_scope, ids, attribute_operand, operation, attribute_value):
    print("============================IN CAMPAIGN=============================0")
    ######################### To Be Continue ########################
    if attribute_operand == 'status':
        if action_scope == 'Campaign':
            for id in ids:
                update_campaign_status(id, attribute_value)
        elif action_scope == 'Groups':
            for id in ids:
                update_adgroup_status(id, attribute_value)
        elif action_scope == 'Keywords':
            for id in ids:
                update_keyword_status(id, attribute_value)
        if attribute_value == 'enable':
            print("Enabling these", action_scope)
        elif attribute_value == 'pause':
            print("Pause these", action_scope)
    elif attribute_operand == 'label':
        print("============================IN CAMPAIGN LABEL=============================1")
        if action_scope == 'Campaign':
            print("============================IN CAMPAIGN LABEL=============================2")
            print(ids, operation, attribute_value)
            update_campaign_labels(ids, operation, attribute_value)
        elif action_scope == 'Groups':
            print("============================IN AdGroup LABEL=============================2")
            print(type(ids), operation, attribute_value)
            update_adgroup_labels(ids, operation, attribute_value)
        elif action_scope == 'Keywords:':
            print("============================IN Keyword LABEL=============================2")
            print(ids, operation, attribute_value)
            update_keyword_labels(ids, operation, attribute_value)
        if operation == 'ADD':
            print('adding label to these ', action_scope, ids)
        elif operation == 'REMOVE':
            print('removing label from these ', action_scope, ids)
    elif attribute_operand == 'cpc':
        pass
    elif attribute_operand == 'cpm':
        pass
    elif attribute_operand == 'cpa':
        pass
    elif attribute_operand == 'roas':
        pass


def get_model(scope):
    if scope == "Campaign":
        return CampaignPerformanceReportModel
    elif scope == "Groups":
        return AdgroupPerformanceReportModel
    elif scope == "Keywords":
        return KeywordPerformanceReportModel


@app.task
def run_rule_engine():
    global temp_list
    for recipe in Rule_Engine_Recipe.objects.all():
        recipe_model = get_model(recipe.scope)
        # if recipe.scope == "Campaign":
        #     recipe_model = CampaignPerformanceReportModel
        # elif recipe.scope == "Groups":
        #     recipe_model = AdgroupPerformanceReportModel
        # elif recipe.scope == "Keywords":
        #     recipe_model = KeywordPerformanceReportModel
        for rule in Rule_Engine_Rules.objects.filter(recipe_id=recipe.id):
            # condition_list = []
            if rule:
                temp_list = {
                    recipe.scope: []
                }
            data = None
            found = 0
            total_conditions = 0
            for con in Rule_Engine_Conditions.objects.filter(rule_id=rule.id):
                total_conditions = total_conditions + 1
                print("=====================================================================")
                print(con.attribute_operand, con.value_operand)
                # print(type(con.attribute_operand), "=====================================================================")
                if con.scope == "Campaign":
                    scope_model = CampaignPerformanceReportModel
                    data = match_condition(scope_model, con.attribute_operand, con.value_operand, con.operation,
                                           con.operation_type)
                    if data:
                        for d in data:
                            recipe_scope_data = recipe_model.objects.filter(CampaignId=d.CampaignId)
                            for ids in recipe_scope_data:
                                append = ids.CampaignId if recipe.scope == 'Campaign' else (
                                    ids.AdGroupId if recipe.scope == 'Groups' else ids.Id)
                                temp_list[recipe.scope].append(append)
                elif con.scope == "Groups":
                    scope_model = AdgroupPerformanceReportModel
                    data = match_condition(scope_model, con.attribute_operand, con.value_operand, con.operation,
                                           con.operation_type)
                    if data:
                        for d in data:
                            recipe_scope_data = recipe_model.objects.filter(AdGroupId=d.AdGroupId)
                            for ids in recipe_scope_data:
                                append = ids.AdGroupId if recipe.scope == 'Groups' else ids.Id
                                temp_list[recipe.scope].append(append)

                elif con.scope == "Keywords":
                    scope_model = KeywordPerformanceReportModel
                    data = match_condition(scope_model, con.attribute_operand, con.value_operand, con.operation,
                                           con.operation_type)
                    if data:
                        for d in data:
                            recipe_scope_data = recipe_model.objects.filter(Id=d.Id)
                            for ids in recipe_scope_data:
                                temp_list[recipe.scope].append(ids.ID)
                if data:
                    found = found + 1
                    print("approved")
                else:
                    print("not approved")
            # print(total_conditions)
            if found == total_conditions:
                # condition_list.append(temp_list)
                (recipe_key, value), = temp_list.items()
                # print(temp_list)

                for ac in Rule_Engine_Action.objects.filter(rule_id=rule.id):
                    if recipe_key == 'Campaign':
                        campaign_ids = value
                        if ac.action_scope == 'Campaign':
                            apply_action(ac.action_scope, campaign_ids, ac.attribute_operand, ac.operation,
                                         ac.attribute_value)
                        elif ac.action_scope == 'Groups':
                            group_ids = get_all_groups_ids(campaign_ids)
                            apply_action(ac.action_scope, group_ids, ac.attribute_operand, ac.operation,
                                         ac.attribute_value)
                        elif ac.action_scope == 'Keywords':
                            group_ids = get_all_groups_ids(campaign_ids)
                            keyword_ids = get_all_keywords_ids(group_ids)
                            apply_action(ac.action_scope, keyword_ids, ac.attribute_operand, ac.operation,
                                         ac.attribute_value)
                    elif recipe_key == 'Groups':
                        group_ids = value
                        # print("in there not success",ac.action_scope)

                        if ac.action_scope == 'Groups':
                            # print("in there success")
                            apply_action(ac.action_scope, group_ids, ac.attribute_operand, ac.operation,
                                         ac.attribute_value)
                        elif ac.action_scope == 'Keywords':
                            keyword_ids = get_all_keywords_ids(group_ids)
                            apply_action(ac.action_scope, keyword_ids, ac.attribute_operand, ac.operation,
                                         ac.attribute_value)
                    elif recipe_key == 'Keywords':
                        keyword_ids = value
                        apply_action(ac.action_scope, keyword_ids, ac.attribute_operand, ac.operation,
                                     ac.attribute_value)

            else:
                print("not super approved")


def match_condition(scope_model, attribute_operand, value_operand, operation, operation_type):
    if operation_type == 'number':
        if operation == '<':
            return scope_model.objects.filter(**{attribute_operand + '__lt': value_operand})
        elif operation == '<=':
            return scope_model.objects.filter(**{attribute_operand + '__lte': value_operand})
        elif operation == '==':
            return scope_model.objects.filter(**{attribute_operand + '__exact': value_operand})
        elif operation == '>':
            return scope_model.objects.filter(**{attribute_operand + '__gt': value_operand})
        elif operation == '>=':
            return scope_model.objects.filter(**{attribute_operand + '__gte': value_operand})

    elif operation_type == 'string':
        if operation == '$':
            return scope_model.objects.filter(**{attribute_operand + '__endswith': value_operand})
        elif operation == '$ic':
            return scope_model.objects.filter(**{attribute_operand + '__iendswith': value_operand})
        elif operation == '^':
            return scope_model.objects.filter(**{attribute_operand + '__startswith': value_operand})
        elif operation == '^ic':
            return scope_model.objects.filter(**{attribute_operand + '__istartswith': value_operand})
        elif operation == 'c':
            return scope_model.objects.filter(**{attribute_operand + '__contains': value_operand})
        elif operation == 'cic':
            return scope_model.objects.filter(**{attribute_operand + '__icontains': value_operand})
        elif operation == 'e':
            return scope_model.objects.filter(**{attribute_operand + '__exact': value_operand})
        elif operation == 'eic':
            return scope_model.objects.filter(**{attribute_operand + '__iexact': value_operand})
        elif operation == 'in':
            return scope_model.objects.filter(**{attribute_operand + '__in': value_operand})
        elif operation == 'inic':
            to_lookup = '|'.join(value_operand.split(' '))
            return scope_model.objects.filter(**{attribute_operand + '__iregex': r'(' + to_lookup + ')'})
            # return scope_model.objects.filter(**{attribute_operand + '__lower__in': value_operand})
        elif operation == 'nc':
            return scope_model.objects.exclude(**{attribute_operand + '__contains': value_operand})
        elif operation == 'ncic':
            return scope_model.objects.exclude(**{attribute_operand + '__icontains': value_operand})
        elif operation == 'ne':
            return scope_model.objects.exclude(**{attribute_operand + '__exact': value_operand})
        elif operation == 'neic':
            return scope_model.objects.exclude(**{attribute_operand + '__iexact': value_operand})

    elif operation_type == 'label':
        if operation == 'e':
            print("currenting", scope_model.objects.get(id=67).Labels,
                  '["' + value_operand + '"]')

            return scope_model.objects.filter(**{attribute_operand + '__exact': '["' + value_operand + '"]'})
        elif operation == 'ea':
            print("problem")
            return scope_model.objects.filter(**{attribute_operand + '__contains': value_operand})
        elif operation == 'eic':
            return scope_model.objects.filter(**{attribute_operand + '__icontains': value_operand})
        elif operation == 'ne':
            return scope_model.objects.exclude(**{attribute_operand + '__contains': value_operand})
        elif operation == 'nea':
            return scope_model.objects.exclude(**{attribute_operand + '__contains': value_operand})
        elif operation == 'nic':
            return scope_model.objects.exclude(**{attribute_operand + '__icontains': value_operand})


def scheduel_ads_task(campaign_id,days,starttime,endtime):
    # Closed on Sunday, so don't configure an AdSchedule for Sunday.
    # monday_through_saturday = [
    #     'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'
    # ]
    campaign_criterion_service = client.GetService(
        'CampaignCriterionService', version='v201809')
    # Creates an operation to add an AdSchedule for each day of the week in the
    # list.
    # enums
    operations = [{
        'operator': 'ADD',
        'operand': {
            'campaignId': campaign_id,
            'criterion': {
                'xsi_type': 'AdSchedule',
                'dayOfWeek': day,
                # Start at 8:45 A.M.
                'startHour': 8,
                'startMinute': 'FORTY_FIVE',
                # End at 7:45 P.M.
                'endHour': 19,
                'endMinute': 'FORTY_FIVE',
            },
            # Run at normal bid rates.
            'bidModifier': 1.0
        }
    } for day in days]

    result = campaign_criterion_service.mutate(operations)
