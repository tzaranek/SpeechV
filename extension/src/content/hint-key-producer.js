class AllKeyProducer {
  constructor(charset) {
    if (charset.length === 0) {
      throw new TypeError('charset is empty');
    }

    this.charset = charset;
    this.counter = [];
  }

  produce() {
    this.increment();

    return this.counter.map(x => this.charset[x]).join('');
  }

  increment() {
    let max = this.charset.length - 1;
    if (this.counter.every(x => x === max)) {
      this.counter = new Array(this.counter.length + 1).fill(0);
      return;
    }

    this.counter.reverse();
    let len = this.charset.length;
    let num = this.counter.reduce((x, y, index) => x + y * len ** index) + 1;
    for (let i = 0; i < this.counter.length; ++i) {
      this.counter[i] = num % len;
      num = ~~(num / len);
    }
    this.counter.reverse();
  }
}

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
    let gen = new AllKeyProducer(this.charset);
    while (tree.leaves < count) {
      let nextSeq = gen.produce();
      tree.addHint(nextSeq);
    }
    return tree.getLeaves();
  }
}
