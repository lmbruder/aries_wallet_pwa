import { add_to_db_and_sync } from '/static/js/backgroundSync.js';

window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('presentProofForm');
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        alert('Request submitted.')
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const credential_id = document.getElementById('id_credential');
        const pres_ex_id = document.getElementById('id_pres_ex').value;
        const params = { 'csrftoken': csrftoken, 'credential_id': credential_id.value, 'pres_ex_id': pres_ex_id };
        add_to_db_and_sync('present_proof', params);

        credential_id.value = '';
    })
});