from django.db import models
from jsonfield import JSONField
from prompt_toolkit.validation import ValidationError
from datetime import datetime


ADWORDS_CAMPAIGN_STATUS = (('U', 'UNKNOWN'), ('E', 'ENABLED'), ('P', 'PAUSED'), ('R', 'REMOVED'))
GROUP_STATUS = (('U', 'UNKNOWN'), ('E', 'ENABLED'), ('P', 'PAUSED'), ('R', 'REMOVED'))
CHANNEL_TYPE = (('DISPLAY', 'DISPLAY'), ('SEARCH', 'SEARCH'))
KEYWORD_STATUS = (('E', 'ENABLED'), ('D', 'DELETED'), ('P', 'PAUSED'))
NOT_ENTERED = -999


class AdwordsCampaign(models.Model):
    objects = models.Manager()
    campaign_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=ADWORDS_CAMPAIGN_STATUS, default='U')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    conversion_optimizer_eligibility = models.BooleanField(null=True, blank=True)
    settings = JSONField(blank=True,
                         default='{"xsi_type": "TargetingSetting","details": [{"xsi_type": "TargetingSettingDetail","criterionTypeGroup": "PLACEMENT","targetAll": "false"},{"xsi_type": "TargetingSettingDetail","criterionTypeGroup": "VERTICAL","targetAll": "true"}]}')
    bidding_strategy_configuration = JSONField(blank=True,
                                               default='{"bids": [{"xsi_type" : "CpcBid","bid": {"microAmount": "1000000"}}]}')
    # channel type values contains: SEARCH, DISPLAY
    advertising_channel_type = models.CharField(max_length=15, choices=CHANNEL_TYPE, default='SEARCH')
    label = models.CharField(max_length=255, null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     o = super().save(*args, **kwargs)
    #     print('IM SAVED =========================================================')
    #     return o

    def __str__(self):
        return "%s campaign with id %s" % (self.name, self.campaign_id)

    class Meta:
        db_table = 'adwords_campaign'


class AdwordsCampaignGroup(models.Model):
    objects = models.Manager()
    campaign = models.ForeignKey(AdwordsCampaign, on_delete=models.CASCADE)
    group_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=GROUP_STATUS, default='U')

    def __str__(self):
        return "%s campaign with group %s" % (self.campaign.name, self.name)

    class Meta:
        db_table = 'adwords_campaign_groups'


class AdwordsCampaignKeywords(models.Model):
    objects = models.Manager()
    # campaign = models.ForeignKey(AdwordsCampaign, on_delete=models.CASCADE)
    group = models.ForeignKey(AdwordsCampaignGroup, on_delete=models.CASCADE)

    keyword_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    text = models.CharField(max_length=255)
    clicks = models.IntegerField(default=1)
    impressions = models.IntegerField(default=1)
    max_cpc = models.IntegerField(default=1)
    status = models.CharField(max_length=10, choices=KEYWORD_STATUS, default='P', null=True, blank=True)

    def __str__(self):
        return "%s group with keyword %s" % (self.group.name, self.keyword_id)

    class Meta:
        db_table = 'adwords_campaign_keywords'


'''
class AdwordsCampaignRuleEngine(models.Model):
    keyword = models.ForeignKey(AdwordsCampaignKeywords,  on_delete=models.CASCADE)
    group = models.ForeignKey(AdwordsCampaignGroup,  on_delete=models.CASCADE)
    clicks = models.IntegerField(default=1)
    impressions = models.IntegerField(default=1)
    max_cpc = models.IntegerField(default=1)
    start_date = models.DateField(auto_now=True)
    end_date = models.DateField()
    status = models.CharField(max_length=1, choices=KEYWORD_STATUS, default='P', null=True, blank=True)

    def __str__(self):
        return "%s group with keyword %s" % (self.group.name, self.keyword.text)

    class Meta:
        db_table = 'adwords_campaign_group_rule_engine'

'''


class AdwordsCampaignRuleEngine_keywords(models.Model):
    objects = models.Manager()
    keyword_id = models.CharField(max_length=255, null=True, unique=True)
    group = models.ForeignKey(AdwordsCampaignGroup, on_delete=models.CASCADE)
    max_cpc = models.IntegerField(blank=True)
    impressions = models.IntegerField(blank=True)
    action = models.CharField(max_length=20, default='Select action', blank=True)

    def clean(self):
        if self.max_cpc == NOT_ENTERED or self.impressions == NOT_ENTERED:
            raise ValidationError("You must specify either cpc or impressions")

    def __str__(self):
        return "%s group with keyword %s" % (self.group.name, self.keyword.text)

    class Meta:
        db_table = 'adwords_campaign_keywords_rule_engine'


