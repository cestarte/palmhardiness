var vanillaTableUnique = 0;

class VanillaTable {
    constructor(options) {
        this.debug = true
        this.FORMATTER_MAX_LEN = 100

        if (this.debug)
            console.log('VanillaTable.constructor', options)

        this.options = options;

        this.$placeholder = document.getElementById(this.options.table_placeholder);
        if (this.$placeholder === null) {
            throw new Error(`VanillaTable placeholder element not found. "${this.options.table_placeholder}"`)
        }

        this.$table = null
        this.pagination = null
        this.$selectedCell = null

        this.insertTemplates()
        this.createTable()
    }

    insertTemplates() {
        if (this.debug)
            console.log('VanilltaTable.insertTemplates')

        const tableTemplate = `
            <template id="table-template">
                <table class="table is-striped is-fullwidth" id="observation-table">
                    <thead>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </template>
        `

        const tablePaginationTemplate = `
            <template id="table-pagination-template">
                <p class="mt-1">
                    Page <span name="current-page"></span> of <span name="total_pages"></span>.
                    Showing <span name="results_on_this_page"></span> of <span name="total_results"></span> results.
                </p>
                <nav class="pagination" role="navigation" aria-label="pagination">
                    <a href="#" class="pagination-previous">Previous</a>
                    <a href="#" class="pagination-next">Next page</a>

                    <ul class="pagination-list">
                        <li>
                            <input type="input" type="number" class="input" value="" name="page-input" size="3" />
                        </li>
                        <li>
                            <a href="#" class="pagination-link" name="go" aria-label="Go to page">Go</a>
                        </li>
                    </ul>
            </template>
        `

        const tableSearchTemplate = `
            <template id="table-search-template">
                <div class="grid mb-1">
                    <div class="cell">
                    </div>
                    <div class="cell">
                    </div>
                    <div class="cell">
                        <input type="text" name="search-input" class="input" placeholder="Search..." value="" />
                    </div>
                </div>
            </template>
        `

        document.body.insertAdjacentHTML("beforeEnd", tableTemplate)
        document.body.insertAdjacentHTML("beforeEnd", tablePaginationTemplate)
        document.body.insertAdjacentHTML("beforeEnd", tableSearchTemplate)
    }

    setSelectedCellByElem($cell) {
        if (this.debug)
            console.log('setSelectedCellByElem', $cell)

        if ($cell) {
            let row = $cell.getAttribute('data-row')
            let col = $cell.getAttribute('data-col')
            this.setSelectedCell(row, col)
        } else {
            console.error('setSelectedCellByElem: $cell is null.')
        }
    }

    setSelectedCell(row, col) {
        if (this.debug)
            console.log('VanillaTable.setSelectedCell', row, col)

        let $prevCell = this.$selectedCell

        // Special rule: if the row, col is 0,0 it means to remove the selection
        if (row === 0 && col === 0) {
            if ($prevCell) {
                $prevCell.classList.remove('has-background-info-light')
                this.$selectedCell = null
            }
            return
        }

        // Normal operation: select the cell at row, col
        // Note: row,col are not necessarily numbers. Don't use parseInt
        let $td = this.$table.querySelector(`td[data-row="${row}"][data-col="${col}"]`)
        if ($td) {
            $td.classList.add('has-background-info-light')
            this.$selectedCell = $td
            if ($prevCell) {
                $prevCell.classList.remove('has-background-info-light')
            }
        } else {
            console.error(`setSelectedCell: cell at row: ${row}, col: ${col} not found.`)
        }
    }

