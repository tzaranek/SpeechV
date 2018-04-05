import { expect } from "chai";
import HintKeyProducer from 'content/hint-key-producer';

describe('HintKeyProducer class', () => {
  describe('#constructor', () => {
    it('throws an exception on empty charset', () => {
      expect(() => new HintKeyProducer([])).to.throw(TypeError);
    });
  });

  describe('#produce', () => {
    it('produce incremented keys', () => {
      let charset = 'abc';
      let sequences = [
          "aaa", "aab",
          "ab", "ac",
          "ba", "bb", "bc",
          "ca", "cb", "cc"]

      let producer = new HintKeyProducer(charset);
      let produced = producer.produce(sequences.length);
      for (let i = 0; i < sequences.length; ++i) {
        expect(produced[i]).to.equal(sequences[i]);
      }
    });
  });
});