class AdwordsCampaignRuleEngine_adgroups(models.Model):
    objects = models.Manager()
    group_id = models.CharField(max_length=255, null=True, unique=True)
    campaign = models.ForeignKey(AdwordsCampaign, on_delete=models.CASCADE)
    target_date = models.DateField(blank=True, auto_now=True)
    max_ctr = models.IntegerField(blank=True, default=NOT_ENTERED)
    location = models.CharField(max_length=70, blank=True)
    action = models.CharField(max_length=20, default='Select action', blank=True)

    class Meta:
        db_table = 'adwords_campaign_adgroups_rule_engine'


class CampaignPerformanceReportModel(models.Model):
    objects = models.Manager()
    CampaignId = models.CharField(max_length=255, null=True, blank=True, unique=True)
    CampaignName = models.CharField(max_length=255, null=True, blank=True)
    Labels = models.CharField(max_length=255, null=True, blank=True)
    LabelIds = models.CharField(max_length=255, null=True, blank=True)

    BiddingStrategyType = models.CharField(max_length=255, null=True, blank=True)
    ExternalCustomerId = models.CharField(max_length=255, null=True, blank=True)
    AdvertisingChannelType = models.CharField(max_length=255, null=True, blank=True)

    Clicks = models.IntegerField(default=0)
    Impressions = models.IntegerField(default=0)
    Cost = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    Ctr = models.CharField(max_length=50, null=True, blank=True)
    AverageCpc = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AveragePosition = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    TopImpressionPercentage = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AbsoluteTopImpressionPercentage = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    Conversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AllConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AllConversionRate = models.CharField(max_length=50, null=True, blank=True)
    AllConversionValue = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    ConversionValue = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ViewThroughConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ConversionRate = models.CharField(max_length=50, null=True, blank=True)
    ValuePerConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ValuePerAllConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    CostPerAllConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    CostPerConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ROAS = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    all_conversion_value_per_cost = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    all_conversion_value_per_click = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    conversion_value_per_cost = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    ClickAssistedConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ImpressionAssistedConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    SearchExactMatchImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    SearchImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    SearchRankLostImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    SearchBudgetLostImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    ContentRankLostImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    ContentImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    SearchAbsoluteTopImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    SearchClickShare = models.CharField(max_length=50, null=True, blank=True)
    SearchTopImpressionShare = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    SearchRankLostTopImpressionShare = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    SearchRankLostAbsoluteTopImpressionShare = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    class Meta:
        db_table = 'campaign_performance_report'


class AdgroupPerformanceReportModel(models.Model):
    objects = models.Manager()
    CpcBid = models.CharField(max_length=255, null=True, blank=True)
    CampaignName = models.CharField(max_length=255, null=True, blank=True)
    AdGroupName = models.CharField(max_length=255, null=True, blank=True)
    Labels = models.CharField(max_length=255, null=True, blank=True)
    LabelIds = models.CharField(max_length=255, null=True, blank=True)
    EffectiveTargetRoas = models.CharField(max_length=50, null=True, blank=True)
    TargetCpa = models.CharField(max_length=50, null=True, blank=True)
    ExternalCustomerId = models.CharField(max_length=255, null=True, blank=True)
    CampaignId = models.CharField(max_length=255, null=True, blank=True)
    AdGroupId = models.CharField(max_length=255, null=True, blank=True, unique=True)
    Clicks = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    Impressions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    Cost = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    Ctr = models.CharField(max_length=50, null=True, blank=True)
    AverageCpc = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AveragePosition = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    TopImpressionPercentage = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AbsoluteTopImpressionPercentage = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    Conversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AllConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AllConversionValue = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AllConversionRate = models.CharField(max_length=50, null=True, blank=True)
    ConversionValue = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ViewThroughConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ConversionRate = models.CharField(max_length=50, null=True, blank=True)
    ValuePerConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ValuePerAllConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    CostPerAllConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    CostPerConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    ROAS = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    all_conversion_value_per_cost = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    all_conversion_value_per_click = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    conversion_value_per_cost = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    ClickAssistedConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ImpressionAssistedConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    SearchExactMatchImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    SearchImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    SearchRankLostImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    ContentImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    SearchAbsoluteTopImpressionShare = models.CharField(max_length=50, null=True, blank=True)
    SearchTopImpressionShare = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    SearchRankLostTopImpressionShare = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    SearchRankLostAbsoluteTopImpressionShare = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    class Meta:
        db_table = 'adgroup_performance_report'