    onDocumentKeyUp(event) {
        if (this.debug)
            console.log('VanillaTable.onDocumentKeyUp', event)

        // Grab the current selected cell and look at the DOM to determine 
        // the new selected cell.
        // Why? The table may have been sorted or filtered or expanded.
        switch (event.key) {
            case "Enter":
                if (this.$selectedCell) {
                    const row = this.$selectedCell.getAttribute('data-row')
                    const col = this.$selectedCell.getAttribute('data-col')
                    //console.log(`Enter key pressed while (${row}, ${col}) is selected.`)

                    const editable = this.$selectedCell.getAttribute('data-editable') === 'true'
                    if (editable) {
                        //console.log('this cell is editable')
                        const val = this.$selectedCell.getAttribute('data-value')
                        this.$selectedCell.focus()
                    }
                } else {
                    //console.log('Enter key pressed but no cell is selected.')
                }
                break
            case "Escape":
                //console.log('Escape key pressed.')
                self.setSelectedCell(0, 0)
                break
            case "ArrowUp":
                if (this.$selectedCell) {
                    const $thisRow = this.$selectedCell.parentElement
                    let $rowAbove = $thisRow.previousElementSibling

                    while ($rowAbove) {
                        const col = this.$selectedCell.getAttribute('data-col')
                        const $cellAbove = $rowAbove.querySelector(`td[data-col="${col}"]`)

                        if ($cellAbove) {
                            const selectable = $cellAbove.getAttribute('data-selectable') !== 'false'
                            const rowIsVisible = $rowAbove.style.display !== 'none'

                            if (selectable && rowIsVisible) {
                                this.setSelectedCellByElem($cellAbove)
                                this.scrollIntoViewIfNeeded($cellAbove)
                                break
                            }
                        }

                        $rowAbove = $rowAbove.previousElementSibling
                    }
                }
                break
            case "ArrowDown":
                if (this.$selectedCell) {
                    const $thisRow = this.$selectedCell.parentElement
                    let $rowBelow = $thisRow.nextElementSibling

                    while ($rowBelow) {
                        const col = this.$selectedCell.getAttribute('data-col')
                        const $cellBelow = $rowBelow.querySelector(`td[data-col="${col}"]`)
                        if ($cellBelow) {
                            const selectable = $cellBelow.getAttribute('data-selectable') !== 'false'
                            const rowIsVisible = $rowBelow.style.display !== 'none'
                            if (selectable && rowIsVisible) {
                                console.log('is visible and selectable')
                                this.setSelectedCellByElem($cellBelow)
                                this.scrollIntoViewIfNeeded($cellBelow)
                                break
                            }
                        }

                        $rowBelow = $rowBelow.nextElementSibling
                    }
                }
                break
            case "ArrowLeft":
                if (this.$selectedCell) {
                    let $cellLeft = this.$selectedCell.previousElementSibling

                    // keep searching left until we find a selectable cell
                    while ($cellLeft) {
                        const selectable = $cellLeft.getAttribute('data-selectable') !== 'false'
                        const isCellVisible = $cellLeft.style.display !== 'none'
                        if (selectable !== false && isCellVisible) {
                            this.setSelectedCellByElem($cellLeft)
                            this.scrollIntoViewIfNeeded($cellLeft)
                            break
                        } else {
                            $cellLeft = $cellLeft.previousElementSibling
                        }
                    }
                }
                break
            case "ArrowRight":
                if (this.$selectedCell) {
                    let $cellRight = this.$selectedCell.nextElementSibling

                    // keep searching right until we find a selectable cell
                    while ($cellRight) {
                        const selectable = $cellRight.getAttribute('data-selectable') !== 'false'
                        const isCellVisible = $cellRight.style.display !== 'none'
                        if (selectable !== false && isCellVisible) {
                            this.setSelectedCellByElem($cellRight)
                            this.scrollIntoViewIfNeeded($cellRight)
                            break
                        } else {
                            $cellRight = $cellRight.nextElementSibling
                        }
                    }
                }
                break
        }

        event.preventDefault()
    }

    scrollIntoViewIfNeeded($element) {
        if (this.debug)
            console.log('VanillaTable.scrollIntoViewIfNeeded', $element)

        if (!$element) {
            console.error('VanillaTable.scrollIntoViewIfNeeded: $element is null.')
            return
        }
        const rect = $element.getBoundingClientRect()
        const isVisibleVertical = (rect.top >= 0) && (rect.bottom <= window.innerHeight)
        const isVisibleHorizontal = (rect.left >= 0) && (rect.right <= window.innerWidth)
        if (!isVisibleVertical || !isVisibleHorizontal) {
            $element.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" })
        }
    }

