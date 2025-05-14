from json import load
import pytest

from ragger.backend.interface import RaisePolicy
from ragger.bip import pack_derivation_path
from ragger.navigator import NavInsID
from ragger.utils import split_message
from ragger.backend import BackendInterface
from ragger.firmware import Firmware
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

# Remove files with no tag and pull out refused trx
# corner case transaction that are handled separately
transactions = [
    item for item in list(TAGGED_CORPUS_FILES)
    if item[0] is not None
        and item[1] != 'transaction_refused.json'
        and item[1] != 'transaction_badparam.json'
        and item[1] != 'transaction_noparams.json'
]

refused_trans = [('eosio','transaction_refused.json'),('vaulta','transaction_refused.json')]
unknown_trans = [(None,'transaction_unknown.json'),
                ('wampus','transaction_badparam.json'),
                ('wampus','transaction_noparams.json')]

# TAGGED_CORPUS_FILE is a list of two elements, the subdirectory and the base filename
# out parameterized tests accepts a list of tuples

@pytest.mark.parametrize("subdir, transaction_filename", transactions)
def test_sign_transaction_accepted(test_name: str,
                                   firmware: Firmware,
                                   backend: BackendInterface,
                                   scenario_navigator: NavigateWithScenario,
                                   subdir: str,
                                   transaction_filename: str):
    folder_name = test_name + "/" + subdir + "/" + transaction_filename.replace(".json", "")

    signing_digest, message = load_transaction_from_file(transaction_filename, subdir)
    client = EosClient(backend)

    if firmware.is_nano:
        end_text = "^Sign$"
    else:
        end_text = "^Hold to sign$"
    with client.send_async_sign_message(VAULTA_PATH, message):
        scenario_navigator.review_approve(test_name=folder_name, custom_screen_text=end_text)
    rapdu = client.get_async_response()
    assert rapdu.status == STATUS_OK
    client.verify_signature(VAULTA_PATH, signing_digest, rapdu.data)

@pytest.mark.parametrize("subdir, transaction_filename", refused_trans)
def test_sign_transaction_refused(test_name: str,
                                  firmware: Firmware,
                                  backend: BackendInterface,
                                  scenario_navigator: NavigateWithScenario,
                                  subdir: str,
                                  transaction_filename: str):

    folder_name = test_name + "/" + subdir + "/" + transaction_filename.replace(".json", "")
    _, message = load_transaction_from_file(transaction_filename, subdir)
    client = EosClient(backend)
    backend.raise_policy = RaisePolicy.RAISE_NOTHING
    if firmware.is_nano:
        end_text = "^Cancel$"
        with client.send_async_sign_message(VAULTA_PATH, message):
            scenario_navigator.review_reject(test_name=folder_name, custom_screen_text=end_text)
        rapdu = client.get_async_response()
        assert rapdu.status == ErrorType.USER_CANCEL
        assert len(rapdu.data) == 0
    else:
        for i in range(4):
            with client.send_async_sign_message(VAULTA_PATH, message):
                scenario_navigator.review_reject(test_name=folder_name + f"/part{i}")
            rapdu = client.get_async_response()
            assert rapdu.status == ErrorType.USER_CANCEL
            assert len(rapdu.data) == 0


def get_nano_review_instructions(num_screen_skip):
    instructions = [NavInsID.RIGHT_CLICK] * num_screen_skip
    instructions.append(NavInsID.BOTH_CLICK)
    return instructions


# This transaction contains multiples actions which doesn't fit in one APDU.
# Therefore the app implementation ask the user to validate the action
# fully contained in the first APDU before answering to it.
# Therefore we can't use the simple check_transaction() helper nor the
# send_async_sign_message() method and we need to do thing more manually.
def test_sign_transaction_newaccount_accepted(test_name, firmware, backend, navigator):
    signing_digest, message = load_transaction_from_file("transaction_newaccount.json")
    client = EosClient(backend)
    payload = pack_derivation_path(VAULTA_PATH) + message
    messages = split_message(payload, MAX_CHUNK_SIZE)
    assert len(messages) == 2

    if firmware.is_nano:
        instructions = get_nano_review_instructions(2) + get_nano_review_instructions(7)
    else:
        instructions = [NavInsID.USE_CASE_REVIEW_TAP] * 5
    with client.send_async_sign_message_full(messages[0], True):
        navigator.navigate_and_compare(ROOT_SCREENSHOT_PATH,
                                       test_name + "/part1",
                                       instructions)

    if firmware.is_nano:
        instructions = get_nano_review_instructions(6) + get_nano_review_instructions(8)
    else:
        if firmware == Firmware.FLEX:
            instructions = [NavInsID.USE_CASE_REVIEW_TAP] * 6
        else:
            instructions = [NavInsID.USE_CASE_REVIEW_TAP] * 5
        instructions.append(NavInsID.USE_CASE_REVIEW_CONFIRM)
        instructions.append(NavInsID.USE_CASE_STATUS_DISMISS)
    with client.send_async_sign_message_full(messages[1], False):
        navigator.navigate_and_compare(ROOT_SCREENSHOT_PATH,
                                       test_name + "/part2",
                                       instructions)
    response = client.get_async_response().data
    client.verify_signature(VAULTA_PATH, signing_digest, response)


# This transaction contains multiples actions which doesn't fit in one APDU.
# Therefore the app implementation ask the user to validate the action
# fully contained in the first APDU before answering to it.
# Therefore we can't use the simple send_async_sign_message() method and we
# need to do thing more manually.
@pytest.mark.parametrize("subdir, transaction_filename", unknown_trans)
def test_sign_transaction_unknown_fail(test_name,
                                    firmware,
                                    backend,
                                    navigator,
                                    subdir,
                                    transaction_filename):

    folder_name = test_name + "/" + transaction_filename.replace(".json", "")
    if subdir:
        folder_name = test_name + "/" + subdir + "/" + transaction_filename.replace(".json", "")
    _, message = load_transaction_from_file(transaction_filename, subdir)
    client = EosClient(backend)
    payload = pack_derivation_path(VAULTA_PATH) + message
    messages = split_message(payload, MAX_CHUNK_SIZE)

    if firmware.device.startswith("nano"):
        instructions = get_nano_review_instructions(2)
    else:
        instructions = [NavInsID.USE_CASE_REVIEW_TAP]
    with client.send_async_sign_message_full(messages[0], True):
        backend.raise_policy = RaisePolicy.RAISE_NOTHING
        navigator.navigate_and_compare(ROOT_SCREENSHOT_PATH,
                                       folder_name,
                                       instructions)
    rapdu = client.get_async_response()
    assert rapdu.status == 0x6A80
