document.addEventListener("DOMContentLoaded", function () {
    // Handle navigation clicks
    document.querySelectorAll(".nav-btn").forEach(button => {
        button.addEventListener("click", function () {
            let target = this.getAttribute("data-target");
            let content = document.getElementById("dynamic-content");

            if (target === "sales" || target === "inventory") {
                fetch("/get_dashboard_data")
                    .then(response => response.json())
                    .then(data => {
                        if (target === "sales") {
                            content.innerHTML = `<h3>Sales Data</h3>${generateTable(data.sales)}`;
                        } else {
                            content.innerHTML = `<h3>Inventory Data</h3>${generateTable(data.inventory)}`;
                        }
                    });
            } else if (target === "new_sale") {
                content.innerHTML = `
                    <h3>New Sale</h3>
                    <form id="sale-form">
                        <label>Item:</label>
                        <input type="text" name="item" required>
                        <label>Quantity:</label>
                        <input type="number" name="quantity" required>
                        <button type="submit">Add Sale</button>
                    </form>
                `;
                document.getElementById("sale-form").addEventListener("submit", submitSale);
            } else if (target === "add_inventory") {
                content.innerHTML = `
                    <h3>Add Inventory</h3>
                    <form id="inventory-form">
                        <label>Item:</label>
                        <input type="text" name="item" required>
                        <label>Quantity:</label>
                        <input type="number" name="quantity" required>
                        <button type="submit">Add Item</button>
                    </form>
                `;
                document.getElementById("inventory-form").addEventListener("submit", submitInventory);
            }
        });
    });

    // Fetch & Load Pie Charts
    fetch("/get_dashboard_data")
        .then(response => response.json())
        .then(data => {
            new Chart(document.getElementById("salesChart"), {
                type: "pie",
                data: {
                    labels: data.sales.map(sale => sale.item),
                    datasets: [{
                        data: data.sales.map(sale => sale.quantity),
                        backgroundColor: ["red", "blue", "green"]
                    }]
                }
            });

            new Chart(document.getElementById("inventoryChart"), {
                type: "pie",
                data: {
                    labels: data.inventory.map(inv => inv.item),
                    datasets: [{
                        data: data.inventory.map(inv => inv.quantity),
                        backgroundColor: ["orange", "purple", "cyan"]
                    }]
                }
            });
        });
});

// Convert Data to Table
function generateTable(data) {
    let table = "<table border='1'><tr><th>Item</th><th>Quantity</th></tr>";
    data.forEach(row => {
        table += `<tr><td>${row.item}</td><td>${row.quantity}</td></tr>`;
    });
    table += "</table>";
    return table;
}

// Submit New Sale
function submitSale(event) {
    event.preventDefault();
    let formData = new FormData(event.target);

    fetch("/add_sale", {
        method: "POST",
        body: formData
    }).then(response => response.json())
      .then(data => alert(data.message));
}

// Submit New Inventory Item
function submitInventory(event) {
    event.preventDefault();
    let formData = new FormData(event.target);

    fetch("/add_inventory", {
        method: "POST",
        body: formData
    }).then(response => response.json())
      .then(data => alert(data.message));
}