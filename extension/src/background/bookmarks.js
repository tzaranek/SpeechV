import operations from 'shared/operations'

const createBookmarkFromCurrent = () => {
  return browser.tabs.query({
      currentWindow: true,
      active: true
    }).then((focusedTabs) => {
      if (focusedTabs.len > 1) {
        console.error("Firefox seems to have broken...");
        return;
      } else if (focusedTabs.len === 0) {
        console.log("No open tabs");
        // TODO: indicate to user something is bad...
        return;
      }

      let title = focusedTabs[0].title;
      let url = focusedTabs[0].url;

      return { "title": title, "url": url };
    }).then(browser.bookmarks.create)
      .then(
        (b) => console.log("Created bookmark: ${b}"),
        (e) => console.log("Error: ${e}")
      );
};

const retrieveBookmarks = () => {
  console.log("RETRIEVING");
  return browser.bookmarks.search({}).then((bs) => {
      console.log("INSIDE THE THEN");
      let user_bs = bs.filter(x => x.parentId === "unfiled_____");
      browser.runtime.sendMessage({
        type: operations.BOOKMARKS_SHOW,
        keys: user_bs
      });
    });
};

export {
  createBookmarkFromCurrent, retrieveBookmarks
};

