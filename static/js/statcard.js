
class StatCard {
    constructor($parent, title, value, onLoad = null) {
        if ($parent === null) {
            throw new Error('Card: $parent is null')
        }

        this.$parent = $parent
        this.$card = this.buildCard(title, value)
        this.onLoad = onLoad

        // handle loading
        if (this.onLoad !== null && typeof this.onLoad === 'function') {
            this.onLoad().then((json) => {
                this.setValue(this.$card, json.value)
                this.$parent.appendChild(this.$card)
            });
        } else {
            this.$parent.appendChild(this.$card)
        }
    }

    calcRems(length) {
        let rem = 3
        if (length > 5)
            rem = 2.5
        if (length > 7)
            rem = 2
        if (length > 9)
            rem = 1

        return `${rem}rem`
    }

    setValue($card, value) {
        let $value = $card.querySelector('.value')
        $value.style.fontSize = `${this.calcRems(value.length)}`
        $value.innerHTML = value
    }

    buildCard(title, value) {
        let $card = document.createElement('div')
        //$card.classList.add('box')//'is-justify-content-space-between'
        $card.innerHTML = `
            <div class="stat-body">
                <div class="">
                    <p class="has-text-centered has-text-weight-bold value" style="font-size:${this.calcRems(value.length)};">${value}</p>
                </div>
            </div>
            <footer class="">
                <div class="">
                    <p class="has-text-centered has-text-weight-normal style="white-space: nowrap;">${title}</p>
                </div>
            </footer>
        `
        return $card
    }


}