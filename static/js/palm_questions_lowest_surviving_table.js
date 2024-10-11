let vanilla = null

window.onload = async function () {
    // table init options
    const options = {
        'table_placeholder': 'lowest-surviving-table-placeholder',
        'has_pagination': true,
        'on_go_to_page': onGoToPage,
        'columns': [
            {
                'name': 'id',
                'label': ' ',
                'selectable': false,
                'custom_body': function (record) {
                    return `<a href="/palm/${record['id']}" aria-label="Go to palm" title="Go to palm">
                                <i class="fa-solid fa-magnifying-glass"></i>
                            </a>`
                }
            },
            {
                'name': 'palmname',
                'label': 'Genus, Species'
            },
            {
                'name': 'min',
                'label': 'Low (Lowest)',
            },
            {
                'name': 'max',
                'label': 'Low (Highest)',
            },
            {
                'name': 'average',
                'label': 'Average',
            },
            {
                'name': 'records',
                'label': '# Observations'
            }
        ]
    }
    vanilla = new VanillaTable(options)

    // wire up custom events
    const $search = document.getElementById('lowest-surviving-search-input')
    $search.value = ''
    $search.addEventListener('input', vanilla.debounce(onLoadLowestSurvivingTable))

    // initial table population
    onLoadLowestSurvivingTable()
}

async function onLoadLowestSurvivingTable() {
    let meta = {}

    const $search = document.getElementById('lowest-surviving-search-input')
    if ($search.value) {
        meta.search = $search.value
    }

    let observations = await getObservations(meta)
    vanilla.refreshTable(observations)
}

async function getObservations(meta) {
    // localhost:5000/api/palm/?offset=0&page=2&results_per_page=15
    let url = '/api/palm/lowestsurviving'

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
        console.error('Failed to fetch the observation data.', error)
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
    if (!meta) {
        console.log('onGoToPage: meta is missing. Cannot proceed.')
        return
    }

    return await getObservations(meta)
}