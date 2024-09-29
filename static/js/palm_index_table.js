let vanilla = null

window.onload = async function () {
    // table init options
    const options = {
        'table_placeholder': 'table-placeholder',
        //'has_search': true,
        //'on_search': onReloadIndex,
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
                'name': 'genus',
                'label': 'Genus'
            },
            {
                'name': 'species',
                'label': 'Species'
            },
            {
                'name': 'variety',
                'label': 'Variety'
            },
            {
                'name': 'common_name',
                'label': 'Common Name',
                'editable': true,
                'onEdit': function (name, oldValue, newValue, row, col) {
                    //if a different row is dirty, prevent editing
                    // if this row has been edited, check if the value is changed
                    if (oldValue !== newValue) {
                        // row is dirty
                    }
                    // if the value is changed, check if it is valid

                    // if the value is invalid, display an 

                    if (validateCommonName(newValue)) {
                        console.log(`onEdit: ${name} = ${newValue}`, oldValue, row, col)
                    } else {
                        alert('Invalid common name')
                        return false
                    }
                }
            },
            {
                'name': 'zone_name',
                'custom_label': `                   
                <div class="dropdown is-hoverable">
                    <div class="dropdown-trigger">
                        Zone <i class="fa-solid fa-circle-info is-size-7" aria-haspopup="true"
                            aria-controls="zone-help"></i>
                    </div>
                    <div class="dropdown-menu" id="zone-help" role="menu">
                        <div class="dropdown-content">
                            <div class="dropdown-item is-size-7 has-text-weight-normal">
                                <p>USDA Hardiness Zones are based on the average annual minimum
                                    temperature.</p>
                                <a target="_blank" href="https://planthardiness.ars.usda.gov/"> <i
                                        class="fa-solid fa-arrow-up-right-from-square"></i> More info at
                                    usda.gov</a>
                            </div>
                        </div>
                    </div>
                </div>`,
                'editable': true,
                'onEdit': function (name, oldValue, newValue, row, col) {
                    console.log(`onEdit: ${name} = ${newValue}`, oldValue, row, col)
                }
            },
            {
                'name': 'observation_count',
                'label': '# Observations'
            }
        ]
    }
    vanilla = new VanillaTable(options)

    // wire up custom events
    const $search = document.getElementById('search-input')
    $search.value = ''
    const $filtered = document.getElementById('filter-unobserved')
    $filtered.checked = false
    $search.addEventListener('input', vanilla.debounce(onReloadIndex))
    $filtered.addEventListener('change', (e) => onReloadIndex())

    // initial table population
    const observations = await getObservations()
    vanilla.refreshTable(observations)
}

async function onReloadIndex() {
    console.log('onReloadIndex')
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
    // localhost:5000/api/palm/?offset=0&page=2&results_per_page=15
    let url = '/api/palm/'

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