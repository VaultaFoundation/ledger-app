/*****************************************************************************
 *   Ledger App EOS.
 *   (c) 2022 Ledger SAS.
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *****************************************************************************/

#ifdef HAVE_BAGL

#include <string.h>

#include "os.h"
#include "ux.h"

#include "glyphs.h"
#include "main.h"
#include "ui.h"
#include "config.h"

static char actionCounter[32];
static char confirmLabel[32];
static char smallConfirmLabel[16];

// display stepped screens
static unsigned int ux_step;
static unsigned int ux_step_count;

static char confirm_text1[16];
static char confirm_text2[16];

static void display_settings_flow(void);
static void switch_settings_contract_data(void);
static void switch_settings_verbose_config(void);
static void display_next_state(uint8_t state);

static void maybe_push_stack(void);

///////////////////////////COMMON FUNCTIONS////////////////////////////
static void maybe_push_stack(void) {
    // reserve a display stack slot if none yet
    if (G_ux.stack_count == 0) {
        ux_stack_push();
    }
}
////////////////////////////////////////////////////////////////////////////////
// Define a UX step with a user callback that runs when the step is shown
UX_STEP_NOCB(ux_status_flow_1_step,
             pbb,
             {
                 &C_icon_validate_14,
                 confirm_text1,
                 confirm_text2,
             });
UX_STEP_CB(ux_ack_flow_1_step,
           pbb,
           user_action_sign_flow_ok(),
           {
               &C_icon_validate_14,
               confirm_text1,
               confirm_text2,
           });
///////////////////////////////////////////////////////////////////////////////

UX_STEP_NOCB(ux_idle_ready_step,
             nn,  // pnn,
             {
                 "Application",
                 "is ready",
             });
UX_STEP_NOCB(ux_display_version_step,
             bn,
             {
                 "Version",
                 APPVERSION,
             });
UX_STEP_CB(ux_settings_step,
           pb,
           display_settings_flow(),
           {
               &C_icon_coggle,
               "Settings",
           });
UX_STEP_CB(ux_quit_step,
           pb,
           os_sched_exit(-1),
           {
               &C_icon_dashboard_x,
               "Quit",
           });

UX_FLOW(ux_idle_flow,
        &ux_idle_ready_step,
        &ux_display_version_step,
        &ux_settings_step,
        &ux_quit_step);

void ui_idle(void) {
    // reserve a display stack slot if none yet
    maybe_push_stack();

    ux_flow_init(0, ux_idle_flow, NULL);
}

////////////////////////////////////////////////////////////////////////////////

UX_STEP_NOCB(ux_abort_warning_step,
             bnn,  // pnn,
             {"Aborting", "Detected", "Unknown Trx"});

UX_FLOW(ux_abort_flow,
        &ux_abort_warning_step,
        &ux_display_version_step,
        &ux_display_version_step,
        &ux_quit_step);

void ui_abort_unknown_action(void) {
    // reserve a display stack slot if none yet
    maybe_push_stack();

    ux_flow_init(0, ux_abort_flow, NULL);
}

///////////////////////////////////////////////////////////////////////////////

UX_STEP_CB(ux_settings_flow_1_step,
           bnnn,
           switch_settings_contract_data(),
           {
               "Contract data",
               "Unknown Action",
               "in transactions",
               confirmLabel,
           });

UX_STEP_CB(ux_settings_flow_2_step,
           bnnn,
           switch_settings_verbose_config(),
           {
               "Verbose",
               "Show Details",
               "in transactions",
               smallConfirmLabel,
           });

UX_STEP_CB(ux_settings_flow_3_step,
           pb,
           ui_idle(),
           {
               &C_icon_back_x,
               "Back",
           });

UX_FLOW(ux_settings_flow,
        &ux_settings_flow_1_step,
        &ux_settings_flow_2_step,
        &ux_settings_flow_3_step);

