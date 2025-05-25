// notifications.js - Handles WebSocket notifications

document.addEventListener("DOMContentLoaded", function () {
	// Only connect if user is authenticated (check for a data attribute on body)
	const isAuthenticated =
		document.body.getAttribute("data-user-authenticated") === "true";

	if (!isAuthenticated) {
		return;
	}

	let notificationSocket = null;
	let reconnectAttempts = 0;
	const maxReconnectAttempts = 5;
	const reconnectDelay = 5000; // 5 seconds

	function connectNotificationSocket() {
		if (notificationSocket) {
			notificationSocket.close();
		}

		const protocol =
			window.location.protocol === "https:" ? "wss://" : "ws://";
		const wsUrl = protocol + window.location.host + "/ws/notifications/";
		console.log("Connecting to notification socket:", wsUrl);

		notificationSocket = new WebSocket(wsUrl);

		notificationSocket.onopen = function (e) {
			console.log("Notification socket connected");
			reconnectAttempts = 0;
		};

		notificationSocket.onmessage = function (e) {
			const data = JSON.parse(e.data);

			if (data.type === "notification") {
				const message = data.message;

				// Handle different notification types
				if (message.type === "price_alert") {
					showNotification(message.title, message.body, message.url);
				}
			}
		};

		notificationSocket.onclose = function (e) {
			console.log("Notification socket closed");

			// Try to reconnect
			if (reconnectAttempts < maxReconnectAttempts) {
				reconnectAttempts++;
				console.log(
					`Reconnecting (${reconnectAttempts}/${maxReconnectAttempts})...`
				);
				setTimeout(connectNotificationSocket, reconnectDelay);
			} else {
				console.log("Max reconnect attempts reached");
			}
		};

		notificationSocket.onerror = function (e) {
			console.error("Notification socket error:", e);
		};
	}

	// Show notification using the browser API if available
	function showNotification(title, body, url) {
		// Create and add a DOM notification (fallback)
		createDOMNotification(title, body, url);

		// Also try to use browser notifications if permission granted
		if (window.Notification && Notification.permission === "granted") {
			const notification = new Notification(title, {
				body: body,
				icon: "/static/img/logo.png",
			});

			notification.onclick = function () {
				window.open(url, "_blank");
				notification.close();
			};
		} else if (
			window.Notification &&
			Notification.permission !== "denied"
		) {
			Notification.requestPermission().then(function (permission) {
				if (permission === "granted") {
					const notification = new Notification(title, {
						body: body,
						icon: "/static/img/logo.png",
					});

					notification.onclick = function () {
						window.open(url, "_blank");
						notification.close();
					};
				}
			});
		}
	}

	// Create a DOM notification
	function createDOMNotification(title, body, url) {
		// Check if notifications container exists, create if not
		let container = document.getElementById("notification-container");
		if (!container) {
			container = document.createElement("div");
			container.id = "notification-container";
			container.style.position = "fixed";
			container.style.bottom = "20px";
			container.style.right = "20px";
			container.style.zIndex = "9999";
			document.body.appendChild(container);
		}

		// Create notification element
		const notification = document.createElement("div");
		notification.className = "alert alert-info alert-dismissible fade show";
		notification.role = "alert";
		notification.style.marginTop = "10px";
		notification.style.boxShadow = "0 4px 8px rgba(0,0,0,0.1)";
		notification.style.minWidth = "300px";
		notification.style.cursor = "pointer";

		notification.innerHTML = `
            <strong>${title}</strong>
            <p>${body}</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

		// Add click handler to go to URL
		notification.addEventListener("click", function (e) {
			if (!e.target.classList.contains("btn-close")) {
				window.location.href = url;
			}
		});

		// Add to container
		container.appendChild(notification);

		// Auto-remove after 10 seconds
		setTimeout(() => {
			notification.classList.remove("show");
			setTimeout(() => {
				container.removeChild(notification);
			}, 300);
		}, 10000);
	}

	// Request notification permission on page load
	if (
		window.Notification &&
		Notification.permission !== "granted" &&
		Notification.permission !== "denied"
	) {
		// Delay asking for permission to avoid overwhelming the user
		setTimeout(function () {
			Notification.requestPermission();
		}, 5000);
	}

	// Connect to notification socket
	connectNotificationSocket();
});
