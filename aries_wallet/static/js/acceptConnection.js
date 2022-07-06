import { add_to_db_and_sync } from '/static/js/backgroundSync.js';

window.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('[id^="acceptConnection_"]');
    if (buttons) {
        for (const button of buttons) {
            button.addEventListener('click', () => {
                alert('Request submitted.')
                const connection_id = button.id.split("_")[1];
                add_to_db_and_sync('accept_connection', { 'connection_id': connection_id });
                window.location.reload();
            })
        }
    }
});
