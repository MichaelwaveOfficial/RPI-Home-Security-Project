
/**
 * Module to dynamically handle settings being updated by the user.
 */

document.addEventListener('DOMContentLoaded', function() {

    dropdownSetup()
    initaliseEventListeners()
    handleFormSubmission()

})

function dropdownSetup(){

    /**
     * Apply event listeners to available dropdown setting containers and their respective titles,
     * Once clicked, pass the users specified containers and its siblings.
     */

    const containers = document.querySelectorAll('.scroll-container')

    containers.forEach((container) => {

        const containerTitle = container.querySelector('.scroll-container-title')

        if (containerTitle) {

            containerTitle.addEventListener('click', () => {
                dropdownToggle(container, containers)
            })
        }
    })
}

function dropdownToggle(currentContainer, containers) {

    /**
     * Toggle the specified settings container visibility by adjusting its maximum height value once selected.
     */

    const currentContainerTitle = currentContainer.querySelector('.scroll-container-title')
    const currentContainerContent = currentContainer.querySelector('.settings-container')

    if (!currentContainerTitle || !currentContainerContent) return

    containers.forEach((container) => {

        if (container != currentContainer) {
            const content = container.querySelector('.settings-container')
            const title = container.querySelector('.scroll-container-title')

            if (content && title) {
                content.style.maxHeight = null 
                title.classList.remove('active')
            }
        }
    })

    currentContainerTitle.classList.toggle('active')
    currentContainerContent.style.maxHeight = currentContainerContent.style.maxHeight ? null : `${currentContainerContent.scrollHeight}px`
}

function initaliseEventListeners() {

    /**
     * Apply event listeners for all input fields within the settings page pertaining to sliders, toggles and selects. 
     */

    document.querySelectorAll('.settings-container').forEach((container) => {

        container.addEventListener('input', handleUserInput)
        container.addEventListener('change', handleUserInput)
    })
}

function handleUserInput(event) {

    /**
     * Handle users input to the fields.
     */

    const target = event.target

    if (target.matches('.slider')) {
        updateOutputField(`slider-output${target.id.slice(-1)}`, target.value)
    } else if (target.matches('.toggle')) {
        updateOutputField(
            `toggle-output${target.id.slice(-1)}`,
            target.checked ? (target.id === 'toggle0' ? 'On' : 'True') : (target.id === 'toggle0' ? 'Off' : 'False'))
    } else if (target.matches('.select')) {
        updateOutputField('select-output0', target.value)
    }
}

function updateOutputField(outputID, value) {

    /**
     * Update the html output field for the elements given ID value.
     */

    const output = document.getElementById(outputID)

    if (output) output.textContent = value
    
}

function handleFormSubmission() {

    const form = document.getElementById('settings-form')
    if (!form) return

    form.addEventListener('change', event => {

        event.preventDefault()

        const updatedSettings = new FormData(form)

        fetch('/settings/update', {
            method: 'POST',
            body: updatedSettings,
        })
            .then((response) => {
                if (!response.ok) throw new Error('Network response is not okay!')
                return response.json
            })
            .then((data) => {
                console.log('Settings updated successfully!', data)
            })
            .catch((error) => {
                console.error('There was an error updating settings!', error)
            })
    })
}