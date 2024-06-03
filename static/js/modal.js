// Functions to create, open, and close modals
// https://bulma.io/documentation/components/modal/

function createModal(triggerElem, titleHtml, contentHtml, footerHtml = null) {
    const template = document.querySelector('#modal-template')
    const modalId = triggerElem.getAttribute('data-modal-id');
    let clone = template.content.cloneNode(true);
    let titleElem = clone.querySelector('.modal-card-title');
    let contentElem = clone.querySelector('.modal-card-body');
    let footElem = clone.querySelector('.modal-card-foot');

    if (!titleHtml) {
        titleElem.remove()
    } else {
        titleElem.innerHTML = titleHtml
    }

    if (!contentHtml) {
        contentElem.innerHTML = "It works!"
    } else {
        contentElem.innerHTML = contentHtml
    }

    if (!footerHtml) {
        footElem.innerHTML = `<div class="buttons">
            <button class="button is-success">Ok</button>
        </div>`
    } else {
        footElem.innerHTML = footerHtml
    }

    // identify this modal based on whatever the trigger says it's going to open
    clone.querySelector('.modal').setAttribute('data-modal-id', modalId);

    // wire up the ability to close the modal
    (clone.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button') || []).forEach(($close) => {
        const $target = $close.closest('.modal');

        $close.addEventListener('click', () => {
            closeModal($target);
        });
    });

    document.body.appendChild(clone);
    let modalElem = document.querySelector('.modal[data-modal-id="' + modalId + '"]');

    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") {
            closeModal(modalElem);
        }
    });

    // wire up the trigger 
    triggerElem.addEventListener('click', () => {
        //console.log('modal triggered', modalElem);
        openModal(modalElem);
    });
}

function openModal($el) {
    $el.classList.add('is-active');
}

function closeModal($el) {
    $el.classList.remove('is-active');
}

function closeAllModals() {
    (document.querySelectorAll('.modal') || []).forEach(($modal) => {
        closeModal($modal);
    });
}
