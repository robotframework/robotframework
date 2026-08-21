function createModal(closeLabel: string = "Close") {
  const modalBackground = document.createElement("div");
  modalBackground.id = "modal-background";
  modalBackground.classList.add("modal-background");
  modalBackground.addEventListener("click", ({ target }) => {
    if ((target as HTMLElement)?.id === "modal-background") hideModal();
  });

  const modalCloseButton = document.createElement("button");
  modalCloseButton.innerHTML =
    '<svg aria-hidden="true"><use href="#icon-close"></use></svg>';
  modalCloseButton.classList.add("modal-close-button");
  // The button holds nothing but an icon, so it needs a name of its own.
  modalCloseButton.setAttribute("aria-label", closeLabel);
  modalCloseButton.setAttribute("type", "button");
  const modalCloseButtonContainer = document.createElement("div");
  modalCloseButtonContainer.classList.add("modal-close-button-container");
  modalCloseButtonContainer.appendChild(modalCloseButton);
  modalCloseButton.addEventListener("click", () => {
    hideModal();
  });
  // The close button sits above the dialog and has to end where the dialog
  // ends, so both take their width from a shared frame.
  const modalFrame = document.createElement("div");
  modalFrame.classList.add("modal-frame");
  modalFrame.appendChild(modalCloseButtonContainer);
  modalBackground.appendChild(modalFrame);
  modalCloseButtonContainer.addEventListener("click", () => {
    hideModal();
  });

  const modal = document.createElement("div");
  modal.id = "modal";
  modal.classList.add("modal");
  modal.addEventListener("click", ({ target }) => {
    if ((target as HTMLElement).tagName.toUpperCase() === "A") hideModal();
  });

  const modalContent = document.createElement("div");
  modalContent.id = "modal-content";
  modalContent.classList.add("modal-content");
  modal.appendChild(modalContent);

  modalFrame.appendChild(modal);
  document.body.appendChild(modalBackground);
  document.addEventListener("keydown", ({ key }) => {
    if (key === "Escape") hideModal();
  });
}
function showModal(content) {
  const modalBackground = document.getElementById("modal-background")!;
  const modal = document.getElementById("modal")!;
  const modalContent = document.getElementById("modal-content")!;
  modalBackground.classList.add("visible");
  modal.classList.add("visible");
  modalContent.appendChild(content.cloneNode(true));
  document.body.style.overflow = "hidden";
}

function hideModal() {
  const modalBackground = document.getElementById("modal-background")!;
  const modal = document.getElementById("modal")!;
  const modalContent = document.getElementById("modal-content")!;

  modalBackground.classList.remove("visible");
  modal.classList.remove("visible");
  document.body.style.overflow = "auto";
  if (window.location.hash.indexOf("#type-") == 0)
    history.pushState("", document.title, window.location.pathname);
  // modal is hidden with a fading transition, timeout prevents premature emptying of modal
  setTimeout(() => {
    modalContent.innerHTML = "";
  }, 200);
}

export { createModal, showModal, hideModal };
