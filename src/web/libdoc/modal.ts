function createModal() {
  const modalBackground = document.createElement("div");
  modalBackground.id = "modal-background";
  modalBackground.classList.add("modal-background");
  modalBackground.addEventListener("click", ({ target }) => {
    if ((target as HTMLElement)?.id === "modal-background") hideModal();
  });

  const modalCloseButton = document.createElement("button");
  modalCloseButton.innerHTML = `<svg xmlns="
    http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="2em" height="2em" className="block" data-v-2754030d="" data-v-512b0344="">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"
                  data-v-2754030d="" fill="var(--text-color)"></path></svg>`;
  modalCloseButton.classList.add("modal-close-button");
  const modalCloseButtonContainer = document.createElement("div");
  modalCloseButtonContainer.classList.add("modal-close-button-container");
  modalCloseButtonContainer.appendChild(modalCloseButton);
  modalCloseButton.addEventListener("click", () => {
    hideModal();
  });
  modalBackground.appendChild(modalCloseButtonContainer);
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

  modalBackground.appendChild(modal);
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
