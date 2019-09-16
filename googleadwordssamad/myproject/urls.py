from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='template_main'),
    path('groups/', views.groups, name='template_groups'),
    path('keywords/', views.keywords, name='template_keywords'),
    path('campaigns/', views.campaigns, name='template_campaigns'),
    path('show/', views.show, name='template_show'),
    path('showkeywords/', views.showkeywords, name='template_show'),
    path('ruleEngine/', views.ruleEngine, name='template_ruleEngine'),
    path('rule_keywords/', views.rule_keywords, name='rule_keywords'),
    path('rule_adgroups/', views.rule_adgroups, name='rule_adgroups'),
    path('rule_campaign/', views.rule_campaign, name='rule_campaign'),
    path('addRules/', views.addRules, name='addRules'),
    path('createRecipe/', views.createRecipe, name='createRecipe'),
    path('recipe_dash/', views.recipe_dash, name='recipe_dash'),
    path('recipeSettings/', views.recipeSettings, name='recipeSettings'),


    path('condition/', views.condition, name='condition'),
    path('action/', views.action, name='action'),
    path('ajaxaction/', views.ajax_action, name='ajax_action'),
    path('ajax_action_options/', views.ajax_action_options, name='ajax_action'),

    path('adscheduler/',views.ad_scheduler,name='adScheduler')
    # path('buildrecipe/', views.buildRecipe, name='buildRecipe')

]
