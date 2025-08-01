import pytest

from ledgered.devices import Device
from ragger.backend import BackendInterface
from ragger.navigator.navigation_scenario import NavigateWithScenario

from test_app_mainmenu_settings_cfg import run_app_mainmenu_settings_cfg
from test_sign_cmd import run_sign_transaction
from test_unknown_transactions import process_transaction_with_mixed_actions

from utils import NULL_VAULTA_CORPUS_FILES


mixed_actions = []
single_actions = []

for tag, filename in NULL_VAULTA_CORPUS_FILES:
    if filename.startswith("mixed_"):
        mixed_actions.append((tag, filename))
    else:
        single_actions.append((tag, filename))

@pytest.mark.parametrize("subdir, transaction_filename", single_actions)
def test_noop_transactions_with_verbose(test_name: str,
                                   device: Device,
                                   backend: BackendInterface,
                                   scenario_navigator: NavigateWithScenario,
                                   subdir: str,
                                   transaction_filename: str):

    # set verbose on
    run_app_mainmenu_settings_cfg(device, backend, scenario_navigator.navigator)
    run_sign_transaction(test_name,device,backend,scenario_navigator,subdir,transaction_filename)

@pytest.mark.parametrize("subdir, transaction_filename", [('null.vaulta', 'mixed_transaction_noop_with_data_trans.json'), ('null.vaulta', 'mixed_transaction_noop_trans.json')])
def test_noop_mixed_transactions_with_verbose(test_name: str,
                                   device: Device,
                                   backend: BackendInterface,
                                   scenario_navigator: NavigateWithScenario,
                                   subdir: str,
                                   transaction_filename: str):

    action_one_args = 1 # noop
    action_two_args = 4 # transfer 
    process_transaction_with_mixed_actions(test_name,device,backend,scenario_navigator,subdir,transaction_filename,action_one_args,action_two_args)
