

/**
 * Modal Stuff
 */
let postModal = document.getElementById('postModal')
let postBtn = document.getElementById('postBtn')

postModal.addEventListener('shown.bs.modal', function () {
    postBtn.focus()
})


/**
 * Messageing Stuff
 */
const button = document.querySelector('.send-msg')
const message = document.querySelector('.msg')