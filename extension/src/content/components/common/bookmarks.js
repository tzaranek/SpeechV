
const showBookmarks = (win, bs) => {
  let doc = win.document;
  let list = doc.createElement("ul");

  bs.forEach((b) => {
    let link = doc.createElement("a");
    link.href = b.url;
    link.textContent = b.title;

    let el = doc.createElement("li");
    el.type = "circle";
    el.appendChild(link);
    list.appendChild(el);
  });

  let wrapper = doc.createElement("div");
  wrapper.id = "centered-list";
  wrapper.appendChild(list);

  doc.body.append(wrapper);
};

export {
  showBookmarks
};

