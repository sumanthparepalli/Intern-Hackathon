import json
import os
import requests

'''For when the user checks out'''


def pullFundsCall(amount, senderCardExpiry, senderCurrencyCode, senderPAN, senderStreet, senderPostelCode):
    true = True
    certPath = ('cert.pem', 'key_7ece49ea-fd19-487a-bca6-cbe7edb2876c.pem')
    url = 'https://sandbox.api.visa.com/visadirect/fundstransfer/v1/pullfundstransactions'
    authentication = ("WKQIY36SGORRI5NSZ8W921bLPb6TiRgo4UnT-n6G0z1c4MZno", 'P91RQSSjrxRxpKdE6OiM4654')
    head = {'Accept': 'application/json', 'Authorization': '{base64 encoded userid:password}',
            'Content-type': 'application/json'}
    body = {"acquirerCountryCode": "840", "acquiringBin": "408999", "amount": amount, "businessApplicationId": "AA",
            "cardAcceptor": {"address": {"country": "USA", "county": "081", "state": "CA", "zipCode": "94404"},
                             "idCode": "ABCD1234ABCD123", "name": "Visa Inc. USA-Foster City",
                             "terminalId": "ABCD1234"}, "cavv": "0700100038238906000013405823891061668252",
            "foreignExchangeFeeTransaction": "11.99", "localTransactionDateTime": "2020-06-27T15:14:21",
            "retrievalReferenceNumber": "330000550000", "senderCardExpiryDate": senderCardExpiry,
            "senderCurrencyCode": senderCurrencyCode, "senderPrimaryAccountNumber": senderPAN, "surcharge": "11.99",
            "systemsTraceAuditNumber": "451001", "nationalReimbursementFee": "11.22",
            "cpsAuthorizationCharacteristicsIndicator": "Y",
            "addressVerificationData": {"street": senderStreet, "postalCode": senderPostelCode},
            "settlementServiceIndicator": "9",
            "colombiaNationalServiceData": {"countryCodeNationalService": "170", "nationalReimbursementFee": "20.00",
                                            "nationalNetMiscAmountType": "A",
                                            "nationalNetReimbursementFeeBaseAmount": "20.00",
                                            "nationalNetMiscAmount": "10.00", "addValueTaxReturn": "10.00",
                                            "taxAmountConsumption": "10.00", "addValueTaxAmount": "10.00",
                                            "costTransactionIndicator": "0", "emvTransactionIndicator": "1",
                                            "nationalChargebackReason": "11"},
            "riskAssessmentData": {"delegatedAuthenticationIndicator": True, "lowValueExemptionIndicator": true,
                                   "traExemptionIndicator": true, "trustedMerchantExemptionIndicator": true,
                                   "scpExemptionIndicator": true}, "visaMerchantIdentifier": "73625198"}
    response = requests.post(url=url, auth=authentication, headers=head, json=body, cert=certPath)
    # print(response)
    return json.loads(response.text)


# For Sending money to merchants at the end of the day
def merchantPushFundsCall(amount, merchantAccNo, ClosebuyAccNo, senderName):
    true = True
    certPath = ('cert.pem', 'key_7ece49ea-fd19-487a-bca6-cbe7edb2876c.pem')
    url = 'https://sandbox.api.visa.com/visadirect/mvisa/v1/merchantpushpayments'
    authentication = ("WKQIY36SGORRI5NSZ8W921bLPb6TiRgo4UnT-n6G0z1c4MZno", 'P91RQSSjrxRxpKdE6OiM4654')
    head = {'Accept': 'application/json', 'Authorization': '{base64 encoded userid:password}',
            'Content-type': 'application/json'}
    body = {
        {
            "acquirerCountryCode": "356",
            "acquiringBin": "408972",
            "amount": amount,
            "businessApplicationId": "MP",
            "cardAcceptor": {
                "address": {
                    "city": "KOLKATA",
                    "country": "IN"
                },
                "idCode": "CA-IDCode-77765",
                "name": "Visa Inc. USA-Foster City"
            },
            "localTransactionDateTime": "2020-07-02T03:42:47",
            "purchaseIdentifier": {
                "type": "0",
                "referenceNumber": "REF_123456789123456789123"
            },
            "recipientPrimaryAccountNumber": merchantAccNo,
            "retrievalReferenceNumber": "412770451035",
            "secondaryId": "123TEST",
            "senderAccountNumber": ClosebuyAccNo,
            "senderName": senderName,
            "senderReference": "",
            "systemsTraceAuditNumber": "451035",
            "transactionCurrencyCode": "356",
            "merchantCategoryCode": "5812",
            "settlementServiceIndicator": "9"
        }}
    response = requests.post(url=url, auth=authentication, headers=head, json=body, cert=certPath)
    # print(response)
    return json.loads(response.text)


# For direct credit donations
def pushFundsCall(amount, merchantName, merchantPAN, senderAccNo, senderAdrres, senderCity, senderName):
    true = True
    certPath = ('cert.pem', 'key_7ece49ea-fd19-487a-bca6-cbe7edb2876c.pem')
    url = 'https://sandbox.api.visa.com/visadirect/fundstransfer/v1/pushfundstransactions'
    authentication = ("WKQIY36SGORRI5NSZ8W921bLPb6TiRgo4UnT-n6G0z1c4MZno", 'P91RQSSjrxRxpKdE6OiM4654')
    head = {'Accept': 'application/json', 'Authorization': '{base64 encoded userid:password}',
            'Content-type': 'application/json'}
    body = {
        {
            "acquirerCountryCode": "840",
            "acquiringBin": "408999",
            "amount": amount,  # 124.05
            "businessApplicationId": "AA",
            "cardAcceptor": {
                "address": {
                    "country": "USA",
                    "county": "San Mateo",
                    "state": "CA",
                    "zipCode": "94404"
                },
                "idCode": "CA-IDCode-77765",
                "name": "Visa Inc. USA-Foster City",
                "terminalId": "TID-9999"
            },
            "localTransactionDateTime": "2020-07-02T03:48:35",
            "merchantCategoryCode": "6012",
            "pointOfServiceData": {
                "motoECIIndicator": "0",
                "panEntryMode": "90",
                "posConditionCode": "00"
            },
            "recipientName": merchantName,  # rohan
            "recipientPrimaryAccountNumber": merchantPAN,  # 4957030420210496
            "retrievalReferenceNumber": "412770451018",
            "senderAccountNumber": senderAccNo,  # 4653459515756154
            "senderAddress": senderAdrres,  # 901 Metro Center Blvd
            "senderCity": senderCity,  # Foster City
            "senderCountryCode": "124",
            "senderName": senderName,  # Mohammed Qasim
            "senderReference": "",
            "senderStateCode": "CA",
            "sourceOfFundsCode": "05",
            "systemsTraceAuditNumber": "451018",
            "transactionCurrencyCode": "USD",
            "transactionIdentifier": "381228649430015",
            "settlementServiceIndicator": "9",
            "colombiaNationalServiceData": {
                "countryCodeNationalService": "170",
                "nationalReimbursementFee": "20.00",
                "nationalNetMiscAmountType": "A",
                "nationalNetReimbursementFeeBaseAmount": "20.00",
                "nationalNetMiscAmount": "10.00",
                "addValueTaxReturn": "10.00",
                "taxAmountConsumption": "10.00",
                "addValueTaxAmount": "10.00",
                "costTransactionIndicator": "0",
                "emvTransactionIndicator": "1",
                "nationalChargebackReason": "11"
            }
        }}
    response = requests.post(url=url, auth=authentication, headers=head, json=body, cert=certPath)
    # print(response)
    return json.loads(response.text)
