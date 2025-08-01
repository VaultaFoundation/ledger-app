from json import load

from speculos_lib.backend import SpeculosBackend
from ragger.bip import pack_derivation_path
from ragger.utils import split_message
from test_app_mainmenu_settings_cfg import run_app_mainmenu_settings_cfg
from test_sign_cmd import get_nano_review_instructions, load_transaction_from_file

from apps.eos import EosClient, STATUS_OK, MAX_CHUNK_SIZE
from apps.eos_transaction_builder import Transaction
from utils import ROOT_SCREENSHOT_PATH, CORPUS_DIR
# Proposed EOS derivation paths for tests ###
VAULTA_PATH = "m/44'/194'/12345'"

transaction_filename='mixed_transaction_noop_with_data_trans.json'
contract='null.vaulta'
_, message = load_transaction_from_file(transaction_filename,contract)
with SpeculosBackend(app_path="/app/build/stax/bin/app.elf") as backend:
    client = EosClient(backend)
    payload = pack_derivation_path(VAULTA_PATH) + message
    messages = split_message(payload, MAX_CHUNK_SIZE)
    client.send_async_sign_message_full(messages[0], True)