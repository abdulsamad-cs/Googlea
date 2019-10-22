from __future__ import absolute_import
# -*- coding: utf-8 -*-


from django.contrib import messages
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from numpy import long

from .tasks import Add_new_Campaign, Add_new_group, Add_new_keyword
from .models import AdwordsCampaignRuleEngine_adgroups, Rule_Engine_Recipe, Rule_Engine_Rules, Rule_Engine_Conditions, \
    Rule_Engine_Action, AdScheduler_Model

from .forms import add_campaign, add_groups, get_groups, add_keywords, rule_keywords_form, rule_adgroups_form, \
    recipe_settings_form, recipe_dash_form, adscheduler_form
from .models import AdwordsCampaign, AdwordsCampaignGroup, AdwordsCampaignKeywords, AdwordsCampaignRuleEngine_keywords
from .utils.utils_data import Value_operand, Condition_scope, Action_scope, Action_dictionary, Action_options, \
    Name_of_Days
from .utils.utils_data import Operations_dictionary
from .utils.utils_data import Fields
from .utils.utils import getDate

from celery.utils.log import get_logger

logger = get_logger(__name__)

operations_dictionary = dict()
fields = []
RULE_COUNT = 1


def AdwordsCampaignList():
    return HttpResponse(AdwordsCampaign.objects.all())


def main(request):
    return render(request, 'myproject/main.html')


def show(request):
    # get_all_campaign()
    return render(request, 'myproject/show.html', {'data': AdwordsCampaign.objects.all()})


def showkeywords(request):
    # get_all_keywords()
    return render(request, 'myproject/showkeywords.html', {'keywords': AdwordsCampaignKeywords.objects.all()})


def campaigns(request):
    if request.method == 'POST' and 'btn_add_campaign' in request.POST:

        form = add_campaign(request.POST)
        if form.is_valid():
            # form.save()
            name = request.POST.get('name')
            status = request.POST.get('status')
            channelType = request.POST.get('channelType')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            budget = request.POST.get('budget')
            budget = long(float(budget)) * 1000000

            # Add_new_Campaign
            try:
                Add_new_Campaign.delay(name, status, channelType, start_date, end_date, budget)
                messages.add_message(request, messages.INFO,
                                     'Your Campaign will be added in a few seconds.')
            except Add_new_Campaign.OperationalError as exc:
                logger.exception('Sending task raised: %r', exc)


    else:
        form = add_campaign()
    context = {
        'add_campaign_form': form,
        'allcampaigns': AdwordsCampaign.objects.all()

    }
    return render(request, 'myproject/campaigns.html', context)


def groups(request):
    campaign_id_foriegn = 0
    if request.method == 'POST' and 'btn_addgroup' in request.POST:
        form1 = add_groups(request.POST)
        form2 = get_groups()
        if form1.is_valid():
            # id=request.POST.get('id')
            campaign_id = request.POST.get('campaign_id')
            name = request.POST.get('name')
            status = request.POST.get('status')
            Add_new_group.delay(campaign_id, name, status)
            messages.add_message(request, messages.INFO,
                                 'Your group will be added in a few seconds!\n Added Campaign id is :' + campaign_id)

    elif request.method == 'POST' and 'btn_getgroup' in request.POST:
        form2 = get_groups(request.POST)
        form1 = add_groups()
        if form2.is_valid():
            campaign_id = request.POST.get('campaign_id')
            obj = AdwordsCampaign.objects.get(campaign_id=campaign_id)
            campaign_id_foriegn = obj.id


    else:
        form1 = add_groups()
        form2 = get_groups()
    context = {
        'campaignid': campaign_id_foriegn,
        'allgroups': AdwordsCampaignGroup.objects.all().filter(campaign_id=campaign_id_foriegn),
        'add_group_form': form1,
        'get_group_form': form2,
    }
    return render(request, 'myproject/groups.html', context)


