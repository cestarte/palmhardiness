let vanilla = null

window.onload = async function () {
    // table init options
    const options = {
        'table_placeholder': 'lowest-survived-table-placeholder',
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
                'name': 'name',
                'label': 'Genus, Species',
                'width': '50%',
                'on_click': (colName, $th) => {
                    const sortOrder = toggleSortOrder($th)
                    onLoadLowestSurvivingTable(null, { 'sort_by': colName, 'sort_order': sortOrder })
                }
            },
            {
                'name': 'min',
                'label': 'Lowest Observed',
                'on_click': (colName, $th) => {
                    const sortOrder = toggleSortOrder($th)
                    onLoadLowestSurvivingTable(null, { 'sort_by': colName, 'sort_order': sortOrder })
                }
            },
            {
                'name': 'max',
                'label': 'Highest (Low) Observed',
                'on_click': (colName, $th) => {
                    const sortOrder = toggleSortOrder($th)
                    onLoadLowestSurvivingTable(null, { 'sort_by': colName, 'sort_order': sortOrder })
                }
            },
            {
                'name': 'average',
                'label': 'Average',
                'on_click': (colName, $th) => {
                    const sortOrder = toggleSortOrder($th)
                    onLoadLowestSurvivingTable(null, { 'sort_by': colName, 'sort_order': sortOrder })
                }
            },
            {
                'name': 'records',
                'label': 'Observations',
                'on_click': (colName, $th) => {
                    const sortOrder = toggleSortOrder($th)
                    onLoadLowestSurvivingTable(null, { 'sort_by': colName, 'sort_order': sortOrder })
                }
            }
        ]
    }
    vanilla = new VanillaTable(options)

    // wire up custom events
    const $search = document.getElementById('lowest-survived-search-input')
    $search.value = ''
    $search.addEventListener('input', vanilla.debounce(onLoadLowestSurvivingTable))

    // initial table population
    onLoadLowestSurvivingTable(null)
}

function toggleSortOrder($th) {
    console.log('toggleSortOrder', $th)
    // remove the sort order from all other columns
    const $thead = $th.parentElement
    const $ths = $thead.querySelectorAll('th')
    $ths.forEach($elem => {
        if (!$elem.isSameNode($th)) {
            $elem.classList.remove('is-sorted-asc')
            $elem.classList.remove('is-sorted-desc')
        }
    })

    // toggle the sort order of this column
    let sortOrder = $th.classList.contains('is-sorted-asc') ? 'asc' : 'desc'
    if (!sortOrder || sortOrder === 'asc') {
        $th.classList.remove('is-sorted-asc')
        $th.classList.add('is-sorted-desc')
        return 'desc'
    } else {
        $th.classList.remove('is-sorted-desc')
        $th.classList.add('is-sorted-asc')
        return 'asc'
    }
}

function buildMeta(metaParts = null) {
    // Start with a default object which will be adjusted and returned.
    let meta = {
        'search': null,
        //'has_next_page': false,     // calculated by api
        //'has_previous_page': false, // calculated by api
        'offset': 0,
        'page': 1,
        //'results_on_this_page': 0,  // calculated by api
        'results_per_page': 15,
        //'total_pages': 1,           // calculated by api
        //'total_results': 0,         // calculated by api
        'sort_by': null,
        'sort_order': null,
    }

    // 1: If any bits of meta were passed in, overwrite the defaults. 
    if (metaParts && typeof metaParts === 'object') {
        for (const [key, value] of Object.entries(metaParts)) {
            // certain data can be ignored
            if (key === 'results_on_this_page' || key === 'total_pages'
                || key === 'total_results'
                || key === 'has_next_page' || key === 'has_previous_page'
            )
                continue

            meta[key] = value
        }
    }

    // 2: Figure out the sort order and column to sort by.
    // $ths = vanilla.$table.querySelectorAll('th')
    // for (let i = 0; i < $ths.length; i++) {
    //     if ($ths[i].classList.contains('is-sorted-asc')) {
    //         // ascending
    //         meta.sort_order = 'asc'
    //         meta.sort_by = $ths[i].getAttribute('data-col-name')
    //         break
    //     } else if ($ths[i].classList.contains('is-sorted-desc')) {
    //         // descending
    //         meta.sort_order = 'desc'
    //         meta.sort_by = $ths[i].getAttribute('data-col-name')
    //         break
    //     } else {
    //         // Default to descending order by name
    //         meta.sort_order = 'desc'
    //         meta.sort_by = 'name'
    //     }
    // }

    // 3: populate the search term with whatever is in the input box
    const $search = document.getElementById('lowest-survived-search-input')
    meta.search = $search.value

    return meta
}

async function onLoadLowestSurvivingTable(event, meta = null) {
    let observations = await getObservations(buildMeta(meta))
    vanilla.refreshTable(observations)
}

async function getObservations(meta) {
    // Build the URL from the meta object.
    // localhost:5000/api/palm/?offset=0&page=2&results_per_page=15
    let url = '/api/palm/lowestsurvived'

    // Object may have multiple query parameters.
    if (meta && typeof meta === 'object') {
        let isFirstAddon = true

        for (const [key, value] of Object.entries(meta)) {
            // if (key === 'search' && !value)
            //     continue // skip empty search term

            if (isFirstAddon) {
                url += `?${key}=${value}`
                isFirstAddon = false
            } else
                url += `&${key}=${value}`
        }
    }

    // Always attempt to read from localstorage to save bandwidth.
    let localStorageData = null // TODO getFromLocalStorage(url)
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
        // TODO saveToLocalStorage(url, json)
        return json
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
                'total_results': 0,
                'sort_by': null,
                'sort_order': null,
            },
            'records': []
        }
    }
}

async function onGoToPage(e, meta) {
    if (!meta) {
        console.error('onGoToPage: meta is missing. Cannot proceed.')
        return
    }

    return await getObservations(buildMeta(meta))
}