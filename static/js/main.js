const updateBtn = document.getElementsByClassName("update-item");
const categories = document.querySelectorAll(".categories li");
const category__form = document.querySelector(".category__form");
const category__name = document.querySelector(".category__form input[type='hidden']");
const category__input = document.querySelectorAll(".category__form input[type='checkbox']");
console.log(categories)
categories.forEach((category, i) => {
  let url = window.location.href.split('?')[1]
  if (url === undefined) {
    categories[0].classList.add('active')
  } else {
    let cate = url.split('=')[1]
    let cate__name = category.dataset.category;
    if (cate__name === cate) {
      categories[i].classList.add("active");
    }
  }
});

category__input.forEach((input, i) => {
  // let input = form.querySelector("input[type='checkbox']");
  let active = input.dataset.active;
  if (active === 'True') {
    input.setAttribute('checked', true)
  }
  
  input.addEventListener('change', (e) => {
    category__name.value = e.target.dataset.name
    category__form.submit();
  })

});

document.addEventListener("click", (e) => {
  let isDropdownBtn = e.target.matches("[data-dropdown-btn]");

  if (!isDropdownBtn && e.target.closest("[data-dropdown]") !== null) return;

  let currentDropdown;
  if (isDropdownBtn) {
    currentDropdown = e.target.closest("[data-dropdown]");
    currentDropdown.classList.toggle("active");
  }

  document.querySelectorAll("[data-dropdown].active").forEach((dropdown) => {
    if (dropdown === currentDropdown) return;
    dropdown.classList.remove("active");
  });
});

for (let i = 0; i < updateBtn.length; i++) {
  updateBtn[i].addEventListener('click', e => {
    const itemId = e.target.dataset.item
    const action = e.target.dataset.action
    const type = e.target.dataset.type
    if (user === "AnonymousUser") {
      console.log('Not Loggin')
    } else {
      updateCartItem(itemId, action, type)
    }
  })
}

const updateCartItem = (itemId, action, type) => {
  console.log("ItemId: ", itemId, "Action: ", action, "Type: ", type);
  let url = "/update-cart/";

  const getData = async () => {
    let response = await fetch(url, {
      method: "POST",
      headers: {
        'Content-type': "application/json",
        "X-CSRFToken": csrftoken, 
      },
      body: JSON.stringify({"itemId": itemId, "action": action})
    })

    let data = await response.json()
     console.log(data);

    if (response.status === 200 && type === 'add') {
      document.querySelector(".messages").classList.add("active");
      document.querySelector(".messages li").innerText = "This item was added to your cart";
      if (document.querySelector(".store__wrapper") != null) {
        document.querySelector(".store__wrapper").classList.add('active');
      }
      setTimeout(() => {
        document.querySelector(".messages").classList.remove("active");
        location.reload()
        if (document.querySelector(".store__wrapper") != null) {
          document.querySelector(".store__wrapper").classList.remove('active');
        }
      }, 5000);
    } else if (response.status === 200) {
      location.reload()
    } 
  }

  getData()
};

