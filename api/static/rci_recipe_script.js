$(document).ready(function (jQuery) {
    jQuery(function ($) {
        $('select').on('change', function (e) {
            let changed_id = e.target.id
            if (changed_id.includes('id_ingredients')) {
                var id = e.target.value;
                var parent = e.target.parentElement.parentElement.parentElement
                var unitsField = parent.children[4]
                $.ajax({
                    type: "GET",
                    url: `http://127.0.0.1:8000/api/ingredients/${id}/`,
                    error: function (request, status, error) {
                        unitsField.textContent = "------"
                    }
                })
                    .done(function (response) {
                        unitsField.textContent = response.allowedUnits.map((o, i) => {
                            return i === 0 ? o.full : " " + o.full
                        })
                    })
            }

        });
    });
});
