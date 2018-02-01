// TODO: Fix singleton bug: iframes appear to load content.js independent of main process
// TODO: receive commands from an external application
// TODO: force execution of commands in sequential order
// TODO: only execute commands in active tab
// TODO: allow commands to be cancelled

class VoiceController {
  constructor() {
    console.log("This should only print once")

    // for proof of concept 
    setTimeout(this.exeCommand.bind(this), 3000);

    // remember where to forward keystrokes
    this.inputComponents = [];
  }

  addInputComponent(comp) {
    console.log("Hello from addInputComp")
    this.inputComponents.push(comp);
  }

  exeCommand(command) {
    console.log("Hello from exeCommand")
    command = [{
      key: 'f',
      repeat: false,
      shiftKey: false,
      ctrlKey: false,
      altKey: false,
      metaKey: false
    }];

    for (let keystroke of command) {
      console.log('Forwarding keystroke')
      console.log(keystroke)
      console.log(`len of inputComponents: ${this.inputComponents.length}`)

      // Talk to input components until one processes our keystroke. Sending
      // to all of them may double execute the keystroke
      for (let comp of this.inputComponents) {
        if (comp.broadcast(keystroke)) {
          break;
        }
      }
    }
  }
}

console.log("VOICE CONTROLLER MODULE LOADED");
// console.log(`window id = ${window.top}`);
console.log(window)
console.log(window.parent)
console.log(window.top === window)

setTimeout(() => {
  console.log("Frames");
  for (let i = 0; i < window.frames.length; i++) {
    console.log(window.frames[i]);
  }
}, 1000);
console.log("passed window log");
// console.log(`window.top.get().windowID = ${browser.window.top.get().windowID}`)

// use singleton pattern
export let voiceController = new VoiceController();

