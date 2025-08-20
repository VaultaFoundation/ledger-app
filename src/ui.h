#pragma once

void ui_idle(void);
void ui_abort_unknown_action(void);
void ui_display_public_key_flow(void);
void ui_display_public_key_done(bool validated);
void ui_display_single_action_sign_flow(void);
void ui_display_multiple_action_sign_flow(void);
void ui_display_action_sign_done(parserStatus_e status, bool validated);

// No-op with no data — does not modify chain state.
// argumentCount is checked out of an abundance of caution.
// The presence of arguments is unexpected, so we require full transaction review in that case.
static inline bool isStateNeutralAction(const char *contract, const char *action, uint8_t noData) {
    char contract_lower[64] = {0};
    size_t i = 0;
    for (; i < sizeof(contract_lower) - 1 && contract[i] != '\0'; i++) {
        char c = contract[i];
        if (c >= 'A' && c <= 'Z') {
            contract_lower[i] = c + ('a' - 'A');
        } else {
            contract_lower[i] = c;
        }
    }
    contract_lower[i] = '\0';
    return (strcmp(contract_lower, "null.vaulta") == 0 && strcmp(action, "noop") == 0 &&
            noData == 1);
}