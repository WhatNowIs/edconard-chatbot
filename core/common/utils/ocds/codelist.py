
def convert_currency(value):
    code_map = {
        'FRW': 'RWF'
    }
    return code_map.get(value, '') if value else ''


def convert_tender_type(value):
    code_map = {
        'G': 'goods',
        'W': 'works',
        'NC': 'services',
        'C': 'consultingServices'
    }
    return code_map.get(value, value)


def convert_tender_status(value):
    code_map = {
        'D':'active',#TODO Request mapping for this value
        'ADV': 'planned',
        'OPE': 'active',#TODO Request mapping for this value
        'EVA': 'active',#TODO Request mapping for this value
        'RVA': 'active',#TODO Request mapping for this value
        'CAN': 'cancelled',
        '': 'unsuccessful',
        'CON': 'complete',
        'WIT': 'withdrawn'
    }
    return code_map.get(value, value)

def convert_tender_method(value):
    code_map = {
        # 'CP':'',
        # 'FA':'',
        'NCB': 'open',
        'ICB': 'open',
        'RFQ': 'selective',
        'NRT': 'limited',
        'IRT': 'limited',
        'SS': 'direct'
    }
    return code_map.get(value, value)


def convert_award_status(value):
    code_map = {
        'REV': 'pending',
        'SUS': 'pending',
        'EVA': 'pending',
        'CON': 'active',
        'CAN': 'cancelled',
        '': 'unsuccessful'
    }
    return code_map.get(value, value)

def convert_contract_status(value):
    code_map = {
        'EC0411': 'pending',
        'EC0731': 'active',
        'EC0543': 'cancelled',
        'EC0684': 'terminated',
        'EC0301': 'pending',#TODO Request mapping for this value
        'EC0302': 'pending',#TODO Request mapping for this value
        'EC0303': 'pending',#TODO Request mapping for this value
        'EC0304': 'pending',#TODO Request mapping for this value
        'EC0402': 'pending',#TODO Request mapping for this value
        'EC0403': 'pending',#TODO Request mapping for this value
        'EC0404': 'pending',#TODO Request mapping for this value
        'EC0412': 'pending',#TODO Request mapping for this value
        'EC0413': 'pending',#TODO Request mapping for this value
        'EC0522': 'pending',#TODO Request mapping for this value
        'EC0523': 'pending',#TODO Request mapping for this value
        'EC0524': 'pending',#TODO Request mapping for this value
        'EC0531': 'pending',#TODO Request mapping for this value
        'EC0533': 'pending',#TODO Request mapping for this value
        'EC0545': 'pending',#TODO Request mapping for this value
        'EC0641': 'pending',#TODO Request mapping for this value
        'EC0642': 'pending',#TODO Request mapping for this value
        'EC0643': 'pending',#TODO Request mapping for this value
        'EC0653': 'pending',#TODO Request mapping for this value
        'EC0661': 'pending',#TODO Request mapping for this value
        'EC0682': 'pending',#TODO Request mapping for this value
        'EC0732': 'pending', #TODO Request mapping for this value
        'EC0733': 'pending', #TODO Request mapping for this value
        'EC0751': 'pending', #TODO Request mapping for this value
        'EC0752': 'pending', #TODO Request mapping for this value
        'EC0753': 'pending',#TODO Request mapping for this value
        'EC0754': 'pending',#TODO Request mapping for this value
    }
    return code_map.get(value, value)