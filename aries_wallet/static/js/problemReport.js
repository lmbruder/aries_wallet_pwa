import { add_to_db_and_sync } from '/static/js/backgroundSync.js';

window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('problemReportForm');
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        alert('Request submitted.')
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const cred_ex_id = document.getElementById('id_cred_ex').value;
        const description = document.getElementById('id_description');
        const params = { 'csrftoken': csrftoken, 'cred_ex_id': cred_ex_id, 'description': description.value };
        add_to_db_and_sync('problem_report', params);

        description.value = '';
    })
});