def keywords(request):
    if request.method == 'POST' and 'btn_addkeyword' in request.POST:
        form3 = add_keywords(request.POST)

        if form3.is_valid():
            group_id = request.POST.get('group')
            status = request.POST.get('status')
            text = request.POST.get('text')
            # messages.add_message(request, messages.INFO,'YYYY'+group_id)

            Add_new_keyword.delay(group_id, text, status)

            group = AdwordsCampaignGroup.objects.get(group_id=group_id)
            c_id = group.campaign_id
            campaign = AdwordsCampaign.objects.get(id=c_id)
            messages.add_message(request, messages.INFO,
                                 'Your keyword will be added in a few seconds!\nin campaign:' + campaign.name + ' in group: ' + group.name)


    else:
        form3 = add_keywords()

    context = {
        'add_keyword_form': form3
    }
    return render(request, 'myproject/keywords.html', context)


def ruleEngine(request):
    context = {

    }
    return render(request, 'myproject/ruleEngine.html', context)


def rule_keywords(request):
    if request.method == 'POST' and 'btn_add_rule' in request.POST:
        form = rule_keywords_form(request.POST)
        if form.is_valid():
            keyword_id = request.POST.get('keyword_id')
            if keyword_id:
                max_impressions = request.POST.get('impressions')
                max_cpc = request.POST.get('max_cpc')
                action = request.POST.get('action')
                try:
                    obj = AdwordsCampaignRuleEngine_keywords.objects.get(keyword_id=keyword_id)
                except AdwordsCampaignRuleEngine_keywords.DoesNotExist:
                    obj = AdwordsCampaignRuleEngine_keywords()
                    obj.keyword_id = keyword_id

                g_id = AdwordsCampaignKeywords.objects.get(keyword_id=keyword_id).group_id
                obj.group = AdwordsCampaignGroup.objects.get(pk=g_id)

                obj.action = action
                obj.max_cpc = -999 if max_cpc == '' else max_cpc
                obj.impressions = -999 if max_impressions == '' else max_impressions
                obj.save()



    else:
        form = rule_keywords_form()
    context = {
        'rule_keywords_form': form
    }

    return render(request, 'myproject/rule_keywords.html', context)


def rule_adgroups(request):
    if request.method == 'POST' and 'btn_add_rule' in request.POST:
        form = rule_adgroups_form(request.POST)
        if form.is_valid():
            group_id = request.POST.get('group_id')
            if group_id:
                location = request.POST.get('location')
                max_ctr = request.POST.get('max_ctr')
                target_date = request.POST.get('target_date')
                action = request.POST.get('action')
                try:
                    obj = AdwordsCampaignRuleEngine_adgroups.objects.get(group_id=group_id)
                except AdwordsCampaignRuleEngine_adgroups.DoesNotExist:
                    obj = AdwordsCampaignRuleEngine_adgroups()
                    obj.group_id = group_id

                c_id = AdwordsCampaignGroup.objects.get(group_id=group_id).campaign_id
                obj.campaign = AdwordsCampaign.objects.get(pk=c_id)

                obj.action = action
                obj.max_ctr = -999 if max_ctr == '' else max_ctr
                obj.location = location
                obj.target_date = target_date
                obj.save()



    else:
        form = rule_adgroups_form()
    context = {
        'rule_adgroups_form': form
    }

    return render(request, 'myproject/rule_adgroups.html', context)


def rule_campaign(request):
    if request.method == 'POST' and 'btn_add_rule' in request.POST:
        form = rule_keywords_form(request.POST)
        if form.is_valid():
            keyword_id = request.POST.get('keyword_id')
            if keyword_id:
                max_impressions = request.POST.get('impressions')
                max_cpc = request.POST.get('max_cpc')
                action = request.POST.get('action')
                try:
                    obj = AdwordsCampaignRuleEngine_keywords.objects.get(keyword_id=keyword_id)
                except AdwordsCampaignRuleEngine_keywords.DoesNotExist:
                    obj = AdwordsCampaignRuleEngine_keywords()
                    obj.keyword_id = keyword_id

                g_id = AdwordsCampaignKeywords.objects.get(keyword_id=keyword_id).group_id
                obj.group = AdwordsCampaignGroup.objects.get(pk=g_id)

                obj.action = action
                obj.max_cpc = -999 if max_cpc == '' else max_cpc
                obj.impressions = -999 if max_impressions == '' else max_impressions
                obj.save()



    else:
        form = rule_keywords_form()
    context = {
        'rule_keywords_form': form
    }

    return render(request, 'myproject/rule_keywords.html', context)


