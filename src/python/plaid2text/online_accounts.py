#! /usr/bin/env python3

from collections import OrderedDict
import datetime
import os
import sys
import textwrap

import plaid
from plaid.api import plaid_api
from plaid import Configuration
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.transactions_get_request import TransactionsGetRequest

import plaid2text.config_manager as cm
from plaid2text.interact import prompt, clear_screen, NullValidator
from plaid2text.interact import NumberValidator, NumLengthValidator, YesNoValidator, PATH_COMPLETER


class PlaidAccess():
    def __init__(self, client_id=None, secret=None):
        if client_id and secret:
            self.client_id = client_id
            self.secret = secret
        else:
            self.client_id, self.secret = cm.get_plaid_config()

        plaid_conf = Configuration(
            host=plaid.Environment.Development,
            api_key = {
                'clientId': self.client_id,
                'secret': self.secret
            }
        )
        api_client = plaid.ApiClient(plaid_conf)
        self.client = plaid_api.PlaidApi(api_client)

    def get_transactions(self,
                         access_token,
                         start_date,
                         end_date,
                         account_ids):
        """Get transaction for a given account for the given dates"""

        ret = []
        total_transactions = None
        page = 0
        account_array = []
        account_array.append(account_ids)
        while True:
            page += 1
            if total_transactions:
                print("Fetching page %d, already fetched %d/%d transactions" % ( page, len(ret), total_transactions))
            else:
                print("Fetching page 1")

            try:
                options = TransactionsGetRequestOptions()
                options.account_ids = account_array
                options.offset = len(ret)
                request = TransactionsGetRequest(
                    access_token=access_token,
                    start_date=start_date.date(),
                    end_date=end_date.date(),
                    options=options
                )
                response = self.client.transactions_get(request)
            except plaid.ApiException as e:
                print("Unable to update plaid account [%s] due to: " % account_ids, file=sys.stderr)
                print("    %s" % e, file=sys.stderr)
                sys.exit(1)

            total_transactions = response['total_transactions']

            def scrub(doc):
                r = doc.to_dict()
                for k in ['date', 'datetime', 'authorized_date', 'authorized_datetime']:
                    if k in r and r[k] is not None:
                        r[k] = r[k].isoformat()
                return r

            ret.extend(list(map(scrub, response['transactions'])))

            if len(ret) >= total_transactions: break

        print("Downloaded %d transactions for %s - %s" % ( len(ret), start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

        return ret
