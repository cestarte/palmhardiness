// Functions to create, open, and close modals
// https://bulma.io/documentation/components/modal/


function createModal($trigger, titleHtml, contentHtml, footerHtml = null) {
    /* 
    Parameters:
      $trigger - An element which will trigger this modal. 
          Adds `data-modal-id` attribute.
          If null, will open the modal immediately. 
      titleHtml - Raw HTML to display in the title. 
          If null, there will be no title element. 
      contentHtml - Raw HTML to display in the body.
      footerHtml - Raw HTML to display in the footer. Can be null. 
    */

    let $modal = document.createElement('div')
    $modal.classList.add('modal')

    // create a unique id for this modal
    if (typeof createModal.counter == 'undefined') {
        createModal.counter = 0;
    }
    createModal.counter++;
    const modalId = 'modal-' + createModal.counter
    $modal.setAttribute('data-modal-id', modalId);

    let $modalBackground = document.createElement('div')
    $modalBackground.classList.add('modal-background')
    $modal.appendChild($modalBackground)

    let $modalCard = document.createElement('div')
    $modalCard.classList.add('modal-card')
    $modal.appendChild($modalCard)

    // header
    if (titleHtml) {
        let $modalCardHead = document.createElement('header')
        $modalCardHead.classList.add('modal-card-head')
        $modalCard.appendChild($modalCardHead)

        let $modalCardTitle = document.createElement('p')
        $modalCardTitle.classList.add('modal-card-title')
        $modalCardTitle.innerHTML = titleHtml
        $modalCardHead.appendChild($modalCardTitle)

        let $modalCardClose = document.createElement('button')
        $modalCardClose.classList.add('delete')
        $modalCardClose.setAttribute('aria-label', 'close')
        $modalCardHead.appendChild($modalCardClose)
    }



    // body
    let $modalCardBody = document.createElement('section')
    $modalCardBody.classList.add('modal-card-body')
    $modalCardBody.innerHTML = contentHtml
    $modalCard.appendChild($modalCardBody)

    // footer
    if (footerHtml !== '') {
        let $modalCardFoot = document.createElement('footer')
        $modalCardFoot.classList.add('modal-card-foot')
        $modalCard.appendChild($modalCardFoot)
        if (footerHtml == 'undefined' || footerHtml == null) {
            $modalCardFoot.innerHTML = `<div class="buttons">
                <button class="button is-success">Ok</button>
            </div>`
        } else {
            $modalCardFoot.innerHTML = footerHtml
        }
    }

    // wire up the ability to close the modal
    ($modal.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button') || []).forEach(($close) => {
        const $target = $close.closest('.modal');

        $close.addEventListener('click', () => {
            closeModal($target);
        });
    });

    // escape key always closes the modal
    document.body.appendChild($modal);
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") {
            closeModal($modal);
        }
    });

    // wire up the trigger 
    if ($trigger) {
        $trigger.setAttribute('data-modal-id', modalId);
        $trigger.addEventListener('click', () => {
            //console.log('modal triggered', $modal);
            openModal($modal);
        });
    } else {
        // ...or open immediately if there's no trigger
        openModal($modal);
    }
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
