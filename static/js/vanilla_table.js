var vanillaTableUnique = 0;

class VanillaTable {
    constructor(options) {
        console.log('VanillaTable constructor', options)
        if (options.parent_elem_id === null) {
            console.error('Parent element cannot be null.')
            throw new Error('Parent element cannot be null.')
        }

        if (options.data_url === null) {
            console.error('Data URL cannot be null.')
            throw new Error('Data URL cannot be null.')
        }

        this.options = options;

        this.$placeholder = document.getElementById(this.options.table_elem_id);
        if (this.$placeholder === null) {
            throw new Error(`Table placeholder element not found. "${this.options.table_elem_id}"`)
        }

        this.$table = null
        this.pagination = null
    }

    createTable(options = null) {
        if (options === null) {
            options = this.options
        }
        const $template = document.querySelector('#table-template')
        let clone = $template.content.cloneNode(true);

        if (this.$template === null) {
            console.error('Table template not found. Did you forget to include the html template?')
            throw new Error('Table template not found.')
        }

        this.populateTableHeader(clone, options.columns)
        this.populateTableBody(clone, options.data)
        this.$placeholder.appendChild(clone)
        this.$table = this.$placeholder.querySelector('table')

        if (this.options.has_search) {
            this.createSearch(this.options)
        }
    }

    populateTableHeader($table, columns) {
        let $thead = $table.querySelector('thead')
        let $tr = document.createElement('tr')
        columns.forEach(column => {
            let $th = document.createElement('th')
            $th.classList.add('is-primary')
            if (column.label) {
                $th.innerText = column.label
            } else if (column.custom_label) {
                $th.innerHTML = column.custom_label
            } else {
                $th.innerText = column.name
            }
            $tr.appendChild($th)
        })
        $thead.appendChild($tr)
    }

    populateTableBody($table, records = []) {
        let $tbody = $table.querySelector('tbody')
        $tbody.innerHTML = '';

        records.forEach(record => {
            let $tr = document.createElement('tr')
            this.options.columns.forEach(column => {
                let $td = document.createElement('td')
                if (column.custom_body) {
                    $td.innerHTML = column.custom_body(record, column.name)
                } else {
                    $td.innerHTML = record[column.name]
                }
                $tr.appendChild($td)
            })
            $tbody.appendChild($tr)
        })
        if (records.length == 0) {
            let $tr = document.createElement('tr');
            $tr.innerHTML = `<td colspan="${this.options.columns.length}" style="text-align:center"><em>No data available.</em></td>`;
            $tbody.appendChild($tr);
        }
    }

    async getApiData(url) {
        let response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();;
    }

    refreshTable(term, meta = {}) {
        let url = this.options.data_url

        if (term) {
            if (url.endsWith('?') === false && url.endsWith('&') === false) {
                if (url.includes('?') === true) {
                    url += '&'
                } else {
                    url += '?'
                }
            }
            url += 'search=' + term
        }

        for (let key in meta) {
            if (url.includes('?') === false) {
                url += `?${key}=${meta[key]}`
            } else {
                url += `&${key}=${meta[key]}`
            }
        }

        this.getApiData(url).then(data => {
            this.populateTableBody(this.$table, data.records)
            this.createPagination(data)
        }).catch(error => {
            console.error(error)
        });
    }

    createPagination(data, options = null) {
        if (options === null) {
            options = this.options
        }
        if (!options || !options.has_pagination) {
            return
        }

        const $template = document.querySelector('#table-pagination-template')
        const $placeholder = document.getElementById(options.pagination_elem_id)

        if (this.$template === null) {
            console.error('Pagination template not found. Did you forget to include the html template?')
            throw new Error('Pagination template not found.')
        }

        if ($placeholder === null) {
            console.error('Pagination placeholder element not found.', options.pagination_elem_id)
            throw new Error('Pagination placeholder element not found.')
        }

        if (!data || !data.meta) {
            console.error('No data or meta information found.')
            $placeholder.innerHTML = ''
            return
        }

        let clone = $template.content.cloneNode(true)
        let $currentPage = clone.querySelector('[name="current-page"]')
        let $pageInput = clone.querySelector('[name="page-input"]')
        let $goButton = clone.querySelector('[name="go"]')
        let $totalPages = clone.querySelector('[name="total_pages"]')
        let $resultsOnThisPage = clone.querySelector('[name="results_on_this_page"]')
        let $totalResults = clone.querySelector('[name="total_results"]')
        let $nextPage = clone.querySelector('.pagination-next')
        let $prevPage = clone.querySelector('.pagination-previous')

        $currentPage.innerText = data.meta.page
        $pageInput.value = data.meta.page
        $totalPages.innerText = data.meta.total_pages
        $resultsOnThisPage.innerText = data.meta.results_on_this_page
        $totalResults.innerText = data.meta.total_results

        let self = this
        // If only 1 page, disable the prev button
        if (data.meta.page <= 1) {
            $prevPage.setAttribute('disabled', '')
        } else {
            // ... otherwise, wire up the prev button
            $prevPage.addEventListener('click', function (e) {
                e.preventDefault()
                self.refreshTable(data.meta.search, { 'page': data.meta.page - 1, 'results_per_page': data.meta.results_per_page })
            });
        }

        // If at the last page, disable the next button
        if (data.meta.page == data.meta.total_pages) {
            $nextPage.setAttribute('disabled', '')
        } else {
            // ...otherwise, wire up the next button
            $nextPage.addEventListener('click', function (e) {
                e.preventDefault()
                self.refreshTable(data.meta.search, { 'page': data.meta.page + 1, 'results_per_page': data.meta.results_per_page })
            });
        }

        // If only 1 page, disable the input 
        if (data.meta.total_pages <= 1) {
            $pageInput.setAttribute('disabled', '')
            $goButton.setAttribute('disabled', '')
        } else {
            // ...otherwise, wire up the go button
            $goButton.addEventListener('click', function (e) {
                e.preventDefault()
                let page = parseInt($pageInput.value)
                if (page > 0 && page <= data.meta.total_pages) {
                    self.refreshTable(data.meta.search, { 'page': page, 'results_per_page': data.meta.results_per_page });
                }
            })
        }

        $placeholder.innerHTML = ''
        $placeholder.appendChild(clone)

    }

    createSearch(options) {
        if (options === null) {
            options = this.options
        }
        if (!options || !options.has_search) {
            return
        }

        const $template = document.querySelector('#table-search-template')
        const $placeholder = document.getElementById(options.search_elem_id);

        if (this.$template === null) {
            console.error('Search template not found. Did you forget to include the html template?')
            throw new Error('Search template not found.')
        }

        if ($placeholder === null) {
            console.error('Search placeholder element not found.', options.search_elem_id)
            throw new Error('Search placeholder element not found.')
        }

        let clone = $template.content.cloneNode(true)
        let $searchInput = clone.querySelector('[name="search-input"]')

        let self = this
        $searchInput.addEventListener('input', function (e) {
            self.processSearch(this.value)
        });

        $placeholder.innerHTML = ''
        $placeholder.appendChild(clone)
    }

    debounce(func, timeout = 510) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => { func.apply(this, args); }, timeout);
        };
    }

    processSearch = this.debounce((term) => this.refreshTable(term));
}

// refreshTable(null, { 'page': 1, 'results_per_page': 15 });