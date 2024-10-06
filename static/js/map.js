/* 
 * Requires:
 *   - Leaflet.js (global L)
 */

const eventIcon = L.divIcon({
    className: 'event-marker',
    html: '<span>E</span>'
});
const palmIcon = L.divIcon({
    className: 'palm-observation-marker',
    html: '<span>P</span>'
});
const cycadIcon = L.divIcon({
    className: 'cycad-observation-marker',
    html: '<span>C</span>'
});


function setMapViewToUserLocation() {
    function onGotUserCoords(position) {
        console.log('got user coord', position.coords)
        map.setView([position.coords.latitude, position.coords.longitude], 9);
    }

    function onFailedUserCoords(err) {
        console.warn(`ERROR(${err.code}): ${err.message}`);
    }

    const options = {
        enableHighAccuracy: false,
        // only wait 3 seconds
        timeout: 3000,
        // if possible, use up to 30 minute old cache
        maximumAge: 1000 * 60 * 30
    };

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(onGotUserCoords, onFailedUserCoords, options)
    }
}

async function getEventLocations() {
    let response = await fetch('/api/event')
    let data = await response.json()
    //console.log('got event locations', data)
    return data
}

function addEventMarkers(events) {
    events.forEach(event => {
        if (!event.latitude || !event.longitude)
            return // continue the loop

        //console.log('adding event marker', event.name)
        if (event.last_modified) {
            date = new Date(event.last_modified + ' UTC')
            event.last_modified = date.toLocaleString()
        }

        L.marker([event.latitude, event.longitude], { icon: eventIcon }).addTo(map)
            .bindPopup(`<strong>Event</strong>: ${event.name}
            <br /><strong>Description</strong>: ${event.description}
            <br /><strong>Who Reported</strong>: ${event.who_reported}
            <br /><strong>Last Modified</strong>: ${event.last_modified}
            <br /><strong>Who Modified</strong>: ${event.who_modified}
            `);
    })
}

async function getPalmObservations() {
    data = []
    try {
        let response = await fetch('/api/observation/palm')
        data = await response.json()
        console.log('got palm observations', data)
    } catch (error) {
        console.error('Failed to fetch the observation data.', error)
    }

    return data
}

function addPalmObservationMarkers(palmObservations) {
    if (!palmObservations) {
        console.warning('No palm observations to add to the map.')
        return
    }

    palmObservations.forEach(o => {
        //console.log(o.PalmId, o.Latitude, o.Longitude)
        if (!o.Latitude || !o.Longitude)
            return // continue the loop

        //console.log('adding palm observation marker', palm.name)
        if (o.LastModified) {
            date = new Date(o.LastModified + ' UTC')
            o.LastModified = date.toLocaleString()
        }

        locationName = o.Country
        if (o.State && locationName)
            locationName += `, ${o.State}`
        else locationName = o.State
        if (o.City)
            locationName += `, ${o.City}`
        else locationName = o.City

        let htmlPopupContent = `
            <strong>Name</strong>: <a href="/palm/${o.PalmId}" target="_blank">${o.Genus} ${o.Species} ${o.Variety}</a>
            <br /><strong>Common Name</strong>: ${o.CommonName || ''}
            <br /><strong>Low Temp</strong>: ${o.LowTemp}&nbsp°F (${((o.LowTemp - 32) * 5 / 9).toFixed(2)}&nbsp°C)
            <br /><strong>Damage</strong>: ${o.DamageText}
            <br /><strong>Description</strong>: ${o.Description | ''}
            <br /><strong>Location</strong>: <a href="#">${locationName}</a>
            <br /><strong>Event</strong>: <a href="#">${o.EventId}: ${o.EventName}</a>
            <br /><strong>Who Reported</strong>: ${o.WhoReported}
            <br /><strong>Last Modified</strong>: ${o.LastModified}
            <br /><strong>Who Modified</strong>: ${o.WhoModified}
            <br /><strong>Source</strong>: <a href="${o.Source}" target="_blank">${o.Source}</a>
            `
        L.marker([o.Latitude, o.Longitude], { icon: palmIcon }).addTo(map)
            .bindPopup(htmlPopupContent)
    })
}


async function getCycadObservations() {
    data = []
    try {
        let response = await fetch('/api/observation/cycad')
        data = await response.json()
        console.log('got cycad observations', data)
    } catch (error) {
        console.error('Failed to fetch the observation data.', error)
    }

    return data
}

function addCycadObservationMarkers(cycadObservations) {
    if (!cycadObservations) {
        console.warning('No cycad observations to add to the map.')
        return
    }

    cycadObservations.forEach(o => {
        //console.log(o.CycadId, o.Latitude, o.Longitude)
        if (!o.Latitude || !o.Longitude)
            return // continue the loop

        if (o.LastModified) {
            date = new Date(o.LastModified + ' UTC')
            o.LastModified = date.toLocaleString()
        }

        locationName = o.Country
        if (o.State && locationName)
            locationName += `, ${o.State}`
        else locationName = o.State
        if (o.City)
            locationName += `, ${o.City}`
        else locationName = o.City

        let htmlPopupContent = `
            <strong>Name</strong>: <a href="/palm/${o.CycadId}" target="_blank">${o.Genus} ${o.Species} ${o.Variety}</a>
            <br /><strong>Common Name</strong>: ${o.CommonName || ''}
            <br /><strong>Low Temp</strong>: ${o.LowTemp}&nbsp°F (${((o.LowTemp - 32) * 5 / 9).toFixed(2)}&nbsp°C)
            <br /><strong>Damage</strong>: ${o.DamageText}
            <br /><strong>Description</strong>: ${o.Description | ''}
            <br /><strong>Location</strong>: <a href="#">${locationName}</a>
            <br /><strong>Event</strong>: <a href="#">${o.EventId}: ${o.EventName}</a>
            <br /><strong>Who Reported</strong>: ${o.WhoReported}
            <br /><strong>Last Modified</strong>: ${o.LastModified}
            <br /><strong>Who Modified</strong>: ${o.WhoModified}
            <br /><strong>Source</strong>: <a href="${o.Source}" target="_blank">${o.Source}</a>
            `
        L.marker([o.Latitude, o.Longitude], { icon: cycadIcon }).addTo(map)
            .bindPopup(htmlPopupContent)
    })
}