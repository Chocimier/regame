(function () {
    var cards = document.querySelectorAll('label > .card')
    for (var i = 0; i < cards.length; ++i) {
        cards[i].addEventListener('click', function (ev, x, d) {
            var control = this.parentNode.control
            if (!control) {
                return
            }
            if (control.value != '0') {
                control.value = '0'
                return
            }
            var controls = control.form.querySelectorAll('[name^="on_table_"]')
            var used = {};
            for (var i = 0; i < controls.length; ++i) {
                used[controls[i].value] = true
            }
            for (var i = 1; i <= controls.length; ++i) {
                if (!used[i]) {
                    control.value = i;
                    return
                }
            }
        })
    }
})()
