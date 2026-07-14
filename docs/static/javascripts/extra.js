function print_document() {
    document.getElementById("download").style.display = "none"
    window.print();
    document.getElementById("download").style.display = "block"
}

function show_modal(id) {
    var modal = document.getElementById("modal");
    modal.style.display = "block";
    var contents = document.getElementById(id).innerHTML;
    document.getElementById("modal-body").innerHTML = contents;

    // When the user clicks on (x), close the modal
    var span = document.getElementsByClassName("close")[0];
    span.onclick = function() {
      modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    }
}

function get_color_scheme() {
    return document.body.getAttribute("data-md-color-scheme") || "default";
}

function get_palette_input(scheme) {
    return document.querySelector('.md-option[data-md-color-scheme="' + scheme + '"]');
}

var settings_theme_observer = null;

function set_settings_theme_label(toggle) {
    var label = toggle.querySelector(".md-ellipsis");
    if (!label) {
        return;
    }

    var is_dark = get_color_scheme() == "slate";
    label.textContent = is_dark ? "Light mode" : "Dark mode";
    toggle.setAttribute("aria-label", is_dark ? "Switch to light mode" : "Switch to dark mode");
}

function toggle_color_scheme(event) {
    event.preventDefault();

    var target_scheme = get_color_scheme() == "slate" ? "default" : "slate";
    var target_input = get_palette_input(target_scheme);

    if (target_input) {
        target_input.click();
    }
}

function is_settings_theme_toggle(link) {
    var href = (link.getAttribute("href") || "").split("#")[0].split("?")[0];
    return /(^|\/)settings\/?$/.test(href) || /(^|\/)settings\.md$/.test(href);
}

function get_settings_theme_toggles() {
    var links = document.querySelectorAll(".md-nav a.md-nav__link");
    return Array.prototype.slice.call(links).filter(is_settings_theme_toggle);
}

function update_settings_theme_labels() {
    get_settings_theme_toggles().forEach(set_settings_theme_label);
}

function init_settings_theme_toggle() {
    var toggles = get_settings_theme_toggles();

    toggles.forEach(function(toggle) {
        if (toggle.dataset.settingsThemeToggle == "true") {
            return;
        }

        toggle.dataset.settingsThemeToggle = "true";
        toggle.addEventListener("click", toggle_color_scheme);
    });

    update_settings_theme_labels();

    if (settings_theme_observer) {
        return;
    }

    settings_theme_observer = new MutationObserver(update_settings_theme_labels);
    settings_theme_observer.observe(document.body, {
        attributes: true,
        attributeFilter: ["data-md-color-scheme"]
    });
}

document.addEventListener("DOMContentLoaded", init_settings_theme_toggle);

if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(init_settings_theme_toggle);
}