static void display_settings_flow(void) {
    strlcpy(confirmLabel,
            (is_unknown_action_allowed() ? "Allowed" : "NOT Allowed"),
            sizeof(confirmLabel));

    strlcpy(smallConfirmLabel, (is_verbose() ? "On" : "Off"), sizeof(smallConfirmLabel));

    ux_flow_init(0, ux_settings_flow, NULL);
}

static void switch_settings_contract_data(void) {
    toogle_unknown_action_allowed();
    display_settings_flow();
}

static void switch_settings_verbose_config(void) {
    toogle_verbose_config();
    display_settings_flow();
}

///////////////////////////////////////////////////////////////////////////////

UX_STEP_NOCB(ux_display_public_flow_1_step,
             pnn,
             {
                 &C_icon_eye,
                 "Verify",
                 "Public Key",
             });
UX_STEP_NOCB(ux_display_public_flow_2_step,
             bnnn_paging,
             {
                 .title = "Public Key",
                 .text = tmpCtx.publicKeyContext.address,
             });
UX_STEP_CB(ux_display_public_flow_3_step,
           pb,
           user_action_address_ok(),
           {
               &C_icon_validate_14,
               "Approve",
           });
UX_STEP_CB(ux_display_public_flow_4_step,
           pb,
           user_action_address_cancel(),
           {
               &C_icon_crossmark,
               "Reject",
           });

UX_FLOW(ux_display_public_flow,
        &ux_display_public_flow_1_step,
        &ux_display_public_flow_2_step,
        &ux_display_public_flow_3_step,
        &ux_display_public_flow_4_step);

void ui_display_public_key_flow(void) {
    ux_flow_init(0, ux_display_public_flow, NULL);
}

void ui_display_public_key_done(bool validated) {
    UNUSED(validated);
    // Display back the original UX
    ui_idle();
}

///////////////////////////////////////////////////////////////////////////////

#define STATE_LEFT_BORDER  0
#define STATE_VARIABLE     1
#define STATE_RIGHT_BORDER 2

UX_STEP_NOCB(ux_single_action_sign_flow_1_step,
             pnn,
             {
                 &C_icon_certificate,
                 "Review",
                 confirmLabel,
             });
UX_STEP_NOCB(ux_single_action_sign_flow_2_step,
             bn,
             {
                 "Contract",
                 txContent.contract,
             });
UX_STEP_NOCB(ux_single_action_sign_flow_3_step,
             bn,
             {
                 "Action",
                 txContent.action,
             });
UX_STEP_INIT(ux_init_left_border, NULL, NULL, { display_next_state(STATE_LEFT_BORDER); });

UX_STEP_NOCB_INIT(ux_single_action_sign_flow_variable_step,
                  bnnn_paging,
                  { display_next_state(STATE_VARIABLE); },
                  {
                      .title = txContent.arg.label,
                      .text = txContent.arg.data,
                  });

UX_STEP_INIT(ux_init_right_border, NULL, NULL, { display_next_state(STATE_RIGHT_BORDER); });

UX_STEP_CB(ux_single_action_sign_flow_7_step,
           pbb,
           user_action_sign_flow_ok(),
           {
               &C_icon_validate_14,
               confirm_text1,
               confirm_text2,
           });
UX_STEP_CB(ux_single_action_sign_flow_8_step,
           pbb,
           user_action_tx_cancel(),
           {
               &C_icon_crossmark,
               "Cancel",
               "signature",
           });

UX_FLOW(ux_single_action_sign_flow,
        &ux_single_action_sign_flow_1_step,
        &ux_single_action_sign_flow_2_step,
        &ux_single_action_sign_flow_3_step,
        &ux_init_left_border,
        &ux_single_action_sign_flow_variable_step,
        &ux_init_right_border,
        &ux_single_action_sign_flow_7_step,
        &ux_single_action_sign_flow_8_step);

