


let screenshotModal = document.getElementById('screenshotModal')
if (screenshotModal) {
    screenshotModal.addEventListener('show.bs.modal', function (event) {
        // Button that triggered the modal
        let button = event.relatedTarget
        // Extract info from data-bs-* attributes
        let screenshotSrc = button.getAttribute('data-src')
        let screenshotName = button.getAttribute('data-name')

        console.log(`Opening screenshot modal for: ${screenshotName} (${screenshotSrc})`)
        console.log(button)

        // Update the modal's content.
        let modalImage = screenshotModal.querySelector('#screenshotModalImage')
        modalImage.src = screenshotSrc

        let modalTitle = screenshotModal.querySelector('#screenshotModalLabel')
        modalTitle.textContent = screenshotName
    })
}
