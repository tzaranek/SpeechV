import * as dom from 'shared/utils/dom';
import * as keys from 'shared/utils/keys';
import * as messages from 'shared/messages';

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

    // listen for messages from the voice controller
    browser.runtime.onMessage.addListener(this.broadcastVirtualKeystroke.bind(this));
  }

  /*
   * Broadcast a voice command to vim-vixen. Keystrokes are of the form:
   * {
   *   key: char,
   *   repeat: bool,
   *   shiftKey: bool,
   *   ctrlKey: bool,
   *   altKey: bool,
   *   metaKey: bool
   * }
   */
  broadcastVirtualKeystroke(message, sender, sendResponse) {
    if (message.type !== messages.SPEECHV_VIRTUAL_KEYSTROKE) {
      return false; //FIXME: what should be returned?
    } else if (window !== window.top) {
      // ensure keystrokes are counted only once
      return false; //FIXME: what should be returned?
    }

    console.log("Broadcasting keystroke");
    console.log(message.keystroke);

    for (let listener of this.onKeyListeners) {
      // stop if they tell us to
      let stop = listener(message.keystroke);
      if (stop) {
        break;
      }
    }
    sendResponse()
    console.log("done broadcasting")
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
