"""
Modified from https://gist.github.com/samuelstevens9/ef37ac880dbf31200d41b831342c8d95
https://api.slack.com/incoming-webhooks#sending_messages
{
  "text":"Read <https://api.slack.com/incoming-webhooks#sending_messages|Send Slack Message> for more details @slackuser #general"
  "link_names": 1
}
"""
import requests,json
def print_slack(message_text=None,payload_obj=None,slack_url=None):
  if(not payload_obj and message_text):
    payload_obj = {"text":message_text,"link_names":1}
  r = requests.put(slack_url,data=json.dumps(payload_obj))
