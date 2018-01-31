let instance = null;
export default class VoiceController {
  constructor(inputComponent) {
    // use singleton pattern
    if (!instance) {
      instance = this;
      instance.inputComponents = [];

      // FIXME: this is 
      console.log("This should only print once")

      // for proof of concept 
      setTimeout(this.exeCommand.bind(instance), 3000);
    }

    // remember where to forward keystrokes
    instance.inputComponents.push(inputComponent)
    return instance;
  }

  exeCommand(command) {
    // FIXME: allow arbitrary commands
    // FIXME: only execute commands in the active tab
    console.log("Hello from exeCommand")
    command = [
      {
        key: 'f',
        repeat: false,
        shiftKey: false,
        ctrlKey: false,
        altKey: false,
        metaKey: false
      }
    ]

    for (let keystroke of command) {
      console.log('Forwarding keystroke')
      console.log(keystroke)

      // Talk to input components until one processes our keystroke. Sending
      // to all of them may double execute the keystroke
      for (let comp of instance.inputComponents) {
        if (comp.broadcast(keystroke)) {
          break;
        }
      }
    }
  }
}

