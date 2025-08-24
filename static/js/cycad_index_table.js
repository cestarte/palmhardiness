let vanilla = null

window.onload = async function () {
    // table init options
    const options = {
        'table_placeholder': 'table-placeholder',
        'has_pagination': true,
        'on_go_to_page': onGoToPage,
        'columns': [
            {
                'name': 'id',
                'label': ' ',
                'selectable': false,
                'custom_body': function (record) {
                    return `<a href="/cycad/${record['id']}" aria-label="Go to cycad" title="Go to cycad">
                                <i class="fa-solid fa-magnifying-glass"></i>
                            </a>`
                }
            },
            {
                'name': 'cycadname',
                'label': 'Genus, Species, Variety'
            },
            {
                'name': 'commonname',
                'label': 'Common Name'
            },
            {
                'name': 'observationcount',
                'label': 'Observations'
            }
        ]
    }
    vanilla = new VanillaTable(options)

    // wire up custom events
    const $search = document.getElementById('search-input')
    $search.value = ''
    const $filtered = document.getElementById('filter-unobserved')
    $filtered.checked = true
    $search.addEventListener('input', vanilla.debounce(onLoadIndexTable))
    $filtered.addEventListener('change', (e) => onLoadIndexTable())

    // initial table population
    onLoadIndexTable()
}

async function onLoadIndexTable() {
    let meta = {}

    if (document.getElementById('filter-unobserved').checked)
        meta.filter_unobserved = true
    else
        meta.filter_unobserved = false

    const $search = document.getElementById('search-input')
    if ($search.value) {
        meta.search = $search.value
    }

    let observations = await getObservations(meta)
    vanilla.refreshTable(observations)
}

async function getObservations(meta) {
    // localhost:5000/api/cycad/?offset=0&page=2&results_per_page=15
    let url = '/api/cycad/'

    // Object may have multiple query parameters.
    if (meta && typeof meta === 'object') {
        let isFirstAddon = true

        if (document.getElementById('filter-unobserved').checked)
            meta.filter_unobserved = true

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
        console.error('Failed to fetch the observation data.', error)
        return {
            'meta': {
                'search': null,
                'filter_unobserved': false,
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

    return await getObservations(meta)
}