#pragma once

#include <string.h>
#include <stddef.h>
#include <stdbool.h>

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