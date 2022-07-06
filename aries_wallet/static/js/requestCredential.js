import { add_to_db_and_sync } from '/static/js/backgroundSync.js';

window.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('[id^="requestCredential_"]');
    if (buttons) {
        for (const button of buttons) {
            button.addEventListener('click', () => {
                alert('Request submitted.')
                const cred_ex_id = button.id.split("_")[1];
                add_to_db_and_sync('request_credential', { 'cred_ex_id': cred_ex_id });
                window.location.reload();
            })
        }
    }
});
