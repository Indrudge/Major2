$(document).ready(function () {
    // Fetch workspaces
    $.getJSON("/get_workspaces/", function (data) {
        let workspaces = data.workspaces;
        let container = $("#workspace-container");
        container.empty();
        
        workspaces.forEach(workspace => {
            let workspaceCard = `
                <div class="workspace-card" data-name="${workspace.name}">
                    <h3>${workspace.name}</h3>
                    <p>${workspace.address}</p>
                </div>
            `;
            container.append(workspaceCard);
        });

        // Handle workspace selection
        $(".workspace-card").click(function () {
            let selectedWorkspace = $(this).attr("data-name");
            $("#selected-workspace").text(selectedWorkspace);
            $("#menu-section").show();
            loadMenu(selectedWorkspace);
        });
    });

    // Fetch and display menu for the selected workspace
    function loadMenu(workspace) {
        $.getJSON(`/get_menu/${workspace}/`, function (data) {
            let dishes = data.menu;
            let container = $("#menu-container");
            container.empty();
            
            dishes.forEach(dish => {
                let dishCard = `
                    <div class="menu-card">
                        <img src="${dish.image}" alt="${dish.name}">
                        <h3>${dish.name}</h3>
                        <p>₹${dish.price}</p>
                        <button onclick="orderDish('${workspace}', '${dish.name}')">Order Now</button>
                    </div>
                `;
                container.append(dishCard);
            });
        });
    }

    // Order function: Deduct ingredients & add sale
    window.orderDish = function (workspace, dishName) {
        $.post("/order/", { workspace: workspace, dish: dishName }, function (response) {
            alert(response.message);
        });
    };
});