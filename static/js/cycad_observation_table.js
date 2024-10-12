async function getObservationsAsync() {
    // the page url path ends with the plant id
    const plantId = window.location.pathname.split('/').pop()
    const url = `/api/cycad/${plantId}/observations`;

    // Always attempt to read from localstorage to save bandwidth.
    let localStorageData = getFromLocalStorage(url)
    if (localStorageData)
        return localStorageData

    // Fetch from the server. The item(s) are not in localstorage.
    try {
        const response = await fetch(url)
        if (!response.ok) {
            throw new Error('Network response was not OK.', response)
        }

        const contentType = response.headers.get("content-type")
        if (!contentType || !contentType.includes("application/json"))
            throw new TypeError('Expected JSON response but got something else.')

        const json = await response.json()
        saveToLocalStorage(url, json)
        return json
    } catch (error) {
        console.error('Failed to fetch the observation data.', error)
        return []
    }
}

window.onload = async function () {
    let options = {
        'table_placeholder': 'observation-table',
        'columns': [
            {
                'name': 'locationname',
                'label': 'Location',
            },
            {
                'name': 'lowtemp',
                'label': 'Low Temp',
                'custom_body': (record, columnName, $cell) => {
                    const id = VanillaTable.generateId()
                    let $elem = document.createElement('div')
                    $elem.innerHTML = `<p>
                    ${record[columnName]}&nbsp°F</p><p>
                    ${((record[columnName] - 32) * 5 / 9).toFixed(2)}&nbsp°C
                    </p>`
                    return $elem
                }
            },
            {
                'name': 'damagetext',
                'label': 'Damage'
            },
            {
                'name': 'description',
                'label': 'Description',
                'formatters': ['max_len', 'text'],
                'on_click': (record, columnName, $cell) => {
                    if (record[columnName] && record[columnName].length > 100)
                        createModal(null, '', record[columnName], '')
                }
            },
            {
                'name': 'eventname',
                'label': 'Event Name',
            },
            {
                'name': 'eventdescription',
                'label': 'Event Description',
                'formatters': ['max_len', 'text'],
                'on_click': (record, columnName, $cell) => {
                    if (record[columnName] && record[columnName].length > 100)
                        createModal(null, record['eventname'], record[columnName], '')
                }
            },
            {
                'name': 'eventwhoreported',
                'label': 'Event Reporter'
            },
            {
                'name': 'source',
                'label': 'Source',
                'formatters': ['link'],
            }
        ]
    }
    let vanilla = new VanillaTable(options)
    let observations = await getObservationsAsync()
    vanilla.populateTableBody(observations)
}