(function () {
    var winConditionType = document.querySelector('#id_winconditiontype')
    winConditionType.addEventListener('change', function (ev) {
        var winConditionNumber = document.querySelector('#id_winconditionnumber')
        winConditionNumber.value = {
            'g': 21,
            'a': 8,
            't': 10,
        }[ev.target.value]
    })
})()
