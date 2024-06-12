from utils.config import get_config

def generate_ocid(number):
    try:
        ocid_prefix = get_config("OCID")
        return f"{ocid_prefix}-{number}"
    except Exception as e:
        # Handle the exception here
        raise Exception(f"Error generating OCID: {e}")


def generate_release_id(ocid, publication_datetime):
    try:
        formatted_datetime = publication_datetime.strftime("%d%m%Y%H%M")
        return f"{ocid}-{formatted_datetime}"
    except Exception as e:
        # Handle the exception here
        raise Exception(f"Error generating release ID: {e}")


def generate_supplier_id(supplier_identifier):
    try:
        suplr_prefix = get_config("SUPLR_PREFIX")
        return f"{suplr_prefix}-{supplier_identifier}"
    except Exception as e:
        # Handle the exception here
        raise Exception(f"Error generating supplier ID: {e}")


def generate_procuring_entity_id(tin):
    try:
        pe_prefix = get_config("PE_PREFIX")
        return f"{pe_prefix}-{tin}"
    except Exception as e:
        # Handle the exception here
        raise Exception(f"Error generating procuring entity ID: {e}")
