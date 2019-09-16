from googleads import adwords


REPORT_TYPE = 'ADGROUP_PERFORMANCE_REPORT'


def main(client, report_type):
  print("==================================="+client.client_customer_id)
  # Initialize appropriate service.
  report_definition_service = client.GetService(
      'ReportDefinitionService', version='v201809')

  # Get report fields.
  fields = report_definition_service.getReportFields(report_type)

  # Display results.
  print ('Report type "%s" contains the following fields:' % report_type)
  print(fields)
  for field in fields:
    print( ' - %s (%s)(%s)' % (field['fieldName'], field['fieldType'],field['displayFieldName']))
    if 'enumValues' in field:
      print ('  := [%s]' % ', '.join(field['enumValues']))

  #write_in_text_file("Group.txt",fields)


def write_in_text_file(name,fields):
  file = open(name,"w")
  for field in fields:
    file.write(field['fieldName']+","+field['fieldType']+"\n")
  file.close()


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, REPORT_TYPE)


