
const showBookmarks = (win, bs) => {
  let doc = win.document;
  let list = doc.createElement("ul");

  bs.forEach((b) => {
    let link = doc.createElement("a");
    link.href = b.url;
    link.textContent = b.title;

    let el = doc.createElement("li");
    el.appendChild(link);
    list.appendChild(el);
  });

  console.log(doc);
  doc.body.append(list);
};

export {
  appendBookmarksToPage
};

