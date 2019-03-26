(function () {
    var cards = document.querySelectorAll('.yourtablerow label .card')
    for (var i = 0; i < cards.length; ++i) {
        cards[i].addEventListener('click', function (ev) {
            var isEmpty = function(obj) {
                return Object.keys(obj).length == 0
            }
            var control = this.parentNode.control
            if (!control) {
                return
            }
            if (control.value != '0') {
                control.value = '0'
                return
            }
            var controls = document.querySelectorAll('.yourtablerow [name^="on_table_"]')
            var used = {};
            for (var i = 0; i < controls.length; ++i) {
                used[controls[i].value] = true
            }
            if (isEmpty(used)){
                return
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
