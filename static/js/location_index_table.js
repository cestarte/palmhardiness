let vanilla = null

window.onload = async function () {
    // table init options
    const options = {
        'table_placeholder': 'table-placeholder',
        'has_pagination': true,
        'on_go_to_page': onGoToPage,
        'columns': [
            {
                'name': 'locationname',
                'label': 'Location',
                'width': '45%'
            },
            {
                'name': 'events',
                'label': 'Events'
            },
            {
                'name': 'palmobservations',
                'label': 'Palm Observations'
            },
            {
                'name': 'cycadobservations',
                'label': 'Cycad Observations'
            },
        ]
    }
    vanilla = new VanillaTable(options)

    // wire up custom events
    const $search = document.getElementById('search-input')
    $search.value = ''
    $search.addEventListener('input', vanilla.debounce(onLoadIndexTable))

    // initial table population
    onLoadIndexTable()
}

async function onLoadIndexTable() {
    let meta = {}

    const $search = document.getElementById('search-input')
    if ($search.value) {
        meta.search = $search.value
    }

    let observations = await getLocations(meta)
    vanilla.refreshTable(observations)
}

async function getLocations(meta) {
    // localhost:5000/api/location/?offset=0&page=2&results_per_page=15
    let url = '/api/location/'

    // Object may have multiple query parameters.
    if (meta && typeof meta === 'object') {
        let isFirstAddon = true

        for (const [key, value] of Object.entries(meta)) {
            if (key === 'search' && !value)
                continue // skip empty search term

            if (isFirstAddon) {
                url += `?${key}=${value}`
                isFirstAddon = false
            } else
                url += `&${key}=${value}`
        }
    }

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
        console.error('Failed to fetch the location data.', error)
        return {
            'meta': {
                'search': null,
                'has_next_page': false,
                'has_previous_page': false,
                'offset': 0,
                'page': 1,
                'results_on_this_page': 0,
                'results_per_page': 15,
                'total_pages': 1,
                'total_results': 0
            },
            'records': []
        }
    }
}

async function onGoToPage(e, meta) {
    //console.log('onGoToPage', meta)
    if (!meta) {
        console.log('onGoToPage: meta is missing. Cannot proceed.')
        return
    }

    return await getLocations(meta)
}