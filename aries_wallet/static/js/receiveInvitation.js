import { add_to_db_and_sync } from '/static/js/backgroundSync.js';

// wait for DOM to load
window.addEventListener('DOMContentLoaded', () => {
    // get the element with the invitationForm id
    const form = document.getElementById('invitationForm');
    if (form) {
        // add an submit event listener to the form
        form.addEventListener('submit', (event) => {
            // prevent the default handling of the form (POST/GET request)
            event.preventDefault();
            alert('Request submitted.')

            // add all relevant parameters to the params variable
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const invitation_url = document.getElementById('id_invitation_url');
            const params = { 'csrftoken': csrftoken, 'invitation_url': invitation_url.value };

            // call the add_to_db_and_sync function with the relevant params
            add_to_db_and_sync('receive_invitation', params);

            // clean up the field
            invitation_url.value = '';
        })
    }
});