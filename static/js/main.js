function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    headers: {'X-CSRFToken': csrftoken}
});

$(function () {
    $(".like-btn, .dislike-btn").click(function (e) {
        e.preventDefault();
        let question_id = $(this).data("qid");
        let like_type = $(this).data("like-type"); // "like" или "dislike"

        $.ajax({
            url: "/ajax/toggle_like/",
            method: "POST",
            data: {
                question_id: question_id,
                like_type: like_type
            },
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            success: function (response) {
                if (response.success) {
                    let likes = response.likes_count || 0;
                    let dislikes = response.dislikes_count || 0;
                    let difference = likes - dislikes;

                    $("#likes-count-" + question_id).text("👍 " + likes);
                    $("#dislikes-count-" + question_id).text("👎 " + dislikes);
                    $("#like-diff-" + question_id).text("🤝 " + difference);
                } else {
                    alert("Ошибка: " + response.error);
                }
            },
            error: function () {
                alert("Произошла ошибка при обращении к серверу (toggle_like).");
            }
        });
    });
})


$(document).ready(function () {
    console.log("jQuery работает, скрипт тоже работает, aeee");

    const MAX_TAGS = 5;
    let currentTags = [];

    $("#question-tags").on("input", function (e) {
        let inputText = $(this).val().trim();
        console.log("Введённый текст:", inputText);

        let parts = inputText.split(";").map(t => t.trim());
        let lastTag = parts.pop();

        if (currentTags.length >= MAX_TAGS) {
            alert(`⚠ Можно ввести максимум ${MAX_TAGS} тегов!`);
            $(this).val(currentTags.join("; ") + "; ");
            return;
        }

        if (lastTag.length > 0) {
            $.ajax({
                url: "/get_tags/",
                method: "GET",
                data: {term: lastTag},
                success: function (tags) {
                    if (!Array.isArray(tags)) {
                        console.warn("⚠ `tags` не является массивом:", tags);
                        return;
                    }
                    console.log("Найденные теги:", tags);
                    showTagSuggestions(tags, lastTag);
                },
                error: function (xhr, status, error) {
                    console.error("Ошибка AJAX-запроса:", error);
                }
            });
        } else {
            $("#tag-suggestions").empty().hide();
        }
    });

    function showTagSuggestions(tags, lastTag) {
        let suggestionsContainer = $("#tag-suggestions");
        suggestionsContainer.empty().show().css({
            "max-height": "200px",
            "overflow-y": "auto",
            "width": $("#question-tags").outerWidth() + "px",
        });

        if (tags.length === 0) {
            suggestionsContainer.hide();
            return;
        }

        tags.forEach(tag => {
            let tagElement = $("<div>")
                .addClass("tag-suggestion p-2 rounded")
                .text(tag)
                .on("click", function () {
                    addTag(tag);
                });
            suggestionsContainer.append(tagElement);
        });
    }

    function addTag(tag) {
        if (currentTags.length >= MAX_TAGS) {
            alert(`Можно ввести максимум ${MAX_TAGS} тегов!`);
            return;
        }

        if (!currentTags.includes(tag)) {
            currentTags.push(tag);
            $("#question-tags").val(currentTags.join("; ") + "; ");
            console.log("✅ Добавлен тег:", tag);
        }

        $("#tag-suggestions").empty().hide();
    }

    $("#question-tags").on("keypress", function (e) {
        if (e.key === ";") {
            e.preventDefault();
            let inputText = $(this).val().trim();
            let parts = inputText.split(";").map(t => t.trim());
            let lastTag = parts.pop();

            if (lastTag && !currentTags.includes(lastTag)) {
                addTag(lastTag);
            }
        }
    });
});

$(document).ready(function () {
    console.log("✅ Скрипт загружен!");

    $("#question-form").on("submit", function (e) {
        e.preventDefault();

        let title = $("#question-title").val().trim();
        let text = $("#question-text").val().trim();
        let tags = $("#question-tags").val().trim().split(";").map(t => t.trim()).filter(Boolean);

        if (tags.length > 5) {
            alert("Можно добавить не более 5 тегов!");
            return;
        }

        $.ajax({
            url: "/submit_question/",
            method: "POST",
            data: {
                title: title,
                text: text,
                tags: tags,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (response) {
                if (response.success) {
                    alert("Вопрос успешно добавлен!");
                    window.location.href = response.redirect_url;
                } else {
                    alert("Ошибка: " + response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Ошибка AJAX:", error);
                alert("Ошибка сервера, попробуйте позже.");
            }
        });
    });
});


