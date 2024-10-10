let vanilla = null

window.onload = async function () {
    // table init options
    const options = {
        'table_placeholder': 'table-placeholder',
        'has_pagination': true,
        'on_go_to_page': onGoToPage,
        'columns': [
            // {
            //     'name': 'id',
            //     'label': ' ',
            //     'selectable': false,
            //     'custom_body': function (record) {
            //         return `<a href="/location/${record['id']}" aria-label="Go to location" title="Go to location">
            //                     <i class="fa-solid fa-magnifying-glass"></i>
            //                 </a>`
            //     }
            // },
            {
                'name': 'country',
                'label': 'Country'
            },
            {
                'name': 'state',
                'label': 'State'
            },
            {
                'name': 'city',
                'label': 'City'
            },
            {
                'name': 'events',
                'label': 'Events'
            },
            {
                'name': 'palm_observations',
                'label': 'Palm Observations'
            },
            {
                'name': 'cycad_observations',
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

    try {
        const response = await fetch(url)
        if (!response.ok) {
            throw new Error('Network response was not OK.', response)
        }

        const contentType = response.headers.get("content-type")
        if (!contentType || !contentType.includes("application/json"))
            throw new TypeError('Expected JSON response but got something else.')
        return await response.json()
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