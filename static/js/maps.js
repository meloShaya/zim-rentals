/**
 * Google Maps utility functions
 */

// Initialize map with marker
function initializeMap(
	mapElementId,
	latitude,
	longitude,
	title,
	draggable = false
) {
	// Check if the map element exists
	const mapElement = document.getElementById(mapElementId);
	if (!mapElement) {
		console.warn(`Map element with ID "${mapElementId}" not found`);
		return null;
	}

	// Create map
	const map = new google.maps.Map(mapElement, {
		center: { lat: latitude, lng: longitude },
		zoom: 15,
		mapTypeControl: true,
		streetViewControl: true,
		fullscreenControl: true,
	});

	// Create marker (use modern AdvancedMarkerElement if available)
	let marker;
	if (google.maps.marker && google.maps.marker.AdvancedMarkerElement) {
		marker = new google.maps.marker.AdvancedMarkerElement({
			position: { lat: latitude, lng: longitude },
			map: map,
			title: title,
		});
	} else {
		marker = new google.maps.Marker({
			position: { lat: latitude, lng: longitude },
			map: map,
			title: title,
			draggable: draggable,
		});
	}

	// Make marker draggable if needed
	if (draggable) {
		// For modern markers
		if (google.maps.marker && google.maps.marker.AdvancedMarkerElement) {
			marker.setDraggable(true);
		}

		// Add drag event listener
		google.maps.event.addListener(marker, "dragend", function () {
			const position = marker.getPosition();
			// Return position to callback if provided
			if (typeof window.markerDragCallback === "function") {
				window.markerDragCallback(position);
			}
		});
	}

	return { map, marker };
}

// Note: The functions isGoogleMapsLoaded and waitForGoogleMapsToLoad
// have been removed as their functionality is now handled by the
// Google Maps API callback mechanism implemented in base.html.
