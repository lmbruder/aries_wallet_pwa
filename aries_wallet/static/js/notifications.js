window.addEventListener("DOMContentLoaded", () => {
    // get elements for notification dropdown
    const dropdown = document.getElementById("notif-dropdown");

    if (dropdown) {
        addDropdownHTML(dropdown);
    }

    const notifSpan = document.getElementById("count_notifs");
    if (notifSpan) {
        // call after load
        setUnreadCount(notifSpan);
    }

    // then call every 10 seconds
    setInterval(function () {
        if (notifSpan) {
            setUnreadCount(notifSpan);
        }
        if (dropdown) {
            addDropdownHTML(dropdown);
        }
    }, 10000);

    const dropdownBadge = document.getElementById("notification-dropdown");
    if (dropdownBadge) {
        dropdownBadge.addEventListener("click", () => {
            fetch("/inbox/notifications/mark-all-as-read/");
            setUnreadCount(notifSpan);
        });
    }
});

function getUnreadCount() {
    return fetch("/inbox/notifications/api/unread_count/")
        .then((response) => {
            return response.json();
        }).then((json) => {
            const count = json.unread_count;
            return count;
        });
}

function setUnreadCount(notifSpan) {
    getUnreadCount()
        .then((count) => notifSpan.textContent = count);
}

// unread and new notifications (less than 24 hours old)
function getAllNotifications() {
    return fetch("/inbox/notifications/api/all_list/")
        .then((response) => {
            return response.json();
        }).then((json) => {
            return json.all_list;
        });
}

function makeNotificationsPretty() {
    prettyNotifications = [];
    return getAllNotifications()
        .then((notifications) => {
            notifications.forEach((notif) => {
                const date = new Date(notif.timestamp);
                timeDiff = Math.round((Date.now() - date.getTime()) / 3600000);
                if (timeDiff < 24 || notif.unread == true) {
                    prettyNotifications.push(notif.verb.toString());
                }
            });
            return prettyNotifications;
        });
}

function addDropdownHTML(dropdown) {
    dropdown.innerHTML = "";

    makeNotificationsPretty().then((list) => {
        for (let i = 0; i < list.length - 1; i++) {
            const li = document.createElement("li");
            li.innerHTML = list[i];
            li.setAttribute("class", "dropdown-item");
            li.setAttribute("onClick", "fetchPage(this.innerHTML)");
            dropdown.appendChild(li);
        }
    });
}

function fetchPage(content) {
    if (content == "New presentation request.") {
        window.location.href = "/proof_requests";
    } else {
        window.location.href = "/";
    }
}
