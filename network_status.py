from stem import Flag
from stem.descriptor import DocumentHandler, parse_file
from stem.descriptor.remote import DescriptorDownloader
from config import CONSENSUS_PATH


def download_consensus():
    downloader = DescriptorDownloader()
    consensus = downloader.get_consensus(document_handler=DocumentHandler.DOCUMENT).run()[0]

    with open(CONSENSUS_PATH, 'w') as descriptor_file:
        descriptor_file.write(str(consensus))


def _get_da_ip_from_consensus():
    consensus = next(parse_file(
        CONSENSUS_PATH,
        document_handler=DocumentHandler.DOCUMENT,
        validate=True
    ))

    authorities_ip_list = []

    for fingerprint, relay in consensus.routers.items():
        if Flag.AUTHORITY in relay.flags:
            # print("%s: %s (%s)" % (fingerprint, relay.address, relay.nickname))
            authorities_ip_list.append(relay.address)

    return authorities_ip_list


HARDCODED_DIRECTORY_IP_LIST = [
    '37.218.247.217',
    '204.13.164.118',
    '199.58.81.140',
    '193.23.244.244',
    '194.109.206.212',
    '86.59.21.38',
    '128.31.0.34',
    '171.25.193.9',
    '154.35.175.225',
    '131.188.40.189'
]


def get_directory_addresses(use_hardcode=False):
    if use_hardcode:
        return HARDCODED_DIRECTORY_IP_LIST

    directories_ip = None

    try:
        print('Reading cached-consensus')
        directories_ip = _get_da_ip_from_consensus()
    except FileNotFoundError:
        print('Consensus not found. Trying to download...')
        download_consensus()
        directories_ip = _get_da_ip_from_consensus()
    except:
        return None

    return directories_ip
