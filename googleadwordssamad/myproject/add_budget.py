import time


def AddBudget(client, micro_amount):
    budget_service = client.GetService('BudgetService')

    operations = [{
        'operator': 'ADD',
        'operand': {
            'name': 'Budget #%s' % time.time(),
            'amount': {
                'microAmount': str(micro_amount)
            },
            'deliveryMethod': 'STANDARD'
        }
    }]
    return budget_service.mutate(operations)['value'][0]['budgetId']