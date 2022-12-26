function removeResChildren(parent) {
  while (parent.firstChild) {
    parent.firstChild.remove();
  }
}

// Darkmode Colors:
// text_color = "white";
// bg_color = "#121212";
// border_color = "#212529";
// hover_color = "rgba(255, 255, 255, 0.15)";
//
// Lightmode Colors:
// text_color = "black";
// bg_color = "white";
// border_color = "rgba(0, 0, 0, 0.125)";
// hover_color = "rgb(233, 236, 239)";

function registerMiniSearch(search_el, result_el, query_endpoint, colors) {
  const { text_color, bg_color, border_color, hover_color } = colors;
  search_el.addEventListener("input", (event) => {
    if (search_el.value.length == 0) {
      result_el.classList.add("d-none");
      search_el.style.borderBottomRightRadius = "0.375rem";
      search_el.style.borderBottomLeftRadius = "0.375rem";
      return false;
    }

    fetch(query_endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: search_el.value,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        search_el.style.borderBottomRightRadius = "0";
        search_el.style.borderBottomLeftRadius = "0";
        removeResChildren(result_el);
        data.results.map((result) => {
          const button = document.createElement("button");
          button.classList.add("list-group-item", "list-group-item-action");
          button.style.backgroundColor = bg_color;
          button.style.color = text_color;
          button.style.borderColor = border_color;
          button.textContent = result;
          button.type = "button";
          button.addEventListener("click", (event) => {
            let btnText = event.target.textContent;
            search_el.value = btnText;
            result_el.classList.add("d-none");
            search_el.style.borderBottomRightRadius = "0.375rem";
            search_el.style.borderBottomLeftRadius = "0.375rem";
          });
          button.addEventListener("mouseover", (_) => {
            button.style.backgroundColor = hover_color;
          });
          button.addEventListener("mouseout", (_) => {
            button.style.backgroundColor = bg_color;
          });
          result_el.appendChild(button);
        });
        result_el.classList.remove("d-none");
      })
      .catch((error) => console.log(error));
  });

  search_el.addEventListener("keydown", (event) => {
    if (event.key == "ArrowDown") {
      for (const child of result_el.children) {
        if (child.style.backgroundColor == hover_color) {
          if (!child.nextSibling) {
            return;
          }
          child.style.backgroundColor = bg_color;
          child.nextSibling.style.backgroundColor = hover_color;
          return;
        }
      }

      result_el.firstChild.style.backgroundColor = hover_color;
    }

    if (event.key == "ArrowUp") {
      for (const child of result_el.children) {
        if (child.style.backgroundColor == hover_color) {
          if (!child.previousSibling) {
            return;
          }
          child.style.backgroundColor = bg_color;
          child.previousSibling.style.backgroundColor = hover_color;
          return;
        }
      }

      result_el.children[result_el.children.length - 1].style.backgroundColor =
        hover_color;
    }

    if (event.key == "Enter") {
      for (const child of result_el.children) {
        if (child.style.backgroundColor == hover_color) {
          event.preventDefault();
          search_el.value = child.textContent;
          result_el.classList.add("d-none");
          search_el.style.borderBottomRightRadius = "0.375rem";
          search_el.style.borderBottomLeftRadius = "0.375rem";
        }
      }
    }
  });
}
