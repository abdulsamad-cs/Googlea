from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'googleadwordssamad.settings')
app = Celery('googleadwordssamad', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    # "get-campaign": {
    #        "task": "googleadwordssamad.myproject.tasks.get_all_campaign",
    #        "schedule": 10.0
    #     },

    #
    #
    # "get-adwords-groups": {
    #        "task": "googleadwordssamad.myproject.tasks.get_all_groups",
    #          "schedule": 10.0
    #        },
    #
    #
    # "update-keywords-in-database": {
    #     "task": "googleadwordssamad.myproject.tasks.updateKeywordsInDatabase",
    #
    #     "schedule": 10.0
    # },

    # "rule-engine": {
    #     "task": "googleadwordssamad.myproject.tasks.rule_engine",
    #     "schedule": 10.0
    # },

    #
    # "location-task": {
    #              "task": "googleadwordssamad.myproject.tasks.pause_adgroup_location",
    #              "schedule": 10.0
    #          },
    #
    "get-campaign-report": {
                 "task": "googleadwordssamad.myproject.tasks.get_all_attributes_campaign",
                 "schedule": 10.0
             },
    # "get-adgroup-report": {
    #     "task": "googleadwordssamad.myproject.tasks.get_all_attributes_adgroup",
    #     "schedule": 10.0
    # },
    # "get-keyword-report": {
    #     "task": "googleadwordssamad.myproject.tasks.get_all_attributes_keyword",
    #     "schedule": 10.0
    # },
    # "run-rule-engine": {
    #     "task": "googleadwordssamad.myproject.tasks.run_rule_engine",
    #     "schedule": 10.0
    # },

}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


if __name__ == '__main__':
    app.start()
