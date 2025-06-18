from json import load
import pytest

from ledgered.devices import Device, DeviceType # type: ignore
from ragger.backend.interface import RaisePolicy
from ragger.bip import pack_derivation_path
from ragger.navigator import NavInsID
from ragger.utils import split_message
from ragger.backend import BackendInterface
from ragger.navigator.navigation_scenario import NavigateWithScenario

from apps.eos import EosClient, STATUS_OK, ErrorType, MAX_CHUNK_SIZE
from apps.eos_transaction_builder import Transaction
from utils import ROOT_SCREENSHOT_PATH, CORPUS_DIR, TAGGED_CORPUS_FILES
# Proposed EOS derivation paths for tests ###
VAULTA_PATH = "m/44'/194'/12345'"

def load_transaction_from_file(transaction_filename, subdir=None):
    if subdir:
        transaction_file_path = CORPUS_DIR / subdir / transaction_filename
    else:
        transaction_file_path = CORPUS_DIR / transaction_filename

    with transaction_file_path.open("r", encoding="utf-8") as f:
        obj = load(f)

    return Transaction().encode(obj)

# These files are in the corpus 
unknown_trans = [(None,'transaction_unknown.json'),
                ('wampus','transaction_badparam.json'),
                ('wampus','transaction_noparams.json'),
                ('wampus','transaction_nomemo.json')]

@pytest.mark.parametrize("subdir, transaction_filename", unknown_trans)
def test_malformed_transfer(test_name,
                                    device,
                                    backend,
                                    navigator,
                                    subdir,
                                    transaction_filename):
    
    folder_name = test_name + "/" + transaction_filename.replace(".json", "")
    if subdir:
        folder_name = test_name + "/" + subdir + "/" + transaction_filename.replace(".json", "")
    _, message = load_transaction_from_file(transaction_filename, subdir)

    client = EosClient(backend)
    # Get appversion and "data_allowed parameter"
    # This works on both the emulator and a physical device
    data_allowed, version = client.send_get_app_configuration()
    assert data_allowed is False
    payload = pack_derivation_path(VAULTA_PATH) 
    
    
    with client.send_async_sign_message_full(payload, True):
        backend.raise_policy = RaisePolicy.RAISE_NOTHING
        navigator.navigate_and_compare(ROOT_SCREENSHOT_PATH,
                    folder_name,
                    [NavInsID.RIGHT_CLICK,NavInsID.RIGHT_CLICK,NavInsID.BOTH_CLICK],
                    screen_change_before_first_instruction=False)