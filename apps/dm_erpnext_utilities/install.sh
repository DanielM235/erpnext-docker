#!/bin/bash
#
# Install dm_erpnext_utilities app in ERPNext Docker container
#
set -e

CONTAINER_NAME="${1:-erpnext_backend}"
SITE_NAME="${2:-erpnext.example.com}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_NAME="dm_erpnext_utilities"

echo "======================================"
echo "Installing $APP_NAME app"
echo "======================================"
echo "Container: $CONTAINER_NAME"
echo "Site: $SITE_NAME"
echo "App directory: $SCRIPT_DIR"
echo ""

# Step 1: Force remove existing app from container
echo "🗑️  Step 1: Removing existing app from container..."
docker exec --user root "$CONTAINER_NAME" bash -c "
    rm -rf /home/frappe/frappe-bench/apps/$APP_NAME /tmp/$APP_NAME
" 2>/dev/null || true
echo "✅ Existing app removed"
echo ""

# Step 2: Copy app to container and set permissions
echo "📦 Step 2: Copying app to container..."
docker cp "$SCRIPT_DIR" "$CONTAINER_NAME:/home/frappe/frappe-bench/apps/$APP_NAME"
docker exec --user root "$CONTAINER_NAME" bash -c "
    chown -R frappe:frappe /home/frappe/frappe-bench/apps/$APP_NAME
    chmod -R 755 /home/frappe/frappe-bench/apps/$APP_NAME
"
echo "✅ App copied"
echo ""

# Step 3: Install Python package and register app
echo "🔧 Step 3: Installing Python package..."
docker exec --user frappe "$CONTAINER_NAME" bash -c "
    cd /home/frappe/frappe-bench
    ./env/bin/pip install -e ./apps/$APP_NAME
"
echo "✅ Python package installed"
echo ""

# Step 4: Add app to apps.txt (both bench and sites)
echo "📝 Step 4: Adding app to apps.txt files..."
docker exec --user frappe "$CONTAINER_NAME" bash -c "
    cd /home/frappe/frappe-bench
    
    # Add to bench apps.txt
    if ! grep -q \"^${APP_NAME}\$\" apps.txt 2>/dev/null; then
        echo \"${APP_NAME}\" >> apps.txt
        echo \"Added ${APP_NAME} to /home/frappe/frappe-bench/apps.txt\"
    fi
    
    # Add to sites apps.txt
    if ! grep -q \"^${APP_NAME}\$\" sites/apps.txt 2>/dev/null; then
        echo \"${APP_NAME}\" >> sites/apps.txt
        echo \"Added ${APP_NAME} to /home/frappe/frappe-bench/sites/apps.txt\"
    fi
    
    echo \"Bench apps.txt:\"
    cat apps.txt
    echo \"Sites apps.txt:\"
    cat sites/apps.txt
"
echo "✅ App added to apps.txt files"
echo ""

# Step 5: Install app on site
echo "🚀 Step 5: Installing app on site..."
docker exec --user frappe "$CONTAINER_NAME" bash -c "
    cd /home/frappe/frappe-bench
    bench --site $SITE_NAME install-app $APP_NAME
"
echo "✅ App installed on site"
echo ""

# Step 6: Verify installation
echo "🔍 Step 6: Verifying installation..."
docker exec --user frappe "$CONTAINER_NAME" bash -c "
    cd /home/frappe/frappe-bench
    bench --site $SITE_NAME list-apps
"
echo ""

echo "======================================"
echo "✅ Installation complete!"
echo "======================================"
echo ""
echo "Available commands:"
echo "  docker exec $CONTAINER_NAME bash -c 'cd /home/frappe/frappe-bench && bench --site $SITE_NAME delete-account-recursive \"ACCOUNT\" \"COMPANY\" --dry-run'"
echo "  docker exec $CONTAINER_NAME bash -c 'cd /home/frappe/frappe-bench && bench --site $SITE_NAME import-chart-of-accounts *.csv \"COMPANY\" --skip-root'"
echo ""
