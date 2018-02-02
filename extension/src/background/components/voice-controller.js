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
    }];

    let message = {
      type: messages.SPEECHV_VIRTUAL_KEYSTROKES,
      command: command
    }

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
      browser.tabs.sendMessage(focusedTab.id, message).then((response) => {
        console.log("Voice command response:");
        console.log(response);
      });
    });
  }
}
console.log("VOICE CONTROLLER MODULE LOADED");

// use singleton pattern
export let voiceController = new VoiceController();

