import datetime

from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import DateInput
from .models import AdwordsCampaign, AdwordsCampaignGroup, AdwordsCampaignKeywords, Rule_Engine_Recipe

STATUS_CHOICES = [('U', 'UNKNOWN'), ('E', 'ENABLED'), ('P', 'PAUSED'), ('R', 'REMOVED')]
CHANNEL_TYPE = (('DISPLAY', 'DISPLAY'), ('SEARCH', 'SEARCH'))
FILTER_CHOICES = (('ENABLED', 'ENABLED'), ('PAUSED', 'PAUSED'))
CAMPAIGN_CHOICES = [(c.campaign_id, c.name) for c in AdwordsCampaign.objects.all()]

GROUP_CHOICES = list()
KEYWORD_CHOICES = list()
CAMPAIGN_CHOICES.append((None, 'Select Campaign'))
KEYWORD_CHOICES.append((None, 'Select Keyword'))
GROUP_CHOICES.append((None, 'Select Adgroup'))

days = [('all', 'All Days'), ('workdays', 'Monday - Friday'), ('weekend', 'Saturdays - Sundays'), ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'), ('WEDNESDAY', 'Wednesday'), ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'), ('SATURDAY', 'Saturday'), ('SUNDAY', 'Sunday')]
time = [(val, f'{(val // 60) % 59:02}' + ':' + f'{val % 60:02}') for val in range(45, 15 * 96, 15)]
for o in AdwordsCampaignKeywords.objects.all():
    g = AdwordsCampaignGroup.objects.get(pk=o.group_id)
    g_name = g.name
    c_name = AdwordsCampaign.objects.get(pk=g.campaign_id).name
    KEYWORD_CHOICES.append((o.keyword_id, o.text + " [Group: " + g_name + " , Campaign: " + c_name + " ]"))

for p in AdwordsCampaignGroup.objects.all():
    c_name = AdwordsCampaign.objects.get(pk=p.campaign_id).name
    GROUP_CHOICES.append((p.group_id, p.name + " [Campaign: " + c_name + " ]"))


class add_campaign(forms.Form):
    name = forms.CharField(label="Enter Campaign name:", max_length=100)
    status = forms.ChoiceField(label="Status", choices=STATUS_CHOICES)
    channelType = forms.ChoiceField(label="Channel Type", choices=CHANNEL_TYPE)
    start_date = forms.DateField(label="Start date", initial=datetime.datetime.now(),
                                 widget=DateInput(format='%Y-%m-%d',
                                                  attrs={'class': "input", 'placeholder': "yyyy/mm/dd"}))
    end_date = forms.DateField(label="End date", widget=DateInput(format='%Y-%m-%d', attrs={'class': "input",
                                                                                            'placeholder': "yyyy/mm/dd"}))
    budget = forms.CharField(label="Enter budget: ", max_length=15)


class add_groups(forms.Form):
    name = forms.CharField(label="Name:", max_length=100)
    status = forms.ChoiceField(label="Status", choices=STATUS_CHOICES)
    campaign_id = forms.ChoiceField(choices=CAMPAIGN_CHOICES)


class get_groups(forms.Form):
    campaign_id = forms.ChoiceField(choices=CAMPAIGN_CHOICES)


class add_keywords(forms.Form):
    text = forms.CharField(label="Keyword:", max_length=100)
    status = forms.ChoiceField(label="Status", choices=STATUS_CHOICES)

    # campaign=forms.ChoiceField(choices=CAMPAIGN_CHOICES)
    group = forms.ChoiceField(choices=GROUP_CHOICES)


class rule_keywords_form(forms.Form):
    keyword_id = forms.ChoiceField(label="Keyword", choices=KEYWORD_CHOICES)
    max_cpc = forms.IntegerField(label="Max CPC greater than", required=False)
    impressions = forms.IntegerField(label="Impressions less than", required=False)
    action = forms.ChoiceField(choices=(('ENABLED', 'Enable keywords'), ('PAUSED', 'Pause keywords')), label="Actions")


class rule_adgroups_form(forms.Form):
    group_id = forms.ChoiceField(label="Group name", choices=GROUP_CHOICES)
    max_ctr = forms.IntegerField(label="Max CTR", required=False)
    location = forms.CharField(label="Location", required=False)
    target_date = forms.DateField(label="Target date", widget=AdminDateWidget, required=False)
    action = forms.ChoiceField(choices=(('ENABLED', 'Enable adgroup'), ('PAUSED', 'Pause adgroup')), label="Actions")


class rule_campaign_form(forms.Form):
    keyword_id = forms.ChoiceField(choices=KEYWORD_CHOICES)
    max_cpc = forms.IntegerField(label="Max CPC", required=False)
    impressions = forms.IntegerField(label="Max Impressions", required=False)
    action = forms.ChoiceField(choices=(('ENABLED', 'Enable keywords'), ('PAUSED', 'Pause keywords')), label="Actions")


class recipe_settings_form(forms.Form):
    created_by = forms.CharField(label="Enter Your name:", max_length=100)
    recipe_name = forms.CharField(label="Enter Recipe name:", max_length=100)
    campaign_filter = forms.ChoiceField(choices=FILTER_CHOICES, label="Campaign Status", required=False)
    adgroup_filter = forms.ChoiceField(choices=FILTER_CHOICES, label="Adgroup Status", required=False)
    keyword_filter = forms.ChoiceField(choices=FILTER_CHOICES, label="Keyword Status", required=False)


class recipe_dash_form(forms.Form):
    recipe = forms.ChoiceField(choices=[], label="YOUR RECIPIES")

    def __init__(self, *args, **kwargs):
        super(recipe_dash_form, self).__init__(*args, **kwargs)
        self.fields['recipe'].choices = [(r.id, r.recipe_name) for r in Rule_Engine_Recipe.objects.all()]
        self.fields['recipe'].choices.append((None, 'Select Recipe'))


class adscheduler_form(forms.Form):
    campaign_name = forms.ChoiceField(choices=CAMPAIGN_CHOICES)
    days = forms.ChoiceField(choices=days, label="Days")
    starttime = forms.ChoiceField(choices=time, label="Start Time")
    endtime = forms.ChoiceField(choices=time, label="End Time")

    def clean(self):

        cleaned_data = super(adscheduler_form, self).clean()
        day = cleaned_data.get("days")
        start = cleaned_data.get("starttime")
        end = cleaned_data.get("endtime")
        if day:
            # print("====================", cleaned_data)
            if int(start) >= int(end):
                print("helllooo", type(start), end)
                raise forms.ValidationError("Start time cannot come after end time.")

        return cleaned_data
    # def __init__(self, *args, **kwargs):
    #     super(adscheduler, self).__init__(*args, **kwargs)
    #     self.fields['days'].choices = [d for d in days]
    #     self.fields['starttime'].choices = [t for t in time]
    #     self.fields['endtime'].choices = [t for t in time]
    # self.fields['recipe'].choices.append((None, 'Select Recipe'))
