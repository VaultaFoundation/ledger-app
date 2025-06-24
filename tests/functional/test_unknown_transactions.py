from json import load
import pytest

from ledgered.devices import Device, DeviceType # type: ignore
from ragger.backend.interface import RaisePolicy
from ragger.bip import pack_derivation_path
from ragger.navigator import NavInsID
from ragger.utils import split_message
from ragger.backend import BackendInterface
from ragger.navigator.navigation_scenario import NavigateWithScenario
from test_app_mainmenu_settings_cfg import test_app_mainmenu_settings_cfg

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
def test_malformed_transfer(test_name: str,
                            device: Device,
                            backend: BackendInterface,
                            scenario_navigator: NavigateWithScenario,
                            subdir: str,
                            transaction_filename: str):

    # navigate and turn on settings 
    if transaction_filename == 'transaction_unknown.json':
        test_app_mainmenu_settings_cfg(device, backend, scenario_navigator.navigator)

    folder_name = test_name + "/" + subdir + "/" + transaction_filename.replace(".json", "")

    signing_digest, message = load_transaction_from_file(transaction_filename, subdir)
    client = EosClient(backend)

    if device.is_nano:
        end_text = "^Sign$"
    else:
        end_text = "^Hold to sign$"
    with client.send_async_sign_message(VAULTA_PATH, message):
        scenario_navigator.review_approve(test_name=folder_name, custom_screen_text=end_text)
    rapdu = client.get_async_response()
    assert rapdu.status == STATUS_OK
    client.verify_signature(VAULTA_PATH, signing_digest, rapdu.data)