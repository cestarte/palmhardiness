const NAMESPACE = 'PCH_'

function listLocalStorageKeys() {
    for (let i = 0; i < localStorage.length; i++) {
        console.log(`key ${localStorage.key(i)}`, localStorage.getItem(localStorage.key(i)))
    }
}

function clearLocalStorageKeys() {
    // Clear all keys that start with the namespace
    // Sometimes in some browsers, looping through and 
    // calling removeKeys() doesn't clear them all in one pass, or even in 
    // a few passes. SO we'll loop until we're done or we hit a max number 
    // of iterations.
    let numRemoved = 0
    const maxIterations = 50
    let numIterations = 0
    while (++numIterations <= maxIterations) {
        for (let i = 0; i < localStorage.length; i++) {
            if (localStorage.key(i).startsWith(NAMESPACE)) {
                ++numRemoved
                localStorage.removeItem(localStorage.key(i))
            }
        }
    }
    console.log(`Cleared ${numRemoved} keys from local storage.`)
}

function saveToLocalStorage(key, value, path = null) {
    if (!key)
        return

    const keyName = NAMESPACE + key
    let toStore = {
        'data': value,
        'storageTime': Date.now()
    }
    if (path)
        toStore['path'] = path

    try {
        localStorage.setItem(NAMESPACE + key, JSON.stringify(toStore))
    } catch (err) {
        console.warn(`Failed to save ${keyName} to local storage.`, err)
    }
}

function getFromLocalStorage(key) {
    if (!key)
        return

    let data = null
    let retrieved = JSON.parse(localStorage.getItem(NAMESPACE + key))
    if (retrieved && retrieved.data && retrieved.storageTime) {
        // Use the data if it's not too old
        const now = new Date()
        const daysToAllow = 3
        let earliest = new Date()
        earliest.setDate(now.getDate() - daysToAllow)
        const whenStored = new Date(retrieved.storageTime)

        if (earliest.getTime() < whenStored.getTime())
            data = retrieved.data
        else
            localStorage.removeItem(NAMESPACE + key)
    }

    //console.log(`getFromLocalStorage(${key})`, data)
    return data
}