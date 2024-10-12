/* 
 * Requires:
 *   - Leaflet.js (global L)
 */

const eventsLayerGroup = L.layerGroup()
const palmObservationsLayerGroup = L.layerGroup()
const cycadObservationsLayerGroup = L.layerGroup()

let map = L.map('map')
    .setView([29.424, -98.491], 9) // default to San Antonio, TX

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map)

var layerControl = L.control.layers(null, null).addTo(map)
layerControl.addOverlay(eventsLayerGroup, "Events", true)
layerControl.addOverlay(palmObservationsLayerGroup, "Palm Observations")
layerControl.addOverlay(cycadObservationsLayerGroup, "Cycad Observations")
layerControl.addTo(map)
eventsLayerGroup.addTo(map) // default 'on'

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
        //console.log('got user coord', position.coords)
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
    const url = '/api/event'

    // Always attempt to read from localstorage to save bandwidth.
    let localStorageData = getFromLocalStorage(url)
    if (localStorageData)
        return localStorageData

    // Fetch from the server. The item(s) are not in localstorage.
    let response = await fetch(url)
    let data = await response.json()
    saveToLocalStorage(url, data)
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

        let marker = L.marker([event.latitude, event.longitude], { icon: eventIcon })
            .bindPopup(`<strong>Event</strong>: ${event.name}
            <br /><strong>Description</strong>: ${event.description}
            <div class="popup-record-detail">
                <strong>Who Reported</strong>: ${event.who_reported}
                <br /><strong>Last Modified</strong>: ${event.last_modified}
                <br /><strong>Who Modified</strong>: ${event.who_reported}
            </div>
            `);
        eventsLayerGroup.addLayer(marker)
    })
}

async function getObservations(plantType) {
    if (!plantType) {
        console.error('No plant type provided. Expecting "palm" or "cycad".')
        return
    }

    let data = []
    plantType = plantType.toLowerCase()
    const url = `/api/observation/${plantType}`

    // Always attempt to read from localstorage to save bandwidth.
    let localStorageData = getFromLocalStorage(url)
    if (localStorageData)
        return localStorageData

    // Fetch from the server. The item(s) are not in localstorage.
    try {
        let response = await fetch(url)
        data = await response.json()
        saveToLocalStorage(url, data)
        //console.log(`got ${plantType} observations`, data)
    } catch (error) {
        console.error('Failed to fetch the observation data.', error)
    }

    return data
}

function addObservationMarkers(observations, plantType) {
    if (!plantType) {
        console.error('No plant type provided. Expecting "palm" or "cycad".')
        return
    }
    if (!observations) {
        console.warning(`No ${plantType} observations to add to the map.`)
        return
    }

    observations.forEach(o => {
        //console.log(o.PalmId, o.Latitude, o.Longitude)
        if (!o.Latitude || !o.Longitude)
            return // continue the loop

        //console.log(`adding ${plantType} observation marker`, palm.name)
        if (o.LastModified) {
            date = new Date(o.LastModified + ' UTC')
            o.LastModified = date.toLocaleString()
        }

        let locationName = o.Country
        if (o.State && locationName)
            locationName += `, ${o.State}`
        else locationName = o.State
        if (o.City)
            locationName += `, ${o.City}`
        else locationName = o.City

        let plantName = o.Genus
        if (o.Species)
            plantName += ` ${o.Species}`
        if (o.Variety)
            plantName += ` ${o.Variety}`

        let plantId = o.PalmId || o.CycadId

        let htmlPopupContent = `
            <strong>Name</strong>: <a href="/${plantType}/${plantId}" target="_blank">${plantName}</a>
            <br /><strong>Common Name</strong>: ${o.CommonName || ''}
            <br /><strong>Low Temp</strong>: ${o.LowTemp}&nbsp°F (${((o.LowTemp - 32) * 5 / 9).toFixed(2)}&nbsp°C)
            <br /><strong>Damage</strong>: ${o.DamageText}
            <br /><strong>Description</strong>: ${o.Description | ''}
            <br /><strong>Location</strong>: ${locationName}
            <br /><strong>Event</strong>: (${o.EventId}): ${o.EventName}
            <br /><strong>Source</strong>: <a href="${o.Source}" target="_blank">${o.Source}</a>
            <div class="popup-record-detail">
                <strong>Who Reported</strong>: ${o.WhoReported}
                <br /><strong>Last Modified</strong>: ${o.LastModified}
                <br /><strong>Who Modified</strong>: ${o.WhoModified}
            </div>
            `

        let marker = L.marker([o.Latitude, o.Longitude], { icon: plantType === 'palm' ? palmIcon : cycadIcon })
            .bindPopup(htmlPopupContent)

        if (plantType === 'palm')
            palmObservationsLayerGroup.addLayer(marker)
        else cycadObservationsLayerGroup.addLayer(marker)
    })
}
