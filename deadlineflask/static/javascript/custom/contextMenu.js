document.addEventListener("DOMContentLoaded", function() {
    var jobsTable = document.getElementById('jobsTable');
    var contextMenu = document.getElementById('contextMenu');
    var editAction = document.getElementById('editAction');
    var deleteAction = document.getElementById('deleteAction');

    // Show context menu on right-click
    jobsTable.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        var x = e.clientX;
        var y = e.clientY;
        contextMenu.style.display = 'block';
        contextMenu.style.left = x + 'px';
        contextMenu.style.top = y + 'px';
    });

    // Hide context menu on click outside
    document.addEventListener('click', function(e) {
        if (!contextMenu.contains(e.target)) {
            contextMenu.style.display = 'none';
        }
    });

    // Define actions for context menu items
    editAction.addEventListener('click', function() {
        // Perform edit action
        alert('Edit action triggered');
        contextMenu.style.display = 'none';
    });

    deleteAction.addEventListener('click', function() {
        // Perform delete action
        alert('Delete action triggered');
        contextMenu.style.display = 'none';
    });
});