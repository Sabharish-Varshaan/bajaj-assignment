// 🔥 CHANGE ONLY THIS IF NEEDED
const API_URL = "https://sabharishvarshaans-bfhl-production.up.railway.app/bfhl";


async function sendRequest() {
    const input = document.getElementById("input").value;
    const statusDiv = document.getElementById("status");
    const resultDiv = document.getElementById("result");

    statusDiv.innerHTML = "";
    resultDiv.innerHTML = "";

    if (!input.trim()) {
        statusDiv.innerHTML = '<div class="error">Please enter some data.</div>';
        return;
    }

    let dataArray;

    try {
        const parsed = JSON.parse(input);
        if (parsed.data && Array.isArray(parsed.data)) {
            dataArray = parsed.data;
        } else {
            throw new Error();
        }
    } catch {
        dataArray = input.split(",").map(item => item.trim());
    }

    statusDiv.innerHTML = "Processing...";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ data: dataArray })
        });

        const result = await response.json();

        if (!response.ok) {
            statusDiv.innerHTML = `<div class="error">${result.detail}</div>`;
            return;
        }

        statusDiv.innerHTML = '<div class="success">Success</div>';

        let html = "";

        html += displayHierarchies(result.hierarchies);

        html += displaySummary(result.summary);

        if (result.invalid_entries.length > 0) {
            html += `
                <div class="card">
                    <h3>Invalid Entries</h3>
                    <p>${result.invalid_entries.join(", ")}</p>
                </div>
            `;
        }

        if (result.duplicate_edges.length > 0) {
            html += `
                <div class="card">
                    <h3>Duplicate Edges</h3>
                    <p>${result.duplicate_edges.join(", ")}</p>
                </div>
            `;
        }

        resultDiv.innerHTML = html;

    } catch {
        statusDiv.innerHTML = '<div class="error">Cannot connect to server</div>';
    }
}


function renderTree(node, tree, isRoot = false) {
    let html = `<li class="${isRoot ? 'root-node' : ''}">
        <span class="node">${node}</span>`;

    const children = Object.keys(tree || {});
    if (children.length > 0) {
        html += "<ul>";
        children.forEach(child => {
            html += renderTree(child, tree[child]);
        });
        html += "</ul>";
    }

    html += "</li>";
    return html;
}


function displayHierarchies(hierarchies) {
    let html = "";

    hierarchies.forEach(h => {
        html += `<div class="card">`;
        html += `<h3> Root: ${h.root}</h3>`;

        if (h.has_cycle) {
            html += `<p class="error">Cycle detected</p>`;
        } else {
            html += `<p>Depth: ${h.depth}</p>`;
            html += `<ul class="tree">${renderTree(h.root, h.tree[h.root], true)}</ul>`;
        }

        html += `</div>`;
    });

    return html;
}

function displaySummary(summary) {
    return `
        <div class="card">
            <h3>Summary</h3>
            <p>Total Trees: ${summary.total_trees}</p>
            <p>Total Cycles: ${summary.total_cycles}</p>
            <p>Largest Tree Root: ${summary.largest_tree_root}</p>
        </div>
    `;
}