from pysnmp import hlapi

def get_string_between(full_string: str, str1: str, str2: str) -> str: 
    try:
        print(full_string)
        idx1 = full_string.index(str1)
        idx2 = full_string.index(str2)
        return full_string[idx1 + len(str1) + 1: idx2]
    except ValueError:
        return '' 

def get_string_from_until(full_string: str, str_from: str, list_until: list) -> str:
    try:
        idx1 = full_string.index(str_from)
    except ValueError:
        return '' 
    
    full_string = full_string[idx1 + len(str_from):]
    res_string = ''
    for char in full_string:
        if char in list_until:
            return res_string
        res_string += char

    return res_string


def snmp_get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()) -> str:
    
    def cast(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return float(value)
            except (ValueError, TypeError):
                try:
                    return str(value)
                except (ValueError, TypeError):
                    pass
        return value

    def construct_object_types(list_of_oids):
        object_types = []
        for oid in list_of_oids:
            object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
        return object_types

    def fetch(handler, count):
        result = []
        for i in range(count):
            try:
                error_indication, error_status, error_index, var_binds = next(handler)
                if not error_indication and not error_status:
                    items = {}
                    for var_bind in var_binds:
                        items[str(var_bind[0])] = cast(var_bind[1])
                    result.append(items)
                else:
                    raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
            except StopIteration:
                break
        return result
    
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types(oids)
    )
    return fetch(handler, 1)[0]

def values_from_snmp_res(target, oid, credentials, port=161):
    snmp_res = snmp_get(target, [oid], credentials, port)
    data = get_string_between(str(snmp_res[oid]), '<<', '>>')

#print(snmp_get('127.0.0.1',['1.3.6.1.2.1.1.3.0'],hlapi.CommunityData('private'), port = 1024))

class SNMP_Helper():

    def __init__(self, ip, port=161, credentials = hlapi.CommunityData('private')):
        self.ip = ip
        self.port = port
        self.credentials = credentials
        self.data = None

    def is_snmp_connection_valid(self):
        try:
            self.data = snmp_get(self.ip, ['1.3.6.1.2.1.1.1'], self.credentials, self.port)
            return True
        except:
            return False

    def get_oid_sys_descr(self):
        """ 
        Para este caso, asumo que solo existe un objeto con ID 0 registrado en este SNMP, y por ende este será el que
        determinará si hay un CM en el SNMP o no. Entiendo que para una aplicación más abarcativa, sería necesario iterar
        sobre todos los OID presentes hasta encontrar el CM o acabar la lista. 
        """
        self.data = snmp_get(self.ip, ['1.3.6.1.2.1.1.1.0'], self.credentials, self.port)

        return self.data

    def is_cablemodem_parse_data(self):
        keywords = ('VENDOR', 'SW_REV', 'MODEL')
        sys_descr = self.data['1.3.6.1.2.1.1.1.0']
        for kw in keywords:
            if kw not in sys_descr:
                return False, {}
            
        stop_chars = (';', '>')
        return True, {
            'VENDOR': get_string_from_until(sys_descr, 'VENDOR: ', stop_chars),
            'SW_REV': get_string_from_until(sys_descr, 'SW_REV: ', stop_chars),
            'MODEL': get_string_from_until(sys_descr, 'MODEL: ', stop_chars),
        }
    

#snmp_helper = SNMP_Helper('127.0.0.1', 1024)
#print(snmp_helper.get_snmp_data('1.3.6.1.2.1.1.1.0'))