static void display_next_state(uint8_t state) {
    if (state == STATE_LEFT_BORDER) {
        if (ux_step == 0) {
            ux_step = 1;
            ux_flow_next();
        } else if (ux_step == 1) {
            --ux_step;
            ux_flow_prev();
        } else if (ux_step > 1) {
            --ux_step;
            ux_flow_next();
        }
    } else if (state == STATE_VARIABLE) {
        printArgument(ux_step - 1, &txProcessingCtx);
    } else if (state == STATE_RIGHT_BORDER) {
        if (ux_step < ux_step_count) {
            ++ux_step;
            ux_flow_prev();
        } else if (ux_step == ux_step_count) {
            ++ux_step;
            ux_flow_next();
        } else if (ux_step > ux_step_count) {
            ux_step = ux_step_count;
            ux_flow_prev();
        }
    }
}

void ui_display_single_action_sign_flow(void) {
    ux_step = 0;
    ux_step_count = txContent.argumentCount;

    if (txProcessingCtx.currentActionNumber > 1) {
        snprintf(confirmLabel,
                 sizeof(confirmLabel),
                 "Action #%d",
                 txProcessingCtx.currentActionIndex);
    } else {
        strlcpy(confirmLabel, "Transaction", sizeof(confirmLabel));
    }

    if (txProcessingCtx.currentActionIndex == txProcessingCtx.currentActionNumber) {
        strlcpy(confirm_text1, "Sign", sizeof(confirm_text1));
        strlcpy(confirm_text2, "transaction", sizeof(confirm_text2));
    } else {
        strlcpy(confirm_text1, "Accept", sizeof(confirm_text1));
        strlcpy(confirm_text2, "& review next", sizeof(confirm_text2));
    }

    ux_flow_init(0, ux_single_action_sign_flow, NULL);
}

void ui_display_action_sign_done(parserStatus_e status, bool validated) {
    UNUSED(status);
    UNUSED(validated);
    // Display back the original UX
    ui_idle();
}

///////////////////////////////////////////////////////////////////////////////
// Define flow steps array (rename to avoid clash with function name)
UX_FLOW(ux_display_blind_sign_flow_steps, &ux_ack_flow_1_step);

void ui_display_blind_sign_flow(void) {
    unsigned int wr1 = snprintf(confirm_text1, sizeof(confirm_text1), "%s", txContent.contract);
    unsigned int wr2 = snprintf(confirm_text2, sizeof(confirm_text2), "%s", txContent.action);

    if (wr1 >= sizeof(confirm_text1) || wr1 < 0 || wr2 >= sizeof(confirm_text2) || wr2 < 0) {
        ui_abort_unknown_action();
    } else {
        ux_flow_init(0, ux_display_blind_sign_flow_steps, NULL);
        // ui_idle();
    }
}

///////////////////////////////////////////////////////////////////////////////

UX_FLOW_DEF_NOCB(ux_multiple_action_sign_flow_1_step,
                 pnn,
                 {
                     &C_icon_certificate,
                     "Review",
                     "Transaction",
                 });
UX_FLOW_DEF_NOCB(ux_multiple_action_sign_flow_2_step,
                 bn,  // pnn,
                 {
                     "With",
                     actionCounter,
                 });
UX_FLOW_DEF_VALID(ux_multiple_action_sign_flow_3_step,
                  pbb,
                  user_action_sign_flow_ok(),
                  {&C_icon_validate_14, "Continue", "review"});
UX_FLOW_DEF_VALID(ux_multiple_action_sign_flow_4_step,
                  pbb,
                  user_action_tx_cancel(),
                  {
                      &C_icon_crossmark,
                      "Cancel",
                      "review",
                  });

UX_FLOW(ux_multiple_action_sign_flow,
        &ux_multiple_action_sign_flow_1_step,
        &ux_multiple_action_sign_flow_2_step,
        &ux_multiple_action_sign_flow_3_step,
        &ux_multiple_action_sign_flow_4_step);

void ui_display_multiple_action_sign_flow(void) {
    snprintf(actionCounter,
             sizeof(actionCounter),
             "%d actions",
             txProcessingCtx.currentActionNumber);
    ux_flow_init(0, ux_multiple_action_sign_flow, NULL);
}

#endif
