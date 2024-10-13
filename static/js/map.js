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
    let data = []

    console.log('getEventLocations: checking from localstorage')
    // Always attempt to read from localstorage to save bandwidth.
    let localStorageData = getFromLocalStorage(url)
    if (localStorageData)
        return localStorageData

    console.log('getEventLocations: fetching event locations')
    // Fetch from the server. The item(s) are not in localstorage.
    try {
        console.log('getEventLocations: fetching event locations')
        let response = await fetch(url)
        data = await response.json()
    } catch (error) {
        console.error('Failed to fetch the event locations.', error)
    }

    saveToLocalStorage(url, data)
    return data
}

function addEventMarkers(events) {
    events.forEach(event => {
        if (!event.latitude || !event.longitude)
            return // continue the loop

        //console.log('adding event marker', event.name)
        if (event.lastmodified) {
            date = new Date(event.lastmodified)
            event.lastmodified = date.toLocaleString()
        }
        let marker = L.marker([event.latitude, event.longitude], { icon: eventIcon })
            .bindPopup(`
            <div class="popup-record">
                <span class='is-label'>Event</span>: ${event.name}
                <br /><span class='is-label'>Description</span>: ${event.description}
                <div class="popup-record-detail">
                    <span class='is-label'>Who Reported</span>: ${event.whoreported}
                    <br /><span class='is-label'>Last Modified</span>: ${event.lastmodified}
                    <br /><span class='is-label'>Who Modified</span>: ${event.whomodified}
                </div>
            </div>`)
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

function shortenUrlForMap(address) {
    if (URL.canParse(address)) {
        let url = new URL(address)
        return url.hostname
    }

    return address
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
        if (!o.latitude || !o.longitude)
            return // continue the loop

        //console.log(`adding ${plantType} observation marker`, palm.name)
        if (o.lastmodified) {
            const date = new Date(o.lastmodified)
            o.lastmodified = date.toLocaleString()
        }

        const plantId = o.palmId || o.cycadId
        let htmlPopupContent = `
            <div class="popup-record">
                <span class='is-label'>Name</span>: <a href="/${plantType}/${plantId}" target="_blank">${o.name}</a>
                <br /><span class='is-label'>Common Name</span>: ${o.commonname || ''}
                <br /><span class='is-label'>Low Temp</span>: ${o.lowtemp}&nbsp°F (${((o.lowtemp - 32) * 5 / 9).toFixed(2)}&nbsp°C)
                <br /><span class='is-label'>Damage</span>: ${o.damagetext}
                <br /><span class='is-label'>Description</span>: ${o.description || ''}
                <br /><span class='is-label'>Location</span>: ${o.locationname}
                <br /><span class='is-label'>Event</span>: ${o.eventname}
                <br /><span class='is-label'>Source</span>: <a href="${o.source}" target="_blank" title="${o.source}">${shortenUrlForMap(o.source)}</a>
                <div class="popup-record-detail">
                    <span class='is-label'>Who Reported</span>: ${o.whoreported}
                    <br /><span class='is-label'>Last Modified</span>: ${o.lastmodified}
                    <br /><span class='is-label'>Who Modified</span>: ${o.whomodified}
                </div>
            </div>
            `

        let marker = L.marker([o.latitude, o.longitude], { icon: plantType === 'palm' ? palmIcon : cycadIcon })
            .bindPopup(htmlPopupContent)

        if (plantType === 'palm')
            palmObservationsLayerGroup.addLayer(marker)
        else cycadObservationsLayerGroup.addLayer(marker)
    })
}

function clearMapLocalStorageKeys() {
    localStorage.removeItem('PCH_/api/observation/palm')
    localStorage.removeItem('PCH_/api/observation/cycad')
    localStorage.removeItem('PCH_/api/event')
}