import re

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Lease, CableModem
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .utils import get_string_between, snmp_get, SNMP_Helper

class JsonResponseStructure:

    def __init__(self):
        self.error_code = 0
        self.error_str = None
        self.result = 'success'
        self.items = {}

    def update_items(self, items):
        self.items = items

    def update_to_failure(self, code, message):
        self.error_code = code
        self.error_str = message
        self.result = 'failure'

    @property
    def json_response(self):
        return JsonResponse({
            "errorCode": self.error_code,
            "errorStr": self.error_str,
            "result": self.result,
            "items": self.items,
        })

@require_POST
@csrf_exempt
def cm_data(request, cm_address):

    def is_cm_address_valid(address):
        return bool(re.match(pattern=r'^[a-zA-Z0-9]{12}$', string=address))
    
    res = JsonResponseStructure()

    if not is_cm_address_valid(cm_address):
        res.update_to_failure(405, "The CM address format is invalid")
        return res.json_response  

    try: 
        lease = Lease.objects.get(mac = cm_address)

    except Lease.DoesNotExist:
        res.update_to_failure(404, "Cable Modem not found")
        return res.json_response
    
    if lease.already_queried is True:
        res.update_to_failure(409, "Cable Modem info already stored")
        return res.json_response
    
    snmp_helper = SNMP_Helper(lease.ip, 1024)

    if not snmp_helper.is_snmp_connection_valid():
        res.update_to_failure(408, "SNMP Timeout")
        return res.json_response
    
    a = snmp_helper.get_oid_sys_descr()
    is_cm, cm_data = snmp_helper.is_cablemodem_parse_data()

    if is_cm:
        res.update_items(cm_data)
        CableModem.objects.create(
            vendor = cm_data["VENDOR"], 
            model = cm_data["MODEL"], 
            software_version = cm_data["SW_REV"], 
        ).save()
        lease.already_queried = True
        lease.save()

    else:
        res.update_to_failure(410, "A cablemodem with a valid data format was not found at the desired IP")

    return res.json_response

