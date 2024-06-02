
function refreshTable(term, meta) {
    let url = 'http://localhost:5000/api/palm?search='
    if (term)
        url += term;
    if (meta) {
        for (let key in meta) {
            url += '&' + key + '=' + meta[key];
        }
    }

    getApiData(url).then(data => {
        console.log('api results', data);
        buildTableBody('palm-table', data);
        buildTablePagination('palm-table', data);
    }).catch(error => {
        console.error(error);
    });
}

function buildTableBody(tableId, data) {
    let table = document.querySelector('#' + tableId);
    let tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    data.records.forEach(p => {
        let tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <a href="/palm/${p['id']}" aria-label="Go to palm" title="Go to palm">
                    <i class="fa-solid fa-magnifying-glass"></i>
                </a> 
            </td>
            <td>${p['genus'] || ''}</td>
            <td>${p['species'] || ''}</td>
            <td>${p['variety'] || ''}</td>
            <td>${p['common_name'] || ''}</td>
            <td>${p['zone_name'] || ''}</td>
            <td>${p['observation_count']}</td>
        `;
        tbody.appendChild(tr);
    });
    if (data.records.length == 0) {
        let tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="7" style="text-align:center"><em>No data available.</em></td>';
        tbody.appendChild(tr);
    }
}

function buildTablePagination(tableDataId, data) {
    const placeholderElem = document.querySelector('[data-id="pagination-placeholder"]');
    const template = document.querySelector('#table-pagination')
    let clone = template.content.cloneNode(true);
    let currentPageElem = clone.querySelector('[name="current-page"]');
    let pageInputElem = clone.querySelector('[name="page-input"]');
    let pageInputGoElem = clone.querySelector('[name="go"]');
    let totalPagesElem = clone.querySelector('[name="total_pages"]');
    let resultsOnThisPageElem = clone.querySelector('[name="results_on_this_page"]');
    let totalResultsElem = clone.querySelector('[name="total_results"]');
    let nextPageElem = clone.querySelector('.pagination-next');
    let prevPageElem = clone.querySelector('.pagination-previous');

    currentPageElem.innerText = data.meta.page;
    pageInputElem.value = data.meta.page;
    totalPagesElem.innerText = data.meta.total_pages;
    resultsOnThisPageElem.innerText = data.meta.results_on_this_page;
    totalResultsElem.innerText = data.meta.total_results;

    // If only 1 page, disable the prev button
    if (data.meta.page <= 1) {
        prevPageElem.setAttribute('disabled', '');
    } else {
        // ... otherwise, wire up the prev button
        prevPageElem.addEventListener('click', function (e) {
            e.preventDefault();
            refreshTable(data.meta.search, { 'page': data.meta.page - 1, 'results_per_page': data.meta.results_per_page });
        });
    }

    // If at the last page, disable the next button
    if (data.meta.page == data.meta.total_pages) {
        nextPageElem.setAttribute('disabled', '');
    } else {
        // ...otherwise, wire up the next button
        nextPageElem.addEventListener('click', function (e) {
            e.preventDefault();
            refreshTable(data.meta.search, { 'page': data.meta.page + 1, 'results_per_page': data.meta.results_per_page });
        });
    }

    // If only 1 page, disable the input 
    if (data.meta.total_pages <= 1) {
        pageInputElem.setAttribute('disabled', '');
        pageInputGoElem.setAttribute('disabled', '');
    } else {
        // ...otherwise, wire up the go button
        pageInputGoElem.addEventListener('click', function (e) {
            e.preventDefault();
            let page = parseInt(pageInputElem.value);
            if (page > 0 && page <= data.meta.total_pages) {
                refreshTable(data.meta.search, { 'page': page, 'results_per_page': data.meta.results_per_page });
            }
        });
    }


    let table = document.querySelector('[data-id="' + tableDataId + '"]');

    // insert the pagination after the table (or table-container element) 
    //table.parentNode.parentNode.insertBefore(clone, table.parentNode.nextSibling);
    placeholderElem.innerHTML = '';
    placeholderElem.appendChild(clone);
}

async function getApiData(url) {
    let response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    let data = await response.json();
    return data;
}

function debounce(func, timeout = 510) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}
const processSearch = debounce((term) => refreshTable(term));