def createRecipe(request):
    context = {
        #   'rule_keywords_form': form
    }
    return render(request, 'myproject/createRecipe.html', context)


def recipeSettings(request):
    if 'btn_scope' in request.POST:
        request.session['scope'] = request.POST['btn_scope']

    if request.method == 'POST' and 'btn_proceed' in request.POST:
        form = recipe_settings_form(request.POST)
        recipe_id = request.POST.get('recipe_id')

        if form.is_valid():
            recipe_name = request.POST.get('recipe_name')
            created_by = request.POST.get('created_by')
            try:
                obj = Rule_Engine_Recipe.objects.get(pk=recipe_id)
            except Rule_Engine_Recipe.DoesNotExist:
                obj = Rule_Engine_Recipe()
            obj.recipe_name = recipe_name
            obj.scope = request.session['scope']
            obj.created_by = created_by
            obj.save()
            # RULE_COUNT = 1
            request.session['recipe_id'] = obj.id
            print("Recipe id:", request.session['recipe_id'])

            # context = {
            #     'scope': request.session['scope'],
            #
            # }
            # return redirect('/myproject/addRules/')
            # return render(request, 'myproject/addRules.html', context)
            return redirect('/addRules/')


    else:
        form = recipe_settings_form()
        print("this code is running why in recipesettings:------>>>>>>>>>>")
        context = {
            'scope': request.session['scope'],
            'recipe_setting_form': form
        }
        return render(request, 'myproject/recipeSettings.html', context)


rule_id_dict = dict()


