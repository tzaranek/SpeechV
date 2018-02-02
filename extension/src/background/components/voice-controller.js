// TODO: receive commands from an external application
// TODO: force execution of commands in sequential order
// TODO: allow commands to be cancelled

import * as messages from 'shared/messages';

class VoiceController {
  constructor() {
    console.log("This should only print once")
    setTimeout(this.onVoiceCommand.bind(this), 3000);

    // TODO: listen to native application. bind to onVoiceCommand
  }

  onVoiceCommand(command) {
    // TODO: communicate with native application
    // TODO: add failure callbacks for promise chains

    // proof of concept
    command = [{
      key: 'f',
      repeat: false,
      shiftKey: false,
      ctrlKey: false,
      altKey: false,
      metaKey: false
    },
    {
      key: 'b',
      repeat: false,
      shiftKey: false,
      ctrlKey: false,
      altKey: false,
      metaKey: false
    }];

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