    createTable(options = this.options) {
        if (this.debug)
            console.log('VanillaTable.createTable', options)

        const $template = document.querySelector('#table-template')
        let clone = $template.content.cloneNode(true);

        if (this.$template === null) {
            console.error('Table template not found. Did you forget to include the html template?')
            throw new Error('Table template not found.')
        }

        this.$placeholder.appendChild(clone)
        this.$table = this.$placeholder.querySelector('table')

        this.populateTableHeader(options.columns)
        this.populateTableBody(options.data)


        // prevent key listeners from interfering with the table
        window.addEventListener("keydown", (e) => {
            if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.code)) {
                e.preventDefault()
            }
        }, false)
        document.removeEventListener("keyup", (e) => this.onDocumentKeyUp(e), true)
        // (re)apply key listeners to the document
        document.addEventListener("keyup", (e) => this.onDocumentKeyUp(e), true)

        this.$table.addEventListener("click", (e) => {
            let row = e.target.getAttribute('data-row')
            let col = e.target.getAttribute('data-col')
            //console.log(`Click on row: ${row}, col: ${col}.`)
            this.setSelectedCell(row, col)
        })

        if (this.options.has_search) {
            this.createSearch(this.options)
        }
    }

    populateTableHeader(columns) {
        // Populates the table header with the given columns.
        if (this.debug)
            console.log('VanillaTable.populateTableHeader', columns)

        let $thead = this.$table.querySelector('thead')
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

    populateTableBody(records = []) {
        // Populates the table body with the given records.
        if (this.debug)
            console.log('VanillaTable.populateTableBody', records)

        let $tbody = this.$table.querySelector('tbody')
        $tbody.innerHTML = '';

        let row = 0
        records.forEach(record => {
            let $tr = document.createElement('tr')
            ++row
            let col = 0
            this.options.columns.forEach(column => {
                let $td = document.createElement('td')
                $td.setAttribute('data-row', row)
                $td.setAttribute('data-col', ++col)

                if (column.selectable === false)
                    $td.setAttribute('data-selectable', column.selectable)

                if (column.editable === true && column.onEdit) {
                    //console.log('setting editable', column.name)

                    $td.setAttribute('data-editable', 'true')
                    $td.setAttribute('contenteditable', 'true')
                    $td.setAttribute('data-value', record[column.name])

                    let self = this
                    $td.addEventListener('input', function (e, fn = column.onEdit, name = column.name, oldValue = record[column.name], r = row, c = col) {
                        // console.log(e)
                        // console.log('name', name)
                        // console.log('oldValue', oldValue)
                        // console.log('newValue', e.target.innerText)
                        // console.log('row,col', r, c)
                        // console.log('fn', fn)
                        self.handleEdit(name, oldValue, e.target.innerText, r, c, fn)
                    })
                }

                if (column.on_click) {
                    $td.addEventListener('click', (event) => column.on_click(record, column.name, $td))
                }

                // Cell custom body and formatters are exclusive of each other. 
                if (column.custom_body && !column.formatters) {
                    // There is a custom body and there are no formatters specified.
                    // The custom body can be a string, HTMLElement, or function which returns HTML string
                    if (column.custom_body instanceof HTMLElement) {
                        console.log('custom_body is HTMLElement')
                        $td.appendChild(column.custom_body)
                    } else if (typeof column.custom_body === 'function') {
                        console.log('custom_body is function')
                        const $elem = column.custom_body(record, column.name, $td)
                        $td.append($elem)
                    } else {
                        console.log('custom_body is string')
                        $td.innerHTML = column.custom_body
                    }
                } else if (!column.custom_body && column.formatters && column.formatters.length > 0) {
                    // There are formatters and there is not a custom body. 
                    let formattedValue = record[column.name]
                    column.formatters.forEach(formatter => {
                        if (this.formatters[formatter]) {
                            formattedValue = this.formatters[formatter](formattedValue)
                        }
                    })
                    $td.innerHTML = formattedValue
                } else {
                    // Just output basic record if...
                    //   * neither custom body nor formatters are defined
                    //   * both custom body & formatters are defined
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

    formatters = {
        date: (value) => {
            if (!value) return ''
            return new Date(value).toLocaleDateString()
        },
        datetime: (value) => {
            if (!value) return ''
            return new Date(value).toLocaleString()
        },
        time: (value) => {
            if (!value) return ''
            return new Date(value).toLocaleTimeString()
        },
        currency: (value) => {
            if (!value) return ''
            return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
        },
        number: (value) => {
            if (!value) return ''
            return new Intl.NumberFormat('en-US').format(value)
        },
        html: (value) => {
            if (!value) return ''

            // replace line breaks with br tags
            value = value.replace(/(?:\r\n|\r|\n)/g, '<br>')
            // replace tabs with 4 spaces
            value = value.replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;')

            return value
        },
        max_len: (value, maxLen = this.FORMATTER_MAX_LEN) => {
            if (!value) return ''

            if (value.length > maxLen) {
                return value.substring(0, maxLen) + '...'
            }
            return value
        },
        sanitize: (value) => {
            if (!value) return ''

            return value.replace(/</g, '&lt;').replace(/>/g, '&gt;')
        },
        text: (value) => {
            if (!value) return ''

            // replace br tag with line break
            value = value.replace(/<br>/g, '\n')
            // replace tabs with 4 spaces
            value = value.replace(/\t/g, '    ')
            // remove html tags
            value = value.replace(/<[^>]*>?/gm, '')

            return value
        },
    }

    // async getApiData(url) {
    //     if (this.debug)
    //         console.log('VanillaTable.getApiData', url)

    //     let response = await fetch(url);
    //     if (!response.ok) {
    //         throw new Error(`HTTP error! status: ${response.status}`);
    //     }
    //     return await response.json()
    // }

    // refreshTable(term, meta = {}) {
    //     if (this.debug)
    //         console.log('VanillaTable.refreshTable', term, meta)

    //     let url = this.options.data_url

    //     if (term) {
    //         if (url.endsWith('?') === false && url.endsWith('&') === false) {
    //             if (url.includes('?') === true) {
    //                 url += '&'
    //             } else {
    //                 url += '?'
    //             }
    //         }
    //         url += 'search=' + term
    //     }

    //     for (let key in meta) {
    //         if (url.includes('?') === false) {
    //             url += `?${key}=${meta[key]}`
    //         } else {
    //             url += `&${key}=${meta[key]}`
    //         }
    //     }

    //     if (this.options.custom_url_builder) {
    //         url = this.options.custom_url_builder(url)
    //     }

    //     this.getApiData(url).then(data => {
    //         this.populateTableBody(this.$table, data.records)
    //         if (this.has_pagination) {
    //             this.createPagination(data)
    //         }
    //     }).catch(error => {
    //         console.error(error)
    //     });
    // }

    createPagination(data, options = null) {
        if (this.debug)
            console.log('VanillaTable.createPagination', data, options)

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
        if (this.debug)
            console.log('VanillaTable.createSearch', options)

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

        if (options.custom_search_addon) {
            let $customPlaceholder = clone.querySelector('[name="custom-search-addon-placeholder"]')
            options.custom_search_addon($customPlaceholder)
        }

        $placeholder.innerHTML = ''
        $placeholder.appendChild(clone)
    }

    static generateId() {
        // borrowed from https://stackoverflow.com/questions/6860853/generate-random-string-for-div-id/6860916#6860916
        function S4() {
            return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
        }

        return `id${S4()}-${S4()}-${S4()}`
    }

    debounce(func, timeout = 510) {
        let timer
        return (...args) => {
            clearTimeout(timer)
            timer = setTimeout(() => { func.apply(this, args); }, timeout)
        };
    }

    processSearch = this.debounce((term) => this.refreshTable(term))
    handleEdit = this.debounce((name, oldValue, newValue, row, col, fn) => fn(name, oldValue, newValue, row, col))
}

// refreshTable(null, { 'page': 1, 'results_per_page': 15 })
