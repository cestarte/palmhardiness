const options = {
    'table_placeholder': 'datasource-table-placeholder',
    'has_pagination': false,
    'columns': [
        {
            'name': 'source',
            'label': 'Source',
            'formatters': ['link']
        },
        {
            'name': 'count',
            'label': 'Count',
        },
        {
            'name': 'type',
            'label': 'Type',
        },
    ]
}
let vanilla = new VanillaTable(options)

// initial table population
onLoadDataSourceTable(vanilla)

async function onLoadDataSourceTable(vanillaTable) {
    let sources = await getDataSources()
    vanillaTable.refreshTable(sources)
}

async function getDataSources() {
    let url = '/api/datasource/'

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

        json = await response.json()
        saveToLocalStorage(url, json)
        return json
    } catch (error) {
        console.error('Failed to fetch the data source data.', error)
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