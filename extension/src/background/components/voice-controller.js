// TODO: allow commands to be cancelled
// TODO: add configuration options for letters used in hints
// TODO: comprehensively error handle

import * as messages from 'shared/messages';

class VoiceController {
  constructor() {
    let port = browser.runtime.connectNative("speechV.py")
    port.onDisconnect.addListener((p) => {
      if (p.error) {
        console.log("disconnected. error:")
        console.log(p.error.message)
      } else {
        console.log("disconnected");
      }
    })
    port.onMessage.addListener(this.exeVoiceCommand.bind(this));
  }

  // TODO: add failure callbacks for promise chains
  exeVoiceCommand(command) {
    console.log("Received command:")
    console.log(command)

    // send to the active tab in the focused window i.e. the focused tab
    browser.tabs.query({ currentWindow: true, active: true }).then((focusedTabs) => {
      if (focusedTabs.length > 1) {
        console.warn(`impossible: more than one focused tab: ${focusedTabs.length}`);
        return;
      } else if (focusedTabs.length === 0 || !focusedTabs[0].active) {
        // TODO: maybe throw an error back to the native application
        return;
      }
      let focusedTab = focusedTabs[0];

      let keystroke_chain = new Promise((resolve, reject) => {
        resolve();
      });

      // send each keystroke separately to simulate how keystrokes are actually sent
      for (let keystroke of command) {
        let message = {
          type: messages.SPEECHV_VIRTUAL_KEYSTROKE,
          keystroke: keystroke
        };
        keystroke_chain = keystroke_chain.then(() => {
          return new Promise((resolve, reject) => {
            console.log("chain:")
            console.log(keystroke)

            browser.tabs.sendMessage(focusedTab.id, message).then((response) => {
              console.log("Voice keystroke response:");
              console.log(response);
              resolve()
            })
          });
        }).then(() => {
          // rate limit keystrokes so that Vim Vixen can update all the
          // state it needs before processing the next one
          // in normal usage, rate limiting is unneeded but it's essential
          // for testing because inputs are issued without delay
          return new Promise((resolve, reject) => {
            setTimeout(resolve, 100);
          });
        });
      }
    });
  }
}
console.log("VOICE CONTROLLER MODULE LOADED");

// use singleton pattern
export let voiceController = new VoiceController();