class KeywordPerformanceReportModel(models.Model):
    objects = models.Manager()
    CpcBid = models.CharField(max_length=255, null=True, blank=True)
    CampaignName = models.CharField(max_length=255, null=True, blank=True)
    AdGroupName = models.CharField(max_length=255, null=True, blank=True)
    KeywordMatchType = models.CharField(max_length=255, null=True, blank=True)
    FirstPageCpc = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    TopOfPageCpc = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    FirstPositionCpc = models.CharField(max_length=255, null=True, blank=True)
    Criteria = models.CharField(max_length=255, null=True, blank=True)
    Labels = models.CharField(max_length=255, null=True, blank=True)
    LabelIds = models.CharField(max_length=255, null=True, blank=True)

    ExternalCustomerId = models.CharField(max_length=255, null=True, blank=True)
    CampaignId = models.CharField(max_length=255, null=True, blank=True)
    AdGroupId = models.CharField(max_length=255, null=True, blank=True)
    Id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    QualityScore = models.CharField(max_length=255, null=True, blank=True)
    HistoricalQualityScore = models.CharField(max_length=255, null=True, blank=True)
    SearchPredictedCtr = models.CharField(max_length=255, null=True, blank=True)
    HistoricalSearchPredictedCtr = models.CharField(max_length=255, null=True, blank=True)
    PostClickQualityScore = models.CharField(max_length=255, null=True, blank=True)
    HistoricalLandingPageQualityScore = models.CharField(max_length=255, null=True, blank=True)
    CreativeQualityScore = models.CharField(max_length=255, null=True, blank=True)
    HistoricalCreativeQualityScore = models.CharField(max_length=255, null=True, blank=True)

    Clicks = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    Impressions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    Cost = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    Ctr = models.CharField(max_length=255, null=True, blank=True)
    AverageCpc = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AveragePosition = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    TopImpressionPercentage = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AbsoluteTopImpressionPercentage = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    Conversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AllConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AllConversionValue = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    AllConversionRate = models.CharField(max_length=255, null=True, blank=True)
    ConversionValue = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ViewThroughConversions = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ConversionRate = models.CharField(max_length=255, null=True, blank=True)
    ValuePerConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    CostPerAllConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    CostPerConversion = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    ROAS = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    all_conversion_value_per_cost = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    all_conversion_value_per_click = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)
    conversion_value_per_cost = models.DecimalField(default=0.0, max_digits=30, decimal_places=2)

    ClickAssistedConversions = models.CharField(max_length=255, null=True, blank=True)
    ImpressionAssistedConversions = models.CharField(max_length=255, null=True, blank=True)
    SearchExactMatchImpressionShare = models.CharField(max_length=255, null=True, blank=True)
    SearchImpressionShare = models.CharField(max_length=255, null=True, blank=True)
    SearchRankLostImpressionShare = models.CharField(max_length=255, null=True, blank=True)
    SearchAbsoluteTopImpressionShare = models.CharField(max_length=255, null=True, blank=True)
    SearchTopImpressionShare = models.CharField(max_length=255, null=True, blank=True)
    SearchRankLostTopImpressionShare = models.CharField(max_length=255, null=True, blank=True)
    SearchRankLostAbsoluteTopImpressionShare = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'keyword_performance_report'


class Rule_Engine_Recipe(models.Model):
    objects = models.Manager()
    recipe_name = models.CharField(max_length=255, null=True, blank=True, default='New Recipe')
    date_created = models.DateField(blank=True, auto_now=True)
    scope = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'recipe'


class Rule_Engine_Rules(models.Model):
    objects = models.Manager()
    rule_name = models.CharField(max_length=255, null=True, blank=True, default='New rule')
    recipe = models.ForeignKey(Rule_Engine_Recipe, on_delete=models.CASCADE)

    class Meta:
        db_table = 'rules'




class Rule_Engine_Conditions(models.Model):
    objects = models.Manager()
    date_range = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(blank=True, auto_now=True)
    end_date = models.DateField(blank=True, default=datetime.now)
    recipe = models.ForeignKey(Rule_Engine_Recipe, on_delete=models.CASCADE)
    attribute_operand = models.CharField(max_length=255, null=True, blank=True)
    operation = models.CharField(max_length=255, null=True, blank=True)
    value_operand = models.CharField(max_length=255, null=True, blank=True)
    scope = models.CharField(max_length=255, null=True, blank=True)
    operation_type = models.CharField(max_length=255, null=True, blank=True)
    rule = models.ForeignKey(Rule_Engine_Rules, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'conditions'


class Rule_Engine_Action(models.Model):
    objects = models.Manager()
    attribute_operand = models.CharField(max_length=255, null=True, blank=True)
    operation = models.CharField(max_length=255, null=True, blank=True)
    attribute_value = models.CharField(max_length=255, null=True, blank=True)
    action_scope = models.CharField(max_length=255, null=True, blank=True)
    rule = models.ForeignKey(Rule_Engine_Rules, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'actions'

class AdScheduler_Model(models.Model):
    objects = models.Manager()
    campaign_id= models.CharField(max_length=255, null=True, blank=True)
    day=models.CharField(max_length=255, null=True, blank=True)
    starttime=models.CharField(max_length=255, null=True, blank=True)
    endtime=models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = 'adscheduler'
