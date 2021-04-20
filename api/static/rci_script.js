$(document).ready(function (jQuery) {
    jQuery(function ($) {
        $('select#id_ingredient').on('change', function () {
            var e = document.getElementById("id_ingredient");
            var id = e.value;

            $.ajax({
                type: "GET",
                url: `http://127.0.0.1:8000/api/ingredients/${id}/`,
                error: function (request, status, error) {
                    document.getElementById('id_allowed_units').textContent = "------"
                }
            })
                .done(function (response) {
                    console.log(response.status)
                    document.getElementById('id_allowed_units').textContent = response.allowedUnits.map((o, i) => {
                        return i === 0 ? o.full : " " + o.full
                    })
                })

        });
    });
});
