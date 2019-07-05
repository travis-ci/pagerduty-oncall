#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Modified from https://gist.github.com/simonfiddaman/5bcfe162aecc20cb534ef40ed849cf02
""" List On-calls on Slack"""

import os
import json
import logging

# Use the PagerDuty Python REST API Sessions library
# https://pagerduty.github.io/pdpyras/
# A local copy is included with this release
from pdpyras import APISession

from slack import print_slack

def main():
    """ Do all the things """

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    secrets = {
       'pagerduty': {'key':  os.environ.get('PAGERDUTY_API_KEY')},
       'slack': {'url': os.environ.get('SLACK_API_URL')}
    }
    config = {
      'responders': [
        {
          'escalation_policy_ids': [ os.environ.get('PAGERDUTY_ESCALATION_POLICY_ID') ],
          'schedule_ids': [ os.environ.get('PAGERDUTY_SCHEDULE_ID') ]
        }
      ]
    }

    # instantiate a pdpyras object
    api = APISession(
        secrets.get('pagerduty').get('key'), # PagerDuty API token from secrets
        'PagerDuty' # Name for logging (optional)
        ## or, with default_from:
        #'PagerDuty', # Name for logging (optional)
        #'user@example.com' # default_from for request header - must be a valid PagerDuty user
        )

    for responder in config.get('responders'):
        # Generally speaking, at the first esclation level where these schedule(s) are mentioned,
        # there should be only one active on-call, regardless of time of day.
        # The expectation is that a level with split day/night or follow-the-sun responsibility will not overlap.

        logging.debug('Retrieving oncalls from PagerDuty API')

        # Poll for a single oncall, based on a schedule id and escalation policy id
        # The use of both Schedule and Escalation Policy limits scope
        oncalls = api.iter_all(
            'oncalls', # method
            {
                #"include[]": "users", # including users doesn't give us the contact details
                "schedule_ids[]": responder.get('schedule_ids'),
                "escalation_policy_ids[]": responder.get('escalation_policy_ids')
            } #params
        )
        oncalls_list = api.get(
            'oncalls', # method
            params={
                #"include[]": "users", # including users doesn't give us the contact details
                "schedule_ids[]": responder.get('schedule_ids'),
                "escalation_policy_ids[]": responder.get('escalation_policy_ids')
            } #params
        )
        logging.debug(oncalls_list.text)

        if oncalls:
            for oncall in oncalls:
                # If we have a Live Call Routing number configured, just display it here
                if responder.get('lcr'):
                    ## directly print the result
                    # schedule - Live Call Routing: +xx xxxxxx,,x User Name until yyyy-mm-ddThh:mm:ssZ
                    msg = u'`{}` - Live Call Routing: `{}` {} until {}'.format(
                        oncall.get('schedule').get('summary'),
                        responder.get('lcr'),
                        oncall.get('user').get('summary'),
                        oncall.get('end')
                    )


                # We don't have an LCR configured, so find the user's phone number(s)
                else:
                    response = api.request(
                        'get', # requests type
                        '/users/{}'.format(oncall.get('user').get('id')), # get single user
                        params={"include[]": "contact_methods"} # include contact _details_
                    )
                    # prepare an empty phone list to populate - there could be more than one
                    phone = {}
                    if response.ok:
                        user = response.json()['user']
                        # loop through all of the contact methods, looking for phone numbers
                        for contact_method in user.get('contact_methods'):
                            logging.debug(u'Contact Method: %s %s',
                                        contact_method.get('type'),
                                        contact_method.get('label'))
                            # add phone numbers in the constructed format to the `phone` list
                            if 'phone' in contact_method['type']:
                                phone[contact_method.get('label')] = u'`{}: +{} {}`'.format(
                                    contact_method.get('label'),
                                    contact_method.get('country_code'),
                                    contact_method.get('address'))
                    # if no `contact_methods` of type `phone`
                    if not phone:
                        phone['EMPTY'] = 'NO PHONE ENTRIES FOUND'

                    ## print the result
                    # schedule - user name - Work: +xx xxxxxx, Mobile: +xx xxxxxx until yyyy-mm-ddThh:mm:ssZ
                    msg = u'{}: *{}* - {} until {}'.format(
                        oncall.get('schedule').get('summary'),
                        oncall.get('user').get('summary'),
                        ', '.join(phone.values()),
                        oncall.get('end')
                        )
                    print(msg)
                    print_slack(message_text=msg, slack_url=secrets.get('slack').get('url'))

                # In the event that multiple results are returned, the first result is provided
                break

        else:
            logging.critical('No oncalls returned')


if __name__ == '__main__':
    main()