@csrf_exempt
def addRules(request):
    edit_all_rule = dict()
    for rule in Rule_Engine_Rules.objects.filter(recipe_id=request.session['recipe_id']):
        edit_all_rule[rule.rule_name] = {
            'all_conditions': [],
            'all_actions': []
        }
        for con in Rule_Engine_Conditions.objects.filter(rule_id=rule.id):
            # try:
            edit_all_rule[rule.rule_name]['all_conditions'].append(
                {
                    'current_scope': con.scope,
                    'date_range': con.date_range,
                    'attribute_operand_tagvalue': con.attribute_operand,
                    'attribute_operation_tagvalue': con.operation,
                    'operation_type': con.operation_type,
                    'value_operand_tagvalue': con.value_operand,
                    'attribute_operand': next(i[0] for i in Fields[con.scope] if i[1] == con.attribute_operand),
                    'attribute_operation': Operations_dictionary[con.operation_type][con.operation],
                    'value_operand': con.value_operand
                }
            )
        # except StopIteration as e:
        #     logger.exception('No conditions found: %r', e)

        for ac in Rule_Engine_Action.objects.filter(rule_id=rule.id):
            # try:
            print(ac.operation)
            edit_all_rule[rule.rule_name]['all_actions'].append(
                {'current_action_scope_value': ac.action_scope,
                 'action_attribute_operand_value': ac.attribute_operand,
                 'action_operation_value': ac.operation,
                 'action_attribute_operand': next(
                     i[0] for i in Action_dictionary[ac.action_scope] if i[1] == ac.attribute_operand),
                 'action_operation': next(
                     i[0] for i in Action_options[ac.attribute_operand] if i[1] == ac.operation),
                 'action_value_operand': ac.attribute_value,
                 'current_action_scope': next(
                     i[0] for i in Action_scope[ac.action_scope] if i[1] == ac.action_scope)
                 }
            )
        # except StopIteration as e:
        #     print("eorret caight")
        #     logger.exception('No actions found: %r', e)

        if len(edit_all_rule[rule.rule_name]['all_conditions']) > 0 and len(
                edit_all_rule[rule.rule_name]['all_actions']) > 0:
            rule_id_dict[rule.rule_name] = rule.id
            request.session['rule_id_dict'] = rule_id_dict

        print("Break point 2 =================== >", request.session['rule_id_dict'])

    print(edit_all_rule)

    context = {

        'scope': request.session['scope'],
        'condition_scope': Condition_scope,
        'action_scope': Action_scope,
        'action_dictionary': Action_dictionary,
        'fields': Fields[request.session['scope']],
        'operations': Operations_dictionary,
        'values_operand': Value_operand,
        'recipe_id': request.session['recipe_id'],
        'edit_all_rules': edit_all_rule

    }

    if request.method == 'POST' and request.is_ajax() and 'addrule' == request.POST['action']:
        all_rules = json.loads(request.POST.get('all_rules'))
        all_rules_for_print = json.loads(request.POST.get('all_rules_for_print'))

        print("=============all rules==========")
        print(all_rules)
        print("=============for print==========")
        print(all_rules_for_print)
        for each_rule_keys, each_rule_vals in all_rules.items():
            try:
                if 'rule_id_dict' in request.session:
                    if each_rule_keys in request.session['rule_id_dict'] and request.POST['recipe_id'] == \
                            request.session['recipe_id']:
                        rule_id = request.session['rule_id_dict'][each_rule_keys]
                    else:
                        rule_id = -1
                else:
                    rule_id = -1
                rule_obj = Rule_Engine_Rules.objects.get(pk=rule_id)
            except Rule_Engine_Rules.DoesNotExist:
                rule_obj = Rule_Engine_Rules()
            rule_obj.recipe = Rule_Engine_Recipe.objects.get(pk=request.session['recipe_id'])
            rule_obj.rule_name = each_rule_keys
            if len(each_rule_vals['all_conditions']) > 0 and len(each_rule_vals['all_actions']) > 0:
                rule_obj.save()
                print("Rule saved : ", each_rule_keys)
                rule_id_dict[each_rule_keys] = rule_obj.id
                request.session['rule_id_dict'] = rule_id_dict

                print("Break point 1 =================== >", request.session['rule_id_dict'])

                for row in Rule_Engine_Conditions.objects.filter(
                        rule_id=request.session['rule_id_dict'][each_rule_keys]):
                    print(row)
                    row.delete()
                for row in Rule_Engine_Action.objects.filter(rule_id=request.session['rule_id_dict'][each_rule_keys]):
                    print(row)
                    row.delete()

                for con in each_rule_vals['all_conditions']:
                    print("condition added")
                    condition_obj = Rule_Engine_Conditions()
                    condition_obj.scope = con['current_scope']
                    condition_obj.operation = con['attribute_operation_tagvalue']
                    condition_obj.attribute_operand = con['attribute_operand_tagvalue']
                    condition_obj.value_operand = con['value_operand']
                    start_date, end_date = getDate(con['date_range'])
                    condition_obj.start_date = start_date
                    condition_obj.end_date = end_date
                    condition_obj.date_range = con['date_range']
                    condition_obj.operation_type = con['operation_type']
                    condition_obj.recipe = Rule_Engine_Recipe.objects.get(pk=request.session['recipe_id'])
                    condition_obj.rule = rule_obj
                    condition_obj.save()
                for ac in each_rule_vals['all_actions']:
                    # print(ac)
                    action_obj = Rule_Engine_Action()
                    # action_obj.scope = ac['current_action_scope_value']
                    action_obj.attribute_operand = ac['action_attribute_operand_value']
                    print("=================================================", ac['action_operation_value'])
                    action_obj.operation = ac['action_operation_value']
                    action_obj.attribute_value = ac['action_value_operand']
                    action_obj.action_scope = ac['current_action_scope_value']

                    # print("Recipe foriegn id:", action_obj.recipe)
                    action_obj.rule = rule_obj
                    action_obj.save()

    return render(request, 'myproject/addRules.html', context)


def ajax_action(request):
    val = 0
    if request.is_ajax():
        val = request.POST['action_on']
        context = {
            'action_dictionary': Action_dictionary[val],
        }
        return render(request, 'myproject/ajax_action.html', context)
    context = {
        'action_dictionary': Action_dictionary[val],
    }
    print(context['action_dictionary'])
    return render(request, 'myproject/addRules.html', context)


def ajax_action_options(request):
    val = 0
    if request.is_ajax():
        val = request.POST['action_option']
        context = {
            'action_options': Action_options[val],
        }
        return render(request, 'myproject/ajax_action_options.html', context)
    context = {
        'action_dictionary': Action_dictionary[val],
    }
    print(context['action_dictionary'])
    return render(request, 'myproject/addRules.html', context)


