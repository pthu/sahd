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

function add_settings_menu() {
    var primary_nav = document.querySelector(".md-nav--primary > .md-nav__list");

    if (!primary_nav || document.getElementById("__nav_settings")) {
        return;
    }

    var item = document.createElement("li");
    item.className = "md-nav__item md-nav__item--nested";
    item.innerHTML = [
        '<input class="md-nav__toggle md-toggle" type="checkbox" id="__nav_settings">',
        '<label class="md-nav__link" for="__nav_settings" id="__nav_settings_label" tabindex="0">',
        '  <span class="md-ellipsis">Settings</span>',
        '  <span class="md-nav__icon md-icon"></span>',
        '</label>',
        '<nav class="md-nav" data-md-level="1" aria-labelledby="__nav_settings_label" aria-expanded="false">',
        '  <label class="md-nav__title" for="__nav_settings">',
        '    <span class="md-nav__icon md-icon"></span>',
        '    Settings',
        '  </label>',
        '  <ul class="md-nav__list" data-md-scrollfix>',
        '    <li class="md-nav__item">',
        '      <a href="#" class="md-nav__link" id="settings-theme-toggle">',
        '        <span class="md-ellipsis"></span>',
        '      </a>',
        '    </li>',
        '  </ul>',
        '</nav>'
    ].join("");

    primary_nav.appendChild(item);

    var toggle = document.getElementById("settings-theme-toggle");
    toggle.addEventListener("click", toggle_color_scheme);
    set_settings_theme_label(toggle);

    var observer = new MutationObserver(function() {
        set_settings_theme_label(toggle);
    });
    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ["data-md-color-scheme"]
    });
}

document.addEventListener("DOMContentLoaded", add_settings_menu);
