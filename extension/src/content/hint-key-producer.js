const replaceAt = (str, index, replacement) => {
    return str.substr(0, index)
        + replacement
        + str.substr(index + replacement.length);
};

function* sequenceGenerator (charset) {
  if (charset.length === 0) {
    throw new TypeError('charset is empty');
  }

  let seq = "";
  let seqIdx = 0;
  while (true) {
    let curCharIdx = charset.indexOf(seq[seqIdx]);
    if (seqIdx !== -1 && curCharIdx === charset.length - 1) {
      seq = replaceAt(seq, seqIdx, charset[0]);
      seqIdx -= 1;
    } else {
      seq = seqIdx === -1
            ? charset[0] + seq
            : replaceAt(seq, seqIdx, charset[curCharIdx+1]);
      seqIdx = seq.length - 1;
      yield seq;
    }
  }
};

class HintTree {
  // each tree holds it's top-level nodes and pointers to subtrees

  constructor(value) {
    this.children = {};
    // this node itself is currently a leaf but for ease of counting, don't
    // count yourself as a leaf
    this.leaves = 0;
    this.value = value;
  }

  addHint(sequence) {
    let newLeafCount = 1;
    if (this.leaves === 0) {
      // parent's don't get any new leaves since the current node is a leaf and
      // we are just moving it's leafy status to its child. however, the node
      // itself must recognize for counting that it should increment it's
      // leaves since it is constructed to 0
      newLeafCount = 0;
      this.leaves = 1;
    }
    if (!(sequence[0] in this.children)) {
      this.children[sequence[0]] = new HintTree(sequence[0]);
    }
    if (sequence.length !== 1) {
      newLeafCount = this.children[sequence[0]].addHint(sequence.substring(1));
    }
    this.leaves += newLeafCount;
    return newLeafCount;
  }

  getLeaves() {
    let ret = this.leaves === 0 ? [this.value] : [];
    Object.keys(this.children).forEach((key) => {
      let subSeqs = this.children[key].getLeaves();
      subSeqs.forEach((s) => ret.push(this.value + s));
    });
    return ret;
  }
}

export default class HintKeyProducer {
  constructor(charset) {
    if (charset.length === 0) {
      throw new TypeError('charset is empty');
    }
    this.charset = charset;
  }

  produce(count) {
    let tree = new HintTree("");
    let gen = sequenceGenerator(this.charset);
    while (tree.leaves < count) {
      let nextSeq = gen.next();
      tree.addHint(nextSeq.value);
    }
    return tree.getLeaves();
  }
}