def recipe_dash(request):
    if request.method == 'POST' and 'btn_edit_recipe' in request.POST:
        form = recipe_dash_form(request.POST)
        request.session['recipe_id'] = request.POST['recipe']
        if form.is_valid():
            for key, value in request.session.items():
                print('{} => {}'.format(key, value))
            print(request.POST['recipe'])

            return redirect('/addRules/')

    else:
        form = recipe_dash_form()
    context = {
        'recipe_dash_form': form
    }
    return render(request, 'myproject/recipe_dash.html', context)


@csrf_exempt
def condition(request):
    if request.is_ajax():
        scope = request.POST['current_scope']
        context = {
            'fields': Fields[scope]
        }
        return render(request, 'myproject/load_scope.html', context)
        # return HttpResponse(json.dumps(context), 'myproject/condition.html')
    context = {
        'fields': Fields[request.session['scope']],
        'operations': Operations_dictionary,
        'values_operand': Value_operand

    }
    return render(request, 'myproject/addRules.html', context)


def action(request):
    context = {
        # 'recipe_dash_form': form
    }
    return render(request, 'myproject/action.html', context)


def ad_scheduler(request):
    context = {
        'starttime': [],
        'endtime': [],
        'days': []
    }
    if request.method == 'POST':

        if request.is_ajax():
            print("ajax call here")
            obj = AdScheduler_Model.objects.filter(campaign_id=request.POST['campaign_id'])
            print(obj)
            if obj:
                for o in obj:
                    context['starttime'].append(o.starttime)
                    context['endtime'].append(o.endtime)
                    context['days'].append(o.day)
                print(context)
            return HttpResponse(json.dumps(context), content_type="application/json")
            # return render(request, 'myproject/adscheduler.html',context)

        form = adscheduler_form(request.POST)
        starttime = request.POST.getlist('starttime')
        endtime = request.POST.getlist('endtime')
        days = request.POST.getlist('days')
        print(request.POST)

        if form.is_valid():
            print("valid")
            try:
                AdScheduler_Model.objects.filter(campaign_id=request.POST['campaign_name']).delete()
                context['saved'] = 1
            except AdScheduler_Model.DoesNotExist:
                pass
            data = []
            for i in range(len(days)):
                # if days[i] == 'all':
                #     for j in range(7):
                #         obj = AdScheduler_Model()
                #         obj.starttime = starttime[i]
                #         obj.endtime = endtime[i]
                #         obj.day = Name_of_Days[j]
                #         obj.campaign_id = request.POST['campaign_name']
                #         obj.save()
                # elif days[i] == 'workdays':
                #     for j in range(5):
                #         obj = AdScheduler_Model()
                #         obj.starttime = starttime[i]
                #         obj.endtime = endtime[i]
                #         obj.day = Name_of_Days[j]
                #         obj.campaign_id = request.POST['campaign_name']
                #         obj.save()
                # elif days[i] == 'weekend':
                #     for j in range(5, 7):
                #         obj = AdScheduler_Model()
                #         obj.starttime = starttime[i]
                #         obj.endtime = endtime[i]
                #         obj.day = Name_of_Days[j]
                #         obj.campaign_id = request.POST['campaign_name']
                #         obj.save()
                # else:
                #     obj = AdScheduler_Model()
                #     obj.starttime = starttime[i]
                #     obj.endtime = endtime[i]
                #     obj.day = days[i]
                #     obj.campaign_id = request.POST['campaign_name']
                #     obj.save()
                obj = AdScheduler_Model()
                obj.starttime = starttime[i]
                obj.endtime = endtime[i]
                obj.day = days[i]
                obj.campaign_id = request.POST['campaign_name']
                obj.save()
                print("savad====>")
                data.append({'id': request.POST['campaign_name'], 'day': days[i],
                             'start_time': starttime[i], 'end_time': endtime[i]})

            print(data)
        # else:
        #     print(days)
        elif len(days) == 0:
            print("deleting")
            AdScheduler_Model.objects.filter(campaign_id=request.POST['campaign_name']).delete()


    else:
        form = adscheduler_form()

    context['adscheduler'] = form
    return render(request, 'myproject/adscheduler.html', context)


def save_data():
    pass
