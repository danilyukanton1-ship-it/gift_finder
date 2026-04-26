(function($) {
    $(document).ready(function() {
        // Функция загрузки тегов для выбранного вопроса
        function loadTags(questionId) {
            if (!questionId) return;

            $.get('/gifts/ajax/get-tags-by-question/', {question_id: questionId})
                .done(function(data) {
                    var select = $('#id_filtered_tags');
                    var currentSelected = select.val() || [];

                    select.empty();

                    $.each(data.tags, function(id, name) {
                        var option = $('<option>', {
                            value: id,
                            text: name
                        });
                        if (currentSelected.indexOf(id) !== -1) {
                            option.attr('selected', true);
                        }
                        select.append(option);
                    });
                });
        }

        // При изменении вопроса
        $('#id_tag_question').on('change', function() {
            loadTags($(this).val());
        });

        // При загрузке страницы
        var initialQuestion = $('#id_tag_question').val();
        if (initialQuestion) {
            loadTags(initialQuestion);
        }
    });
})(django.jQuery);