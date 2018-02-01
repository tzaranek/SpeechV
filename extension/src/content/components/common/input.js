import * as dom from 'shared/utils/dom';
import * as keys from 'shared/utils/keys';
import { voiceController } from './voice-controller';

const ENABLE_KEYBOARD = true;

export default class InputComponent {
  constructor(target) {
    this.pressed = {};
    this.onKeyListeners = [];

    if (ENABLE_KEYBOARD) {
      target.addEventListener('keypress', this.onKeyPress.bind(this));
      target.addEventListener('keydown', this.onKeyDown.bind(this));
      target.addEventListener('keyup', this.onKeyUp.bind(this));
    }

    // Connect SpeechV with Vim Vixen
    voiceController.addInputComponent(this);
  }

  /*
   * Broadcast a keystroke to vim-vixen. Returns true if a
   * listener processes the keystroke. Keystrokes are of the form: 
   * 
   * {
   *   key: modifierdKeyName(e.key),                                                  
   *   repeat: e.repeat,                                                              
   *   shiftKey: shift,                                                               
   *   ctrlKey: e.ctrlKey,                                                            
   *   altKey: e.altKey,                                                              
   *   metaKey: e.metaKey,                                                            
   * }
   * 
   * See src/shared/utils/keys.js for more info
   */
  broadcast(keystroke) {
    console.log("Broadcasting keystroke")
    console.log(keystroke)

    // Talk to listeners until one processes our keystroke
    for (let listener of this.onKeyListeners) {
      if (listener(keystroke)) {
        return true;
      }
    }
    return false;
  }


  onKey(cb) {
    this.onKeyListeners.push(cb);
  }

  onKeyPress(e) {
    if (this.pressed[e.key] && this.pressed[e.key] !== 'keypress') {
      return;
    }
    this.pressed[e.key] = 'keypress';
    this.capture(e);
  }

  onKeyDown(e) {
    if (this.pressed[e.key] && this.pressed[e.key] !== 'keydown') {
      return;
    }
    this.pressed[e.key] = 'keydown';
    this.capture(e);
  }

  onKeyUp(e) {
    delete this.pressed[e.key];
  }

  capture(e) {
    if (this.fromInput(e)) {
      if (e.key === 'Escape' && e.target.blur) {
        e.target.blur();
      }
      return;
    }
    if (['Shift', 'Control', 'Alt', 'OS'].includes(e.key)) {
      // pressing only meta key is ignored
      return;
    }

    let key = keys.fromKeyboardEvent(e);

    for (let listener of this.onKeyListeners) {
      let stop = listener(key);
      if (stop) {
        e.preventDefault();
        e.stopPropagation();
        break;
      }
    }
  }

  fromInput(e) {
    if (!e.target) {
      return false;
    }
    return e.target instanceof HTMLInputElement ||
      e.target instanceof HTMLTextAreaElement ||
      e.target instanceof HTMLSelectElement ||
      dom.isContentEditable(e.target);
  }
}
