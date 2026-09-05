/* Generated catalogue HTML remains usable without JavaScript. */
(function () {
  const books = JSON.parse(document.getElementById("books-data").textContent);
      const grid = document.getElementById("series-grid");
      const modal = document.getElementById("series-modal");
      const modalBody = document.getElementById("series-modal-body");
      const modalCover = document.getElementById("series-modal-cover");
      const modalShell = modal.querySelector(".modal-shell");
      const modalClose = modal.querySelector(".modal-close");
      let modalTrigger = null;
      let previousOverflow = null;
      const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#39;"
      }[char]));
      const plainTitle = (book) => book.title.replace(/\s+/g, " ");

      if (typeof modal.showModal !== "function") return;
      grid.querySelectorAll(".book-card-trigger").forEach((button) => { button.hidden = false; });

      const openModal = (bookIndex, trigger) => {
        if (modal.open) return;
        const book = books[bookIndex];
        modalCover.innerHTML = `
          <img src="${book.cover}" alt="《${escapeHtml(plainTitle(book))}》封面" />
        `;
        modalBody.innerHTML = `
          <span class="page-kicker">Book Detail</span>
          <h3 id="series-modal-title">${escapeHtml(book.title)}</h3>
          <p class="modal-book-meta">${escapeHtml(book.author)} ${book.creatorRole === "editor" ? "编" : "著"} / ${escapeHtml(book.translator)} 译</p>
          <p>${escapeHtml(book.description)}</p>
          <p><a class="cta-button" href="./${book.id}/index.html">打开独立详情页 →</a></p>
          <div class="fact-list">
            <div class="fact-item"><span>出版时间</span><span>${book.published}</span></div>
            <div class="fact-item"><span>${book.creatorRole === "editor" ? "编者" : "作者"}</span><span>${escapeHtml(book.author)}</span></div>
            <div class="fact-item"><span>译者</span><span>${escapeHtml(book.translator)}</span></div>
            <div class="fact-item"><span>出版社</span><span>${escapeHtml(book.publisher)}</span></div>
          </div>
        `;
        modalTrigger = trigger;
        previousOverflow = {
          root: document.documentElement.style.overflow,
          body: document.body.style.overflow
        };
        document.documentElement.style.overflow = "hidden";
        document.body.style.overflow = "hidden";
        modal.classList.add("is-open");
        // Native modal dialogs make the rest of the document inert.
        modal.showModal();
        modalShell.scrollTop = 0;
        modalClose.focus({ preventScroll: true });
      };

      grid.addEventListener("click", (event) => {
        const trigger = event.target.closest(".book-card-trigger");
        if (!trigger) return;
        const card = trigger.closest(".book-card");
        const bookIndex = books.findIndex((item) => item.id === card.dataset.bookId);
        if (bookIndex >= 0) openModal(bookIndex, trigger);
      });

      const closeModal = () => {
        if (modal.open) modal.close();
      };

      modal.addEventListener("click", (event) => {
        if (event.target === modal || event.target.closest(".modal-close")) {
          closeModal();
        }
      });

      modal.addEventListener("keydown", (event) => {
        if (event.target === modalShell) {
          const readingKeys = {
            Home: 0,
            End: modalShell.scrollHeight,
            PageDown: modalShell.scrollTop + modalShell.clientHeight * 0.9,
            PageUp: modalShell.scrollTop - modalShell.clientHeight * 0.9,
            ArrowDown: modalShell.scrollTop + 40,
            ArrowUp: modalShell.scrollTop - 40
          };
          if (Object.prototype.hasOwnProperty.call(readingKeys, event.key)) {
            event.preventDefault();
            event.stopPropagation();
            modalShell.scrollTop = readingKeys[event.key];
            return;
          }
        }
        if (event.key === "Escape") {
          event.preventDefault();
          event.stopPropagation();
          closeModal();
        } else if (event.key === "Tab") {
          // The close button, reading area and permanent-detail link stay reachable.
          const focusables = Array.from(modal.querySelectorAll("button:not([disabled]), .modal-shell, a[href]"));
          const first = focusables[0];
          const last = focusables[focusables.length - 1];
          if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus({ preventScroll: true });
          } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus({ preventScroll: true });
          }
          event.stopPropagation();
        }
      });

      modal.addEventListener("cancel", (event) => {
        event.preventDefault();
        closeModal();
      });

      modal.addEventListener("close", () => {
        modal.classList.remove("is-open");
        if (previousOverflow) {
          document.documentElement.style.overflow = previousOverflow.root;
          document.body.style.overflow = previousOverflow.body;
          previousOverflow = null;
        }
        if (modalTrigger && modalTrigger.isConnected) {
          modalTrigger.focus({ preventScroll: true });
        }
        modalTrigger = null;
      });

})